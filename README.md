# 🛍️ Storefront Chatbot

A modern e-commerce chatbot application with intelligent product search, comparison features, and personalized recommendations. Built with React frontend and FastAPI backend.

## 🏗️ Project Structure

```
storefront-chatbot/
├── 🖥️  client/                    # React frontend application
│   ├── src/
│   │   ├── components/           # Reusable UI components
│   │   ├── pages/               # Page components (routing)
│   │   ├── contexts/            # React contexts (state management)
│   │   ├── hooks/               # Custom React hooks
│   │   ├── lib/                 # Utilities and API clients
│   │   └── types/               # TypeScript type definitions
│   └── public/                  # Static assets
│
├── 🖧  server/                     # FastAPI backend application
│   └── src/
│       ├── models/              # SQLAlchemy database models
│       ├── routers/             # API route handlers
│       ├── services/            # Business logic services
│       │   ├── database/        # Database/CRUD services
│       │   ├── search/          # Search and AI services
│       │   ├── chat-modes/      # Chat feature modes
│       │   └── prompts/         # Prompt templates
│       ├── database.py          # Database configuration
│       ├── schemas.py           # Pydantic schemas
│       └── main.py              # FastAPI application entry point
│
└── 📁 scripts/                    # Data processing and setup scripts
    ├── chromadb-builders/       # ChromaDB vector database builders
    ├── data-loaders/            # Data loading and setup scripts
    ├── data/                    # Large datasets and files
    └── databases/               # Vector databases and cache files
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm (for frontend)
- **Python** 3.10+ (for backend)
- **Git** for version control

### 1️⃣ Setup Backend
```bash
cd storefront-chatbot/server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ Setup Frontend
```bash
cd storefront-chatbot/client
npm install
```

### 3️⃣ Initialize Databases
```bash
cd storefront-chatbot/scripts/chromadb-builders
python productdbbuilder.py
python review_synthesis_dbbuilder.py

cd ../data-loaders
python load_data.py
```

### 4️⃣ Run the Application
```bash
# Terminal 1: Start backend server
cd storefront-chatbot/server/src
python main.py

# Terminal 2: Start frontend dev server
cd storefront-chatbot/client
npm run dev
```

🎉 **Access the application at `http://localhost:5173`**

## 🔧 Key Features

### 🤖 AI-Powered Chat
- **Intelligent Product Search**: Semantic search across product catalogs
- **Product Comparison**: Side-by-side product comparisons with AI insights
- **Q&A Mode**: Ask specific questions about products

### 👤 User Management  
- **User Authentication**: Secure login/logout functionality
- **Pet Profiles**: Manage pet information for personalized recommendations
- **Order History**: Track previous purchases and preferences

### 🛍️ Product Discovery
- **Advanced Filtering**: Filter by brand, category, price, and more
- **Search Analytics**: Understanding user search patterns
- **Recommendation Engine**: AI-powered product suggestions

## 📊 Services Architecture

### Database Services (`server/src/services/database/`)
- **ProductService**: Product catalog management and retrieval
- **UserService**: User authentication and profile management  
- **PetService**: Pet profile management
- **ChatService**: Chat history and message persistence

### Search Services (`server/src/services/search/`)
- **SearchEngine**: Vector-based semantic product search
- **ChatbotLogic**: AI conversation handling and context management
- **SearchAnalyzer**: Search pattern analysis and optimization

### Chat Features (`server/src/services/chat-modes/`)
- **ProductComparison**: Side-by-side product comparison logic
- **ProductQA**: Question-answering about specific products

### Configuration (`server/src/services/prompts/`)
- **Prompt Templates**: AI prompt engineering and templates

## 📚 Data Management

### ChromaDB Builders (`scripts/chromadb-builders/`)
- **ProductDBBuilder**: Builds vector embeddings for products
- **ReviewSynthesisBuilder**: Processes and embeds product reviews
- **ArticleDBBuilder**: Creates knowledge base from articles

### Data Loaders (`scripts/data-loaders/`)
- **load_data.py**: Loads user and pet data into SQL database
- **generate_credentials.py**: Creates user authentication credentials
- **assign_pets.py**: Associates pets with user accounts

## 🛠️ Development

### Adding New Features
1. **Backend**: Add new services in appropriate `services/` subdirectory
2. **Frontend**: Create components in `client/src/components/`
3. **Database**: Add models in `server/src/models/`
4. **API**: Add routes in `server/src/routers/`

### Environment Configuration
Create `.env` file in `server/` directory:
```env
OPENAI_API_KEY_2=your_openai_api_key
DATABASE_URL=sqlite:///./storefront.db
```

### Database Migrations
```bash
cd storefront-chatbot/scripts/data-loaders
python load_data.py  # Recreates tables and loads fresh data
```

## 🧪 Testing

### Running Backend Tests
```bash
# From the server directory
cd storefront-chatbot/server
pytest tests/

# Run with coverage report
pytest --cov=src tests/

# Run specific test file
pytest tests/services/test_search_queries.py
```

### Test Structure
The test suite is organized by service:

#### Search Services Tests
- **test_search_queries.py**: Tests basic product searches, dietary restrictions, categories, and brand-specific searches
- **test_search_analyzer.py**: Tests matching search terms with product details (brands, categories, ingredients)
- **test_searchengine.py**: Tests product ranking and search result sorting

#### Prompt Services Tests
- **test_prompts.py**: Tests generating AI prompts for product details, comparisons, and Q&A

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes following the project structure
4. Test your changes thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using React, FastAPI, ChromaDB, and OpenAI**

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

