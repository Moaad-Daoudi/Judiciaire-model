import os
import glob
import chromadb
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re

class LegalRAGPipeline:
    def __init__(self, db_path=None):
        # 1. Path Setup (Robust for backend folder structure)
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(backend_dir)
        
        self.model_path = os.path.join(backend_dir, "models", "lora")
        self.db_path = os.path.join(project_root, "vector_database")
        self.pdf_folder = os.path.join(project_root, "data", "pdfs")
        
        print(f"--- INIT ---")
        print(f"Model path: {self.model_path}")
        print(f"Database path: {self.db_path}")
        
        # 2. Vector Database
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(name="moroccan_legal_docs")
        self.embedding_model = SentenceTransformer("intfloat/multilingual-e5-base", device="cuda")
        
        # 3. Model Loading
        quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, local_files_only=True, fix_mistral_regex=True)
        self.llm_model = AutoModelForCausalLM.from_pretrained(
            self.model_path, 
            quantization_config=quantization_config, 
            device_map="auto",
            local_files_only=True
        )
        print("✅ Model loaded.")

    def ingest_pdfs(self):
        pdf_files = glob.glob(os.path.join(self.pdf_folder, "*.pdf"))
        print(f"Found {len(pdf_files)} PDFs.")
        
        # Keep legal articles together
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500, 
            chunk_overlap=250,
            separators=["\nARTICLE", "\nArticle", "\nSection", "\nChapitre", "\n"]
        )
        
        all_docs = []
        for pdf_file in pdf_files:
            source_name = os.path.basename(pdf_file)
            loader = PyMuPDFLoader(pdf_file)
            pages = loader.load()
            
            # Clean and "Bind" source name to text
            for page in pages:
                page.page_content = re.sub(r'^\d+\s*$', '', page.page_content, flags=re.MULTILINE)
                page.page_content = f"SOURCE DOCUMENT: {source_name}\n{page.page_content}"
            
            all_docs.extend(text_splitter.split_documents(pages))

        texts = [d.page_content for d in all_docs]
        metadatas = [{"source": os.path.basename(d.metadata['source'])} for d in all_docs]
        ids = [f"id_{i}" for i in range(len(texts))]
        
        # Embed
        formatted_texts = [f"passage: {t.strip()}" for t in texts]
        embeddings = self.embedding_model.encode(formatted_texts).tolist()
        
        self.collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
        print(f"✅ Successfully ingested {len(texts)} articles.")

    def generate_answer(self, query):
        # 1. Retrieve
        results = self.collection.query(
            query_embeddings=self.embedding_model.encode([f"query: {query}"]).tolist(), 
            n_results=2, include=["documents", "metadatas"]
        )
        
        context_list = []
        for i in range(len(results['documents'][0])):
            doc = results['documents'][0][i]
            filename = results['metadatas'][0][i].get('source', 'Unknown')
            context_list.append(f"SOURCE: {filename}\nCONTENT: {doc}")
        
        context = "\n\n".join(context_list)
        
        # 2. STRUCTURED PROMPT
        # We define a strict output template
        system_prompt = (
            "You are a professional Moroccan legal assistant. "
            "You MUST use ONLY the CONTEXT to answer. "
            "Follow this template strictly for your response:\n\n"
            "ANSWER:\n[Direct, one-sentence answer]\n\n"
            "EXPLANATION:\n[Brief explanation based on the context, citing specific Article numbers if present]\n\n"
            "SOURCE:\n- [Source File Name]\n\n"
            "If the answer is not in the context, output only: 'I cannot find the answer in the provided documents'."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION:\n{query}"}
        ]
        
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        
        # 3. Generate with low temperature
        outputs = self.llm_model.generate(
            **inputs, 
            max_new_tokens=512, 
            do_sample=False, 
            repetition_penalty=1.2
        )
        
        response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[-1]:], skip_special_tokens=True)
        return response