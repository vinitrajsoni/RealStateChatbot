from fastapi import FastAPI
from pydantic import BaseModel
from modules.llm_csv_analyzer import ask_llm_about_csv
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Real Estate CSV Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def home():
    return {"message": "🏠 Real Estate Chatbot API running successfully!"}

@app.post("/chat")
def query_csv(request: QueryRequest):
    response = ask_llm_about_csv(request.query)
    print(response)
    return {
        "summary": response["summary"],
        "results": response["results"]
    }
