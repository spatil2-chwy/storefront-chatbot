"""
Script to create database tables for the persona memory system.
Run this to set up the new persona tracking tables.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from src.database import Base, get_database_url
from src.models.persona_memory import PersonaUpdate, PersonaCategory
from src.models.user import User  # Import to ensure table exists
from src.models.interaction import Interaction


def create_persona_tables():
    """Create the persona memory tables."""
    
    # Get database URL
    database_url = get_database_url()
    engine = create_engine(database_url)
    
    print("Creating persona memory tables...")
    
    # Create only the new tables
    PersonaUpdate.__table__.create(engine, checkfirst=True)
    PersonaCategory.__table__.create(engine, checkfirst=True)
    Interaction.__table__.create(engine, checkfirst=True)
    
    print("✅ Persona memory tables created successfully!")
    
    # Initialize default persona categories
    initialize_default_categories(engine)


def initialize_default_categories(engine):
    """Initialize the default persona categories."""
    from sqlalchemy.orm import sessionmaker
    import json
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if categories already exist
        existing_count = session.query(PersonaCategory).count()
        if existing_count > 0:
            print(f"Found {existing_count} existing persona categories, skipping initialization.")
            return
        
        print("Initializing default persona categories...")
        
        default_categories = [
            {
                "name": "brand_preference",
                "description": "Brand preferences for specific product types",
                "subcategories": json.dumps(["dog_toys", "cat_toys", "dog_food", "cat_food", "treats", "accessories", "general"])
            },
            {
                "name": "quality_preference", 
                "description": "Quality and luxury preferences",
                "subcategories": json.dumps(["dog_toys", "cat_toys", "food", "treats", "accessories", "general"])
            },
            {
                "name": "price_sensitivity",
                "description": "Price range and budget preferences", 
                "subcategories": json.dumps(["dog_toys", "cat_toys", "food", "treats", "accessories", "general"])
            },
            {
                "name": "ingredient_preference",
                "description": "Ingredient and dietary preferences",
                "subcategories": json.dumps(["dog_food", "cat_food", "treats", "general"])
            },
            {
                "name": "pet_care_philosophy",
                "description": "Overall approach to pet care",
                "subcategories": json.dumps(["health", "training", "lifestyle", "general"])
            }
        ]
        
        for cat_data in default_categories:
            category = PersonaCategory(**cat_data)
            session.add(category)
        
        session.commit()
        print(f"✅ Initialized {len(default_categories)} default persona categories!")
        
    except Exception as e:
        print(f"❌ Error initializing categories: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    create_persona_tables()