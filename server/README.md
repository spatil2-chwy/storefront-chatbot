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

```bash
uvicorn main:app --reload --host localhost --port 8000
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
- `POST /api/chat/messages` Clear all chat messages
 - Add new chat message
- `DELETE /api/chat/messages` -
#### Health
- `GET /api/health` - Health check

## Features

- **In-memory storage** with dummy data for development
- **CORS enabled** for frontend integration
- **Automatic API documentation** with Swagger/OpenAPI
- **Type safety** with Pydantic models
- **Async/await** support throughout


### Project Structure
```
server/
├── main.py          # FastAPI application and middleware
├── routes.py        # API route definitions
├── storage.py       # In-memory data storage
├── schemas.py       # Pydantic models
├── requirements.txt # Python dependencies
└── README.md        # This file
``` 