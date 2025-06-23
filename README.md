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

### Key Changes
- ✅ **Monorepo structure** - Clean separation between frontend and backend
- ✅ **Frontend config in client/** - All frontend configuration files moved to client directory
- ✅ **Type definitions** - TypeScript types defined in `client/src/types/`
- ✅ **No shared folder** - Removed shared folder since backend is Python
- ✅ **Independent package management** - Frontend and backend have separate dependency management

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
- Product details with images and pricing

### User Experience
- Modern, responsive UI with Tailwind CSS
- Smooth animations and transitions
- Intuitive chat interface
- Authentication system

## 🛠️ Development

### Frontend Development
```bash
cd client
npm run dev          # Start development server
npm run build        # Build for production
npm run check        # TypeScript type checking
```

### Backend Development
```bash
cd server
source venv/bin/activate
uvicorn main:app --reload --host localhost --port 8000
```

### Running Both Services
```bash
# Terminal 1 - Frontend
cd client && npm run dev

# Terminal 2 - Backend
cd server && source venv/bin/activate && uvicorn main:app --reload
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
The built files will be in `../dist/public/`

### Backend Production
```bash
cd server
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📁 File Organization

### Frontend (`client/`)
- **Configuration files** - All config files (vite, tailwind, typescript, etc.) are in the client root
- **Source code** - React components, pages, and utilities in `src/`
- **Types** - TypeScript interfaces in `src/types/`
- **Static assets** - Images and public files in `public/`

### Backend (`server/`)
- **FastAPI app** - Main application logic
- **API routes** - Endpoint definitions
- **Data models** - Pydantic schemas
- **Storage** - In-memory data management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both frontend and backend
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details
