from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from pathlib import Path

app = FastAPI(title="Chewy Clone API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class User(BaseModel):
    id: int
    email: str
    name: str

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class Product(BaseModel):
    id: int
    name: str
    brand: str
    price: float
    originalPrice: Optional[float] = None
    image: str
    rating: float
    reviewCount: int
    category: str
    inStock: bool
    autoshipEligible: bool
    freeShipping: bool
    description: str

class ChatMessage(BaseModel):
    id: str
    content: str
    sender: str  # 'user' or 'ai'
    timestamp: str

# In-memory storage (replace with database in production)
users_db = {}
products_db = [
    {
        "id": 1,
        "name": "Blue Buffalo Life Protection Formula Adult Chicken & Brown Rice Recipe Dry Dog Food",
        "brand": "Blue Buffalo",
        "price": 54.98,
        "originalPrice": 64.99,
        "image": "/api/placeholder/300/300",
        "rating": 4.5,
        "reviewCount": 2847,
        "category": "Dog Food",
        "inStock": True,
        "autoshipEligible": True,
        "freeShipping": True,
        "description": "Made with real chicken, wholesome whole grains, garden veggies and fruit, BLUE Life Protection Formula is formulated to support the health and well-being of dogs."
    },
    {
        "id": 2,
        "name": "Hill's Science Diet Adult Perfect Weight Small & Mini Chicken Recipe Dry Dog Food",
        "brand": "Hill's Science Diet",
        "price": 43.99,
        "image": "/api/placeholder/300/300",
        "rating": 4.3,
        "reviewCount": 1256,
        "category": "Dog Food",
        "inStock": True,
        "autoshipEligible": True,
        "freeShipping": True,
        "description": "Clinically proven nutrition that transforms your dog's life. Precisely balanced nutrition that helps dogs maintain ideal weight."
    }
]

current_user_id = 1

# Routes
@app.get("/")
async def read_root():
    return {"message": "Chewy Clone API"}

@app.get("/api/user")
async def get_current_user():
    """Get current user (mock authentication)"""
    if current_user_id in users_db:
        return users_db[current_user_id]
    return {"id": 1, "email": "user@example.com", "name": "Test User"}

@app.post("/api/auth/login")
async def login(user_data: UserLogin):
    """Mock login endpoint"""
    # In production, verify password hash
    user = {
        "id": 1,
        "email": user_data.email,
        "name": "Test User"
    }
    users_db[1] = user
    return user

@app.post("/api/auth/logout")
async def logout():
    """Mock logout endpoint"""
    return {"message": "Logged out successfully"}

@app.get("/api/products")
async def get_products():
    """Get all products"""
    return products_db

@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    """Get specific product"""
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Serve static files from client dist (when built)
if Path("client/dist").exists():
    @app.mount("/assets", StaticFiles(directory="client/dist/assets"), name="assets")
    
    # Catch-all route for SPA
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the React SPA"""
        # Check if it's an API route
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Serve static files
        static_file_path = Path("client/dist") / full_path
        if static_file_path.exists() and static_file_path.is_file():
            return FileResponse(static_file_path)
        
        # Serve index.html for SPA routes
        return FileResponse("client/dist/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)