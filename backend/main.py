# Docker/backend/backend/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health") #Fast API의 상태를 확인하는
async def health_check():
    return {"status": "ok"}
