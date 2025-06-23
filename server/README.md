# FastAPI Backend

This is the FastAPI backend for the storefront chatbot application, migrated from Express.js.

## Setup

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

### Option 1: Using uvicorn directly
```bash
uvicorn main:app --reload --host localhost --port 8000
```

### Option 2: Using the run script
```bash
python run.py
```

### Option 3: Using the main module
```bash
python -m main
```

## API Endpoints

The server will be available at `http://localhost:8000`

### API Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Available Endpoints

#### Users
- `GET /api/users/{user_id}` - Get user by ID
- `GET /api/users/email/{email}` - Get user by email
- `POST /api/users` - Create new user

#### Products
- `GET /api/products` - Get all products (with optional filtering)
- `GET /api/products/{product_id}` - Get product by ID

#### Chat
- `GET /api/chat/messages` - Get all chat messages
- `POST /api/chat/messages` - Add new chat message
- `DELETE /api/chat/messages` - Clear all chat messages

#### Health
- `GET /api/health` - Health check

## Features

- **In-memory storage** with dummy data for development
- **CORS enabled** for frontend integration
- **Request logging** similar to Express.js
- **Automatic API documentation** with Swagger/OpenAPI
- **Type safety** with Pydantic models
- **Async/await** support throughout

## Development

The backend uses in-memory storage with dummy data. In production, you would replace the `MemStorage` class with a real database implementation.

### Project Structure
```
backend/
├── main.py          # FastAPI application and middleware
├── routes.py        # API route definitions
├── storage.py       # In-memory data storage
├── schemas.py       # Pydantic models
├── requirements.txt # Python dependencies
├── run.py          # Development server script
└── README.md       # This file
``` 