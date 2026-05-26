# rag_engine.py
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
        # IMPORTANT: Replace this with the model you actually used for training
        # (e.g., "Qwen/Qwen2.5-7B-Instruct")
        self.base_model_name = "unsloth/Qwen2.5-3B-Instruct-bnb-4bit" 
        
        self.max_seq_length = 2048
        # Ensure this uses the script's directory as the base
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
        from unsloth import FastLanguageModel
        print(f"Loading model with Unsloth optimization from: {self.local_dir}")
        
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.local_dir,
            max_seq_length=self.max_seq_length,
            dtype=None,
            load_in_4bit=True,
        )
        
        # Optimize model for inference (activates 2x inference speedup)
        FastLanguageModel.for_inference(self.model)
        
        print("Model loaded successfully.")

    def _setup_rag(self):
        # Make sure this path is correct
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'data', 'final_frensh_arabic_training_dataset.jsonl')
        
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
        
        # Ensure 'sentence-transformers' is installed
        embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
        self.vector_store = FAISS.from_documents(docs, embeddings)

    def generate_answer(self, question: str, max_new_tokens: int = 512):
        if self.vector_store is None:
            return "RAG not initialized."

        # 1. Retrieval
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})
        docs = retriever.invoke(question)

        # ❌ if no documents → stop immediately
        if not docs:
            return "Information not found in legal context."

        docs = docs[:4]

        context = "\n\nLEGAL CONTEXT:\n"
        context += "\n---\n".join([doc.page_content for doc in docs])

        # =========================
        # 🔥 DEBUG (VERY IMPORTANT)
        # =========================
        print("\n========== RETRIEVED CONTEXT ==========")
        print(context)
        print("=======================================\n")
        
        # 2. Prompting
        system_prompt = """You are a Moroccan legal assistant specialized ONLY in Moroccan law.

STRICT RULES:
- Answer ONLY questions related to Moroccan law and legal matters.
- If the question is not legal, refuse politely.
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
        
        # Tokenize & Generate
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer(
            [prompt],
            return_tensors="pt"
        ).to("cuda")
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, 
                max_new_tokens=max_new_tokens,
                do_sample=False,
                repetition_penalty=1.15,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
            
        # Decode only the generated tokens (slice off the input)
        generated_tokens = outputs[0][inputs['input_ids'].shape[-1]:]
        return self.tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()