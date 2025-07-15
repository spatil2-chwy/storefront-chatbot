from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import engine, Base
from src.routers.routes import router
from src.utils.logging_config import setup_logging
import logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)


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
    
    return app


app = create_app()