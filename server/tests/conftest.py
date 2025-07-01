"""
Common test fixtures and configuration.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import chromadb

@pytest.fixture
def db_session() -> Session:
    """
    Creates an in-memory SQLite database session for testing.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Import all models and create tables
    from src.models.user import User
    from src.models.pet import PetProfile
    from src.models.chat import ChatMessage
    
    # Create all tables
    User.metadata.create_all(bind=engine)
    PetProfile.metadata.create_all(bind=engine)
    ChatMessage.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def mock_chroma_client(mocker):
    """
    Creates a mock ChromaDB client for testing.
    """
    # Create a mock client with all necessary methods
    mock_client = mocker.MagicMock()
    
    # Create a mock collection
    mock_collection = mocker.MagicMock()
    mock_collection.get.return_value = {
        "metadatas": [{
            "PRODUCT_ID": "123",
            "CLEAN_NAME": "Test Product",
            "PURCHASE_BRAND": "Test Brand",
            "PRICE": "29.99",
            "AUTOSHIP_PRICE": "25.99",
            "RATING_AVG": "4.5",
            "RATING_CNT": "100",
            "DESCRIPTION_LONG": "Test product description",
            "CATEGORY_LEVEL1": "Test Category",
            "FULLIMAGE": ["image1.jpg", "image2.jpg"],
            "THUMBNAIL": "thumbnail.jpg",
            "specialdiettag:grain-free": True,
            "ingredienttag:chicken": True,
            "review_synthesis": '{"what_customers_love": ["Great quality"], "what_to_watch_out_for": ["Size runs small"], "should_you_buy_it": "Yes"}'
        }]
    }
    
    # Set up the get_collection method
    mock_client.get_collection = mocker.MagicMock(return_value=mock_collection)
    
    return mock_client

@pytest.fixture
def mock_openai_client(mocker):
    """
    Creates a mock OpenAI client for testing.
    """
    mock_client = mocker.MagicMock()
    mock_completion = mocker.MagicMock()
    mock_completion.choices = [mocker.MagicMock(message=mocker.MagicMock(content="Test response"))]
    mock_client.chat.completions.create.return_value = mock_completion
    return mock_client 