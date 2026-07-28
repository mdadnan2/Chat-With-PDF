from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers.upload import router as upload_router
from app.routers.chat import router as chat_router
from app.routers import auth

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api/v1")
app.include_router(chat_router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": f"Welcome to {settings.app_name}!"}
