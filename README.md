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

Load the data from server:

```bash
python -m src.scripts.load_data
````

# Start FastAPI server
uvicorn src.main:app --reload --host localhost --port 8000
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
- **ChromaDB** - Vector database for semantic search
- **Sentence Transformers** - Text embeddings
- **CORS middleware** - Frontend integration
- **Automatic API docs** - Swagger/OpenAPI


## 🔌 API Endpoints

### Users
- `GET /api/users/{user_id}` - Get user by ID
- `GET /api/users/email/{email}` - Get user by email
- `POST /api/users` - Create new user

### Products
- `GET /api/products/search` - Search products using semantic search
- `GET /api/products/{product_id}` - Get product by ID

### Chat
- `GET /api/chat/messages` - Get all chat messages
- `POST /api/chat/messages` - Add new chat message
- `DELETE /api/chat/messages` - Clear all chat messages

### Health
- `GET /api/health` - Health check


# Product Comparison Feature

The comparison feature allows users to select up to 3 products and ask the AI to compare them based on various criteria like price, quality, ingredients, ratings, etc. The AI uses detailed product metadata to provide comprehensive comparisons.

## Architecture

### Backend Components

1. **`src/services/prompts.py`** - Contains the comparison prompt template
2. **`src/services/comparison_service.py`** - Handles comparison logic and OpenAI API calls
3. **`src/routers/chat_router.py`** - Contains the `/chats/compare` endpoint

### Frontend Components

1. **`client/src/components/ProductCard.tsx`** - Updated with compare checkboxes
2. **`client/src/components/ChatWidget.tsx`** - Updated to handle comparison mode
3. **`client/src/contexts/ChatContext.tsx`** - Added comparison state management
4. **`client/src/lib/api.ts`** - Added comparison API call


# Product Buffer System

The product buffer system manages the top 300 products retrieved from initial searches and enables efficient follow-up queries using the review synthesis collection.

## Architecture

### Collections
- **Products Collection**: Contains product metadata and embeddings for initial search
- **Review Synthesis Collection**: Contains review synthesis data and embeddings for follow-up re-ranking

### Buffer Management
- **Global Buffer**: Stores top 300 products from initial search
- **Context Tracking**: Maintains query and filter context for follow-up searches

## Workflow

### 1. Initial Search (`search_products`)
```
User Query → Product Collection → Top 300 Products → Buffer Storage → Display Top 30 + Follow-up Questions
```

### 2. Follow-up Search (`search_products_with_followup`)
```
User Follow-up → Review Collection → Re-rank Buffer Products → Update Buffer → Display Re-ranked Top 30 + New Follow-up Questions
```

## Key Functions

### Buffer Management
- `get_product_buffer()`: Retrieve current buffer
- `set_product_buffer(products, query, filters)`: Store products with context
- `clear_product_buffer()`: Clear buffer for new searches

### Search Functions
- `query_products()`: Initial search, stores results in buffer
- `query_products_with_followup()`: Re-ranks buffer using review collection

