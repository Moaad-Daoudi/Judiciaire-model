# Juridical AI - Moroccan Legal Assistant

A RAG (Retrieval-Augmented Generation) system for Moroccan law using Qwen 2.5 and ChromaDB.

## Prerequisites
- Python 3.10+
- Node.js (for the frontend)
- NVIDIA GPU with CUDA drivers (for 4-bit model loading)

## Setup Backend
1. Go to the backend folder:
   `cd backend`
2. Create and activate a virtual environment:
   `python3 -m venv venv`
   `source venv/bin/activate`
3. Install dependencies:
   `pip install -r requirements.txt`
4. Download the AI models (this will create the `models/` folder):
   `python download_models.py`

## Setup Frontend
1. Go to the frontend folder:
   `cd ../frontend`
2. Install packages:
   `npm install`

## How to run
1. **Backend:**
   `cd backend`
   `source venv/bin/activate`
   `python main.py`
2. **Frontend:**
   `cd ../frontend`
   `npm run dev`

## Adding Data
- Place all legal PDF documents inside the `data/pdfs/` folder.
- The system will automatically ingest them into the vector database on the first run.