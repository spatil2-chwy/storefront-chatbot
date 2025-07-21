from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from src.models.order import Order, OrderItem
from src.schemas import OrderCreate, Order as OrderSchema, OrderSummary
import logging

logger = logging.getLogger(__name__)

class OrderService:
    
    @staticmethod
    def create_order(db: Session, order_data: OrderCreate) -> OrderSchema:
        """Create a new order with order items"""
        try:
            # Create the order
            db_order = Order(
                customer_id=order_data.customer_id,
                subtotal=order_data.subtotal,
                shipping_cost=order_data.shipping_cost,
                tax_amount=order_data.tax_amount,
                total_amount=order_data.total_amount,
                shipping_first_name=order_data.shipping_first_name,
                shipping_last_name=order_data.shipping_last_name,
                shipping_email=order_data.shipping_email,
                shipping_phone=order_data.shipping_phone,
                shipping_address=order_data.shipping_address,
                shipping_city=order_data.shipping_city,
                shipping_state=order_data.shipping_state,
                shipping_zip_code=order_data.shipping_zip_code,
                payment_method=order_data.payment_method,
                card_last_four=order_data.card_last_four,
                cardholder_name=order_data.cardholder_name,
                billing_address=order_data.billing_address,
                billing_city=order_data.billing_city,
                billing_state=order_data.billing_state,
                billing_zip_code=order_data.billing_zip_code,
                order_date=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(db_order)
            db.flush()  # Get the order_id
            
            # Create order items
            for item_data in order_data.items:
                db_order_item = OrderItem(
                    order_id=db_order.order_id,
                    product_id=item_data.product_id,
                    product_title=item_data.product_title,
                    product_brand=item_data.product_brand,
                    product_image=item_data.product_image,
                    quantity=item_data.quantity,
                    purchase_option=item_data.purchase_option,
                    unit_price=item_data.unit_price,
                    total_price=item_data.total_price
                )
                db.add(db_order_item)
            
            db.commit()
            db.refresh(db_order)
            
            logger.info(f"Created order {db_order.order_id} for customer {order_data.customer_id}")
            return OrderSchema.from_orm(db_order)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating order: {str(e)}")
            raise
    
    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> Optional[OrderSchema]:
        """Get order by ID"""
        db_order = db.query(Order).filter(Order.order_id == order_id).first()
        if db_order:
            return OrderSchema.from_orm(db_order)
        return None
    
    @staticmethod
    def get_orders_by_customer(db: Session, customer_id: int) -> List[OrderSummary]:
        """Get all orders for a customer (summary view)"""
        orders = db.query(Order).filter(Order.customer_id == customer_id).order_by(Order.order_date.desc()).all()
        
        order_summaries = []
        for order in orders:
            items_count = len(order.items)
            order_summary = OrderSummary(
                order_id=order.order_id,
                order_date=order.order_date,
                status=order.status,
                total_amount=order.total_amount,
                items_count=items_count
            )
            order_summaries.append(order_summary)
        
        return order_summaries
    
    @staticmethod
    def update_order_status(db: Session, order_id: int, new_status: str) -> Optional[OrderSchema]:
        """Update order status"""
        try:
            db_order = db.query(Order).filter(Order.order_id == order_id).first()
            if not db_order:
                return None
            
            db_order.status = new_status
            db_order.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(db_order)
            
            logger.info(f"Updated order {order_id} status to {new_status}")
            return OrderSchema.from_orm(db_order)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating order status: {str(e)}")
            raise
