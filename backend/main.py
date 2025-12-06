from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import chatbot_api, recommendation_api

app = FastAPI(title="Chatbot + Film Öneri Sistemi")

# CORS Ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'lar
app.include_router(chatbot_api.router, prefix="/api", tags=["Chatbot"])
app.include_router(recommendation_api.router, prefix="/api", tags=["Recommendation"])

@app.get("/")
def home():
    return {"message": "API aktif! /api/chat ve /api/recommend kullanılabilir."}
