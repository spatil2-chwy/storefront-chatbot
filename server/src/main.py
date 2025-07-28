from os import getenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from src.database import engine, Base
from src.routers.routes import router
from src.evaluation.logging_config import setup_logging
import logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

ENV = getenv("ENV", "dev").lower()

def create_app() -> FastAPI:
    app = FastAPI(title="Storefront Chatbot API", version="1.0.0")
    
    logger.info("Starting Storefront Chatbot API")

    Base.metadata.create_all(bind=engine)

    if ENV == "dev":
        logger.info("Running in development mode")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        # Redirect root to Vite dev server (optional)
        @app.get("/")
        def redirect_to_vite():
            return RedirectResponse("http://localhost:5173")

    elif ENV == "prod":
        logger.info("Running in production mode")
        # Mount assets directory to serve JS/CSS files
        app.mount("/assets", StaticFiles(directory="../dist/public/assets/"), name="assets")

    app.include_router(router)
    
    # Mount static files at root level for production (after API routes to avoid conflicts)
    if ENV == "prod":
        app.mount("/", StaticFiles(directory="../dist/public/", html=True), name="static")
    
    logger.info("Application initialized successfully")
    return app


app = create_app()