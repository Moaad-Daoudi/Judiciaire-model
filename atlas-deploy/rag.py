import torch
import os
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

class LegalRAGPipeline:
    def __init__(self):
        # We load the standard unquantized base model for CPU deployment
        self.base_model_name = "Qwen/Qwen2.5-3B-Instruct" 
        
        self.max_seq_length = 2048
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.local_dir = os.path.join(base_dir, 'models', 'lora')
        self.model = None
        self.tokenizer = None
        self.vector_store = None
        
        # 1. Setup Model
        self._load_model()
        # 2. Setup RAG
        self._setup_rag()

    def _load_model(self):
        print(f"Loading base model {self.base_model_name} on CPU...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
        
        # Load base model in float32 for CPU compatibility
        base_model = AutoModelForCausalLM.from_pretrained(
            self.base_model_name,
            torch_dtype=torch.float32,
            device_map="cpu"
        )
        
        print(f"Applying LoRA adapter from: {self.local_dir}")
        # Apply LoRA fine-tuning weights onto the base model
        self.model = PeftModel.from_pretrained(base_model, self.local_dir)
        print("Model loaded successfully on CPU.")

    def _setup_rag(self):
        local_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(local_dir, 'data', 'final_frensh_arabic_training_dataset.jsonl')
        
        if not os.path.exists(file_path):
            print(f"Warning: Data file not found at {file_path}")
            return

        documents = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line.strip())
                page_content = f"Question: {record.get('input', '')}\nRéponse: {record.get('output', '')}"
                documents.append(Document(page_content=page_content))
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.split_documents(documents)
        
        embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
        self.vector_store = FAISS.from_documents(docs, embeddings)

    def generate_answer(self, question: str, max_new_tokens: int = 512):
        if self.vector_store is None:
            return "RAG not initialized."

        retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
        docs = retriever.invoke(question)

        if not docs:
            return "Information not found in legal context."

        docs = docs[:4]

        context = "\n\nLEGAL CONTEXT:\n"
        context += "\n---\n".join([doc.page_content for doc in docs])

        print("\n========== RETRIEVED CONTEXT ==========")
        print(context)
        print("=======================================\n")
        
        system_prompt = """You are a Moroccan legal assistant specialized ONLY in Moroccan law.

            STRICT RULES FOR GREETINGS:
            - You are allowed to respond to basic polite greetings (like "hi", "hello", "مرحبا", "bonjour") naturally and politely in the same language the user used.
            - After greeting the user, politely ask them how you can assist them with Moroccan law.

            STRICT RULES FOR LEGAL ANSWERS:
            - Answer ONLY questions related to Moroccan law and legal matters.
            - If the user asks a non-legal question (after the initial greeting), refuse politely.
            - Do NOT invent laws, article numbers, or legal sources.
            - If the legal information is uncertain or missing from the context, say:
            "I do not have enough verified legal information to answer accurately."
            - Use ONLY the provided legal context when available.
            - If the answer is not present in the retrieved context, say so clearly.
            - Always answer in the same language as the user.
            - Keep answers concise, professional, and legally focused.
            - Mention the law/article ONLY if explicitly present in the context.
            - Never fabricate article numbers.
            - Your responses are for legal information only and do not replace a lawyer.
        """
        messages = [
            {"role": "system", "content": system_prompt + context},
            {"role": "user", "content": question}
        ]
        
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Removed .to("cuda") so it processes using the CPU
        inputs = self.tokenizer([prompt], return_tensors="pt").to("cpu")
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, 
                max_new_tokens=max_new_tokens,
                do_sample=False,
                repetition_penalty=1.15,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
            
        generated_tokens = outputs[0][inputs['input_ids'].shape[-1]:]
        return self.tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()