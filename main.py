"""
Main entry point for the RAG API server
"""
import uvicorn
from presentation.api.app import create_app
from infrastructure.config.settings import get_settings
from core.logging_config import setup_logging


def main():
    """Start the API server"""
    # Setup logging
    setup_logging(log_level="INFO")

    # Get settings
    settings = get_settings()

    # Create FastAPI app
    app = create_app()

    # Run server
    # Note: reload is disabled in Docker as it requires app to be passed as import string
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()
