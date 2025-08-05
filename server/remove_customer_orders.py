#!/usr/bin/env python3
"""
Script to remove all orders for a specific customer from the database.
This script will delete all orders and their associated order items for Kathleen Simpson.
"""

import sys
import os
from pathlib import Path

# Add the server directory to the Python path
server_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(server_dir))

from src.database import get_db
from src.models.order import Order, OrderItem
from sqlalchemy.orm import Session
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def remove_customer_orders(customer_id: int, customer_name: str = "Unknown"):
    """
    Remove all orders for a specific customer from the database.
    
    Args:
        customer_id (int): The customer ID to remove orders for
        customer_name (str): Customer name for logging purposes
    """
    db = next(get_db())
    
    try:
        logger.info(f"Starting removal of all orders for {customer_name} (customer_id: {customer_id})")
        
        # First, let's check how many orders exist for this customer
        order_count = db.query(Order).filter(Order.customer_id == customer_id).count()
        logger.info(f"Found {order_count} orders for customer {customer_id}")
        
        if order_count == 0:
            logger.info(f"No orders found for customer {customer_id}. Nothing to delete.")
            return
        
        # Get all order IDs for this customer
        order_ids = db.query(Order.order_id).filter(Order.customer_id == customer_id).all()
        order_ids = [order_id[0] for order_id in order_ids]
        
        logger.info(f"Order IDs to be deleted: {order_ids}")
        
        # Count order items that will be deleted (due to cascade)
        total_items = db.query(OrderItem).filter(OrderItem.order_id.in_(order_ids)).count()
        logger.info(f"Total order items that will be deleted: {total_items}")
        
        # Delete all orders for this customer
        # Due to the cascade="all, delete-orphan" relationship, order items will be deleted automatically
        deleted_orders = db.query(Order).filter(Order.customer_id == customer_id).delete()
        
        # Commit the changes
        db.commit()
        
        logger.info(f"Successfully deleted {deleted_orders} orders for customer {customer_id}")
        logger.info(f"All associated order items ({total_items}) were also deleted due to cascade")
        
        # Verify deletion
        remaining_orders = db.query(Order).filter(Order.customer_id == customer_id).count()
        remaining_items = db.query(OrderItem).filter(OrderItem.order_id.in_(order_ids)).count()
        
        if remaining_orders == 0 and remaining_items == 0:
            logger.info("✅ Verification successful: All orders and items have been removed")
        else:
            logger.warning(f"⚠️  Verification failed: {remaining_orders} orders and {remaining_items} items still exist")
        
    except Exception as e:
        logger.error(f"Error removing orders for customer {customer_id}: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function to remove Kathleen's orders"""
    # Kathleen Simpson's customer_id from the data
    KATHLEEN_CUSTOMER_ID = 28260188
    KATHLEEN_NAME = "Kathleen Simpson"
    
    print("=" * 60)
    print(f"REMOVING ALL ORDERS FOR {KATHLEEN_NAME}")
    print("=" * 60)
    
    # Confirm with user
    response = input(f"Are you sure you want to delete ALL orders for {KATHLEEN_NAME} (customer_id: {KATHLEEN_CUSTOMER_ID})? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("Operation cancelled.")
        return
    
    try:
        remove_customer_orders(KATHLEEN_CUSTOMER_ID, KATHLEEN_NAME)
        print("\n✅ Successfully removed all orders for Kathleen Simpson!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 