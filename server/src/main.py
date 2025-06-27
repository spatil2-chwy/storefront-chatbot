from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import engine, Base
from src.routers.routes import router
from src.services.searchengine import warmup
import asyncio
import threading


def create_app() -> FastAPI:
    app = FastAPI(title="Storefront Chatbot API", version="1.0.0")

    Base.metadata.create_all(bind=engine)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    
    # Warm up the search engine in a background thread to avoid blocking startup
    def warmup_thread():
        try:
            warmup()
        except Exception as e:
            print(f"Error during warmup: {e}")
    
    threading.Thread(target=warmup_thread, daemon=True).start()
    
    return app


app = create_app()