from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import traceback
from rag import LegalRAGPipeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global pipeline
try:
    print("Loading AI Brain... this may take a minute.")
    bot = LegalRAGPipeline()
    if bot.collection.count() == 0:
        bot.ingest_pdfs() 
    print("AI is ready!")
except Exception as e:
    print("CRITICAL ERROR LOADING MODEL:")
    print(traceback.format_exc())
    bot = None

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if bot is None:
        raise HTTPException(status_code=500, detail="AI Model failed to load.")
    
    try:
        user_query = request.message
        # Simple logging to see the query in terminal
        print(f"User asked: {user_query}")
        
        answer = bot.generate_answer(user_query)
        return {"reply": answer}
    except Exception as e:
        print("ERROR DURING GENERATION:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)