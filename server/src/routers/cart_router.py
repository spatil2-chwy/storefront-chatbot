# Cart router - handles cart operations
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import json
import logging

# Initialize logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cart", tags=["cart"])

# In-memory cart storage (in production, this would be in a database)
_carts: Dict[str, Dict] = {}

# Pydantic models for request/response
class AddToCartRequest(BaseModel):
    productId: int
    quantity: int = 1
    purchaseOption: str = 'buyonce'  # 'buyonce' or 'autoship'
    userId: Optional[int] = None

class CartItemResponse(BaseModel):
    id: str
    product: Dict[str, Any]
    quantity: int
    purchaseOption: str
    addedAt: str
    price: float

class CartResponse(BaseModel):
    id: str
    userId: Optional[int] = None
    items: List[CartItemResponse]
    totalItems: int
    totalPrice: float
    createdAt: str
    updatedAt: str

class UpdateCartItemRequest(BaseModel):
    quantity: int

# Helper function to get cart key
def get_cart_key(userId: Optional[int] = None) -> str:
    return f"user_{userId}" if userId else "anonymous"

# Helper function to calculate cart totals
def calculate_cart_totals(items: List[Dict]) -> tuple[int, float]:
    total_items = sum(item['quantity'] for item in items)
    total_price = sum(item['price'] * item['quantity'] for item in items)
    return total_items, total_price

@router.get("/", response_model=CartResponse)
async def get_cart(userId: Optional[int] = Query(None)):
    """Get user's cart"""
    cart_key = get_cart_key(userId)
    
    if cart_key not in _carts:
        # Initialize empty cart
        from datetime import datetime
        now = datetime.now().isoformat()
        _carts[cart_key] = {
            "id": cart_key,
            "userId": userId,
            "items": [],
            "totalItems": 0,
            "totalPrice": 0.0,
            "createdAt": now,
            "updatedAt": now
        }
    
    return _carts[cart_key]

@router.get("/{user_id}", response_model=CartResponse)
async def get_user_cart(user_id: int):
    """Get specific user's cart"""
    return await get_cart(user_id)

@router.post("/items", response_model=CartItemResponse)
async def add_to_cart(request: AddToCartRequest):
    """Add item to cart"""
    try:
        cart_key = get_cart_key(request.userId)
        
        # Get or create cart
        cart = await get_cart(request.userId)
        
        # Create cart item (in production, you'd fetch product data from database)
        from datetime import datetime
        item_id = f"item_{request.productId}_{request.purchaseOption}_{datetime.now().timestamp()}"
        
        # Mock product data (in production, fetch from product service)
        mock_product = {
            "id": request.productId,
            "title": f"Product {request.productId}",
            "brand": "Mock Brand",
            "price": 29.99,
            "autoshipPrice": 28.49 if request.purchaseOption == 'autoship' else None,
            "image": "/placeholder-product.jpg"
        }
        
        price = mock_product["autoshipPrice"] if request.purchaseOption == 'autoship' and mock_product["autoshipPrice"] else mock_product["price"]
        
        cart_item = {
            "id": item_id,
            "product": mock_product,
            "quantity": request.quantity,
            "purchaseOption": request.purchaseOption,
            "addedAt": datetime.now().isoformat(),
            "price": price
        }
        
        # Check if item already exists (same product and purchase option)
        existing_item_index = None
        for i, item in enumerate(cart["items"]):
            if (item["product"]["id"] == request.productId and 
                item["purchaseOption"] == request.purchaseOption):
                existing_item_index = i
                break
        
        if existing_item_index is not None:
            # Update existing item quantity
            cart["items"][existing_item_index]["quantity"] += request.quantity
            cart_item = cart["items"][existing_item_index]
        else:
            # Add new item
            cart["items"].append(cart_item)
        
        # Recalculate totals
        total_items, total_price = calculate_cart_totals(cart["items"])
        cart["totalItems"] = total_items
        cart["totalPrice"] = total_price
        cart["updatedAt"] = datetime.now().isoformat()
        
        _carts[cart_key] = cart
        
        logger.info(f"Added item to cart: {request.productId}, quantity: {request.quantity}")
        return cart_item
        
    except Exception as e:
        logger.error(f"Error adding item to cart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add item to cart: {str(e)}")

@router.put("/items/{item_id}", response_model=CartItemResponse)
async def update_cart_item(item_id: str, request: UpdateCartItemRequest, userId: Optional[int] = Query(None)):
    """Update cart item quantity"""
    try:
        cart = await get_cart(userId)
        cart_key = get_cart_key(userId)
        
        # Find the item
        item_index = None
        for i, item in enumerate(cart["items"]):
            if item["id"] == item_id:
                item_index = i
                break
        
        if item_index is None:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        if request.quantity <= 0:
            # Remove item if quantity is 0 or less
            removed_item = cart["items"].pop(item_index)
        else:
            # Update quantity
            cart["items"][item_index]["quantity"] = request.quantity
            removed_item = cart["items"][item_index]
        
        # Recalculate totals
        total_items, total_price = calculate_cart_totals(cart["items"])
        cart["totalItems"] = total_items
        cart["totalPrice"] = total_price
        
        from datetime import datetime
        cart["updatedAt"] = datetime.now().isoformat()
        _carts[cart_key] = cart
        
        return removed_item
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating cart item: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update cart item: {str(e)}")

@router.delete("/items/{item_id}")
async def remove_from_cart(item_id: str, userId: Optional[int] = Query(None)):
    """Remove item from cart"""
    try:
        cart = await get_cart(userId)
        cart_key = get_cart_key(userId)
        
        # Find and remove the item
        original_count = len(cart["items"])
        cart["items"] = [item for item in cart["items"] if item["id"] != item_id]
        
        if len(cart["items"]) == original_count:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        # Recalculate totals
        total_items, total_price = calculate_cart_totals(cart["items"])
        cart["totalItems"] = total_items
        cart["totalPrice"] = total_price
        
        from datetime import datetime
        cart["updatedAt"] = datetime.now().isoformat()
        _carts[cart_key] = cart
        
        return {"message": "Item removed from cart"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing item from cart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to remove item from cart: {str(e)}")

@router.post("/clear")
async def clear_cart(userId: Optional[int] = Query(None)):
    """Clear entire cart"""
    try:
        cart_key = get_cart_key(userId)
        
        if cart_key in _carts:
            from datetime import datetime
            _carts[cart_key]["items"] = []
            _carts[cart_key]["totalItems"] = 0
            _carts[cart_key]["totalPrice"] = 0.0
            _carts[cart_key]["updatedAt"] = datetime.now().isoformat()
        
        return {"message": "Cart cleared"}
        
    except Exception as e:
        logger.error(f"Error clearing cart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cart: {str(e)}")

@router.post("/{user_id}/clear")
async def clear_user_cart(user_id: int):
    """Clear specific user's cart"""
    return await clear_cart(user_id)

@router.post("/coupon")
async def apply_coupon(couponCode: str, userId: Optional[int] = Query(None)):
    """Apply coupon to cart (mock implementation)"""
    # Mock coupon functionality
    cart = await get_cart(userId)
    
    # Simple mock: 10% discount for "SAVE10"
    if couponCode.upper() == "SAVE10":
        discount = cart["totalPrice"] * 0.1
        cart["totalPrice"] = max(0, cart["totalPrice"] - discount)
        cart["appliedCoupon"] = {
            "code": couponCode,
            "discount": discount,
            "description": "10% off"
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid coupon code")
    
    return cart

@router.post("/shipping")
async def calculate_shipping(zipCode: str, userId: Optional[int] = Query(None)):
    """Calculate shipping cost (mock implementation)"""
    cart = await get_cart(userId)
    
    # Mock shipping calculation
    if cart["totalPrice"] >= 49:
        shipping_cost = 0
        delivery = "Free 1-3 day shipping"
    else:
        shipping_cost = 4.95
        delivery = "Standard shipping (5-7 days)"
    
    return {
        "shippingCost": shipping_cost,
        "estimatedDelivery": delivery
    }

@router.post("/checkout")
async def create_checkout_session(userId: Optional[int] = Query(None)):
    """Create checkout session (mock implementation)"""
    cart = await get_cart(userId)
    
    if not cart["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Mock checkout session
    from datetime import datetime
    session_id = f"checkout_{cart['id']}_{datetime.now().timestamp()}"
    
    return {
        "checkoutUrl": f"/checkout/{session_id}",
        "sessionId": session_id
    }
