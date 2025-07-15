from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import engine, Base
from src.routers.routes import router
from src.evaluation.logging_config import setup_logging
import logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title="Storefront Chatbot API", version="1.0.0")
    
    logger.info("Starting Storefront Chatbot API")

    Base.metadata.create_all(bind=engine)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    
    logger.info("Application initialized successfully")
    return app


app = create_app()