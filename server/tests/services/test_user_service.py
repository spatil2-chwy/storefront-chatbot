"""
Tests for the UserService class.
"""
import pytest
from datetime import date
from src.models.user import User
from src.models.pet import PetProfile
from src.services.database.user_service import UserService

@pytest.fixture
def user_service():
    """Creates a UserService instance for testing."""
    return UserService()

@pytest.fixture
def sample_user():
    """Creates a sample user for testing."""
    return User(
        customer_key=1,
        customer_id="TEST001",
        name="Test User",
        email="test@example.com",
        password="test_password",
        customer_address_city="Test City",
        customer_address_state="TS",
        customer_address_zip="12345"
    )

@pytest.fixture
def sample_pet():
    """Creates a sample pet for testing."""
    return PetProfile(
        pet_profile_id=1,
        customer_id="TEST001",
        pet_name="TestPet",
        pet_type="Dog",
        pet_breed="TestBreed",
        pet_breed_size_type="Medium",
        weight=20.5,
        life_stage="Adult",
        gender="Male",
        birthday=date(2020, 1, 1),
        allergy_count=1,
        pet_new=True,
        status="Active",
        time_created=date(2020, 1, 1),
        time_updated=date(2020, 1, 1)
    )

def test_create_user(user_service, db_session, sample_user):
    """Test creating a new user."""
    created_user = user_service.create_user(db_session, sample_user)
    assert created_user.customer_key == sample_user.customer_key
    assert created_user.name == sample_user.name
    assert created_user.email == sample_user.email
    assert created_user.password == sample_user.password

def test_get_user(user_service, db_session, sample_user):
    """Test retrieving a user by customer key."""
    db_session.add(sample_user)
    db_session.commit()
    
    user = user_service.get_user(db_session, sample_user.customer_key)
    assert user is not None
    assert user.customer_key == sample_user.customer_key
    assert user.email == sample_user.email
    assert user.password == sample_user.password

def test_get_nonexistent_user(user_service, db_session):
    """Test retrieving a non-existent user."""
    user = user_service.get_user(db_session, 999)
    assert user is None

def test_update_user(user_service, db_session, sample_user):
    """Test updating a user's information."""
    db_session.add(sample_user)
    db_session.commit()
    
    updated_data = User(
        customer_key=sample_user.customer_key,
        customer_id="TEST001",
        name="Updated Name",
        email="updated@example.com",
        password="updated_password"
    )
    
    updated_user = user_service.update_user(db_session, sample_user.customer_key, updated_data)
    assert updated_user is not None
    assert updated_user.name == "Updated Name"
    assert updated_user.email == "updated@example.com"
    assert updated_user.password == "updated_password"

def test_delete_user(user_service, db_session, sample_user):
    """Test deleting a user."""
    db_session.add(sample_user)
    db_session.commit()
    
    result = user_service.delete_user(db_session, sample_user.customer_key)
    assert result is True
    
    deleted_user = user_service.get_user(db_session, sample_user.customer_key)
    assert deleted_user is None

def test_get_pets_by_user(user_service, db_session, sample_user, sample_pet):
    """Test retrieving pets associated with a user."""
    db_session.add(sample_user)
    db_session.add(sample_pet)
    db_session.commit()
    
    pets = user_service.get_pets_by_user(db_session, sample_user.customer_key)
    assert len(pets) == 1
    assert pets[0].pet_name == sample_pet.pet_name
    assert pets[0].customer_id == sample_pet.customer_id

def test_get_user_context_for_chat(user_service, db_session, sample_user, sample_pet):
    """Test getting formatted user context for chat."""
    db_session.add(sample_user)
    db_session.add(sample_pet)
    db_session.commit()
    
    context = user_service.get_user_context_for_chat(db_session, sample_user.customer_key)
    assert context is not None
    assert context["user_id"] == sample_user.customer_key
    assert context["name"] == sample_user.name
    assert len(context["pets"]) == 1
    
    pet_info = context["pets"][0]
    assert pet_info["name"] == sample_pet.pet_name
    assert pet_info["type"] == sample_pet.pet_type
    assert pet_info["breed"] == sample_pet.pet_breed
    assert pet_info["weight"] == sample_pet.weight
    assert pet_info["allergies"] is True
    assert pet_info["is_new"] is True

def test_format_pet_context_for_ai(user_service):
    """Test formatting pet context for AI."""
    user_context = {
        "name": "Test User",
        "location": {"city": "Test City", "state": "TS"},
        "pets": [{
            "name": "TestPet",
            "type": "Dog",
            "breed": "TestBreed",
            "size": "Medium",
            "weight": 20.5,
            "life_stage": "Adult",
            "age_months": 24,
            "allergies": True,
            "is_new": True
        }]
    }
    
    formatted = user_service.format_pet_context_for_ai(user_context)
    assert "Test User" in formatted
    assert "Test City, TS" in formatted
    assert "TestPet" in formatted
    assert "TestBreed Dog" in formatted
    assert "2 years old" in formatted
    assert "Has allergies" in formatted 