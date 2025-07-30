#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import get_db
from sqlalchemy import text

def fix_pet_profiles_table():
    db = next(get_db())
    
    try:
        print("=== Fixing pet_profiles table ===")
        
        # First, let's backup the existing data
        print("Backing up existing pet data...")
        existing_pets = db.execute(text("SELECT * FROM pet_profiles")).fetchall()
        print(f"Found {len(existing_pets)} existing pets")
        
        # Drop the existing table
        print("Dropping existing pet_profiles table...")
        db.execute(text("DROP TABLE IF EXISTS pet_profiles"))
        
        # Create the table with proper auto-increment
        print("Creating new pet_profiles table with auto-increment...")
        create_table_sql = """
        CREATE TABLE pet_profiles (
            PET_PROFILE_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CUSTOMER_ID BIGINT,
            PET_NAME TEXT,
            PET_TYPE TEXT,
            PET_BREED TEXT,
            PET_BREED_SIZE_TYPE TEXT,
            GENDER TEXT,
            WEIGHT_TYPE FLOAT,
            SIZE_TYPE TEXT,
            BIRTHDAY DATETIME,
            LIFE_STAGE TEXT,
            ADOPTED BOOLEAN,
            ADOPTION_DATE DATETIME,
            STATUS TEXT,
            STATUS_REASON TEXT,
            TIME_CREATED DATETIME,
            TIME_UPDATED DATETIME,
            WEIGHT FLOAT,
            ALLERGIES TEXT,
            PHOTO_COUNT BIGINT,
            PET_BREED_ID BIGINT,
            PET_TYPE_ID BIGINT,
            PET_NEW BOOLEAN,
            FIRST_BIRTHDAY DATETIME
        )
        """
        db.execute(text(create_table_sql))
        
        # Re-insert the existing data (excluding NULL pet_profile_id records)
        print("Re-inserting valid pet data...")
        valid_pets = [pet for pet in existing_pets if pet[0] is not None]  # pet[0] is pet_profile_id
        print(f"Re-inserting {len(valid_pets)} valid pets")
        
        for pet in valid_pets:
            # Convert tuple to dict for parameter binding
            params = {
                'pet_profile_id': pet[0],
                'customer_id': pet[1],
                'pet_name': pet[2],
                'pet_type': pet[3],
                'pet_breed': pet[4],
                'pet_breed_size_type': pet[5],
                'gender': pet[6],
                'weight_type': pet[7],
                'size_type': pet[8],
                'birthday': pet[9],
                'life_stage': pet[10],
                'adopted': pet[11],
                'adoption_date': pet[12],
                'status': pet[13],
                'status_reason': pet[14],
                'time_created': pet[15],
                'time_updated': pet[16],
                'weight': pet[17],
                'allergies': pet[18],
                'photo_count': pet[19],
                'pet_breed_id': pet[20],
                'pet_type_id': pet[21],
                'pet_new': pet[22],
                'first_birthday': pet[23]
            }
            
            insert_sql = """
            INSERT INTO pet_profiles (
                PET_PROFILE_ID, CUSTOMER_ID, PET_NAME, PET_TYPE, PET_BREED, 
                PET_BREED_SIZE_TYPE, GENDER, WEIGHT_TYPE, SIZE_TYPE, BIRTHDAY, 
                LIFE_STAGE, ADOPTED, ADOPTION_DATE, STATUS, STATUS_REASON, 
                TIME_CREATED, TIME_UPDATED, WEIGHT, ALLERGIES, PHOTO_COUNT, 
                PET_BREED_ID, PET_TYPE_ID, PET_NEW, FIRST_BIRTHDAY
            ) VALUES (:pet_profile_id, :customer_id, :pet_name, :pet_type, :pet_breed, 
                     :pet_breed_size_type, :gender, :weight_type, :size_type, :birthday, 
                     :life_stage, :adopted, :adoption_date, :status, :status_reason, 
                     :time_created, :time_updated, :weight, :allergies, :photo_count, 
                     :pet_breed_id, :pet_type_id, :pet_new, :first_birthday)
            """
            db.execute(text(insert_sql), params)
        
        db.commit()
        print("Successfully fixed pet_profiles table!")
        
        # Verify the fix
        result = db.execute(text("PRAGMA table_info(pet_profiles)")).fetchall()
        print("\n=== New table schema ===")
        for row in result:
            print(f"Column: {row}")
            
    except Exception as e:
        print(f"Error fixing table: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_pet_profiles_table()
