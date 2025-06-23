#!/usr/bin/env python3
"""
Simple test script to verify the FastAPI backend works
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_storage():
    """Test the storage functionality"""
    try:
        from storage import storage
        from schemas import UserCreate, ChatMessageCreate, SenderType
        
        print("✅ Storage module imported successfully")
        
        # Test user creation
        user_data = UserCreate(email="test@example.com", name="Test User")
        user = await storage.create_user(user_data)
        print(f"✅ User created: {user.name} ({user.email})")
        
        # Test product retrieval
        products = await storage.get_products()
        print(f"✅ Found {len(products)} products")
        
        # Test chat messages
        messages = await storage.get_chat_messages()
        print(f"✅ Found {len(messages)} chat messages")
        
        # Test adding a new message
        new_message = ChatMessageCreate(
            content="Hello from test!",
            sender=SenderType.USER
        )
        message = await storage.add_chat_message(new_message)
        print(f"✅ Added new message: {message.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing storage: {e}")
        return False

async def test_schemas():
    """Test the Pydantic schemas"""
    try:
        from schemas import User, Product, ChatMessage, SenderType
        
        print("✅ Schemas imported successfully")
        
        # Test user schema
        user = User(id=1, email="test@example.com", name="Test User")
        print(f"✅ User schema works: {user.name}")
        
        # Test chat message schema
        message = ChatMessage(
            id="test-123",
            content="Test message",
            sender=SenderType.AI,
            timestamp=asyncio.get_event_loop().time()
        )
        print(f"✅ Chat message schema works: {message.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing schemas: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing FastAPI Backend Components...")
    print("=" * 50)
    
    # Test schemas
    schemas_ok = await test_schemas()
    
    # Test storage
    storage_ok = await test_storage()
    
    print("=" * 50)
    if schemas_ok and storage_ok:
        print("✅ All tests passed! Backend is ready to run.")
        print("\nTo start the server, run:")
        print("  uvicorn main:app --reload --host localhost --port 8000")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 