from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import auth, history, chat

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI 智慧学习系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(history.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"message": "AI 智慧学习系统 API"}
