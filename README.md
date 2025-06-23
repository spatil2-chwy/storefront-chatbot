# Storefront Chatbot

A modern e-commerce chatbot application with a React frontend and FastAPI backend. Features AI-powered product recommendations and live agent support.

## 🚀 Quick Start

### Prerequisites
- Node.js (v18 or higher) - for frontend
- Python (v3.8 or higher) - for backend
- npm or yarn

### Frontend (React/Vite)
```bash
# Navigate to client directory
cd client

# Install dependencies
npm install

# Start development server
npm run dev
```
The frontend will be available at `http://localhost:5173`

### Backend (FastAPI)
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn main:app --reload --host localhost --port 8000
```
The backend will be available at `http://localhost:8000`

### API Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🏗️ Project Structure

```
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Page components
│   │   └── main.tsx       # Entry point
│   └── index.html         # HTML template
├── backend/                # FastAPI backend
│   ├── main.py            # FastAPI application
│   ├── routes.py          # API routes
│   ├── storage.py         # In-memory data storage
│   ├── schemas.py         # Pydantic models
│   ├── requirements.txt   # Python dependencies
│   └── run.py             # Development server script
├── shared/                # Shared types (legacy)
└── server/                # Legacy Express backend (can be removed)
```

## 🔧 Backend Architecture

### Current Stack: FastAPI (Python)
The backend is built with:
- **FastAPI** - Modern, fast web framework
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server
- **In-memory storage** - Dummy data for development
- **CORS middleware** - Frontend integration
- **Automatic API docs** - Swagger/OpenAPI

### Migration from Express.js
This project was migrated from Express.js to FastAPI. The migration included:
- ✅ API routes converted to FastAPI endpoints
- ✅ TypeScript types converted to Pydantic models
- ✅ Express middleware converted to FastAPI middleware
- ✅ Request/response logging maintained
- ✅ CORS configuration preserved
- ✅ Dummy data storage implemented

## 🎯 Key Features

### Chat Widget
- AI-powered product recommendations
- Live agent support toggle
- Real-time messaging
- Product filtering based on chat content

### Product Management
- Dynamic product catalog
- Search and filtering
- Category-based navigation

### User Experience
- Modern, responsive UI
- Smooth animations
- Intuitive chat interface

## 🛠️ Development

### Frontend Development
```bash
cd client
npm run dev
```

### Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### Type Checking
```bash
# Frontend TypeScript
cd client
npm run check

# Backend (FastAPI handles type validation automatically)
```

## 🔌 API Endpoints

### Users
- `GET /api/users/{user_id}` - Get user by ID
- `GET /api/users/email/{email}` - Get user by email
- `POST /api/users` - Create new user

### Products
- `GET /api/products` - Get all products (with optional filtering)
- `GET /api/products/{product_id}` - Get product by ID

### Chat
- `GET /api/chat/messages` - Get all chat messages
- `POST /api/chat/messages` - Add new chat message
- `DELETE /api/chat/messages` - Clear all chat messages

### Health
- `GET /api/health` - Health check

## 🚀 Deployment

### Frontend Production Build
```bash
cd client
npm run build
```

### Backend Production
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both frontend and backend
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details
