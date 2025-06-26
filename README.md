# Storefront Chatbot

Chewy chatbot application with a React frontend and FastAPI backend. Features AI-powered product recommendations and live agent support.

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
# Navigate to server directory
cd server

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
├── client/                # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── lib/           # Utilities and hooks
│   │   ├── types/         # TypeScript type definitions
│   │   └── main.tsx       # Entry point
│   ├── public/            # Static assets
│   ├── package.json       # Frontend dependencies
│   ├── vite.config.ts     # Vite configuration
│   ├── tailwind.config.ts # Tailwind CSS configuration
│   ├── tsconfig.json      # TypeScript configuration
│   ├── postcss.config.js  # PostCSS configuration
│   ├── components.json    # shadcn/ui configuration
│   └── index.html         # HTML template
├── server/                # FastAPI backend
│   ├── main.py            # FastAPI application
│   ├── routes.py          # API routes
│   ├── storage.py         # In-memory data storage
│   ├── schemas.py         # Pydantic models
│   └── requirements.txt   # Python dependencies
├── dist/                  # Production build output
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🔧 Architecture

### Frontend Stack
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling framework
- **shadcn/ui** - Component library
- **Wouter** - Client-side routing
- **React Query** - Data fetching
- **Zod** - Schema validation

### Backend Stack
- **FastAPI** - Modern, fast web framework
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server
- **In-memory storage** - Dummy data for development
- **CORS middleware** - Frontend integration
- **Automatic API docs** - Swagger/OpenAPI


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

Load the data from server:

```bash
python -m src.scripts.load_data
````