"""
Tests for the ChatService class.
"""
import pytest
from datetime import datetime
from src.services.database.chat_service import ChatService
from src.models.chat import ChatMessage
from src.models.constants import SenderType

@pytest.fixture
def chat_service():
    """Creates a ChatService instance for testing."""
    return ChatService()

@pytest.fixture
def sample_message():
    """Creates a sample chat message for testing."""
    return ChatMessage(
        id="test-message-1",
        content="Test message content",
        sender=SenderType.USER,
        timestamp=datetime.now()
    )

def test_create_message(chat_service, db_session, sample_message):
    """Test creating a new chat message."""
    created_message = chat_service.create_message(db_session, sample_message)
    
    assert created_message.id == sample_message.id
    assert created_message.content == sample_message.content
    assert created_message.sender == sample_message.sender
    assert created_message.timestamp is not None

def test_get_message(chat_service, db_session, sample_message):
    """Test retrieving a chat message by ID."""
    # Add message to database
    db_session.add(sample_message)
    db_session.commit()
    
    # Test retrieval
    message = chat_service.get_message(db_session, sample_message.id)
    assert message is not None
    assert message.id == sample_message.id
    assert message.content == sample_message.content
    assert message.sender == sample_message.sender

def test_get_nonexistent_message(chat_service, db_session):
    """Test retrieving a non-existent message."""
    message = chat_service.get_message(db_session, "nonexistent-id")
    assert message is None 