from pathlib import Path
import pandas as pd
import random
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from src.database import engine, Base, get_db

def generate_sample_pet_data():
    """Generate sample pet data"""
    # Sample pet data
    pets_data = []
    
    # Generate 50 sample pets
    for i in range(1, 51):
        pet_data = {
            'PET_PROFILE_ID': i,
            'CUSTOMER_ID': random.randint(1, 10),  # 10 customers
            'PET_NAME': f"Pet{i}",
            'PET_TYPE': random.choice(['DOG', 'CAT']),
            'PET_BREED': random.choice(['Golden Retriever', 'Labrador', 'Persian', 'Siamese', 'Mixed Breed']),
            'PET_BREED_SIZE_TYPE': random.choice(['SMALL', 'MEDIUM', 'LARGE', None]),
            'GENDER': random.choice(['MALE', 'FEMALE']),
            'WEIGHT_TYPE': random.choice(['LBS', 'KG', None]),
            'SIZE_TYPE': random.choice(['SMALL', 'MEDIUM', 'LARGE', None]),
            'BIRTHDAY': pd.Timestamp.now() - pd.Timedelta(days=random.randint(365, 3650)),
            'LIFE_STAGE': random.choice(['P', 'A', 'S']),  # Puppy, Adult, Senior
            'ADOPTED': random.choice([True, False]),
            'ADOPTION_DATE': None,  # Will be set if adopted
            'STATUS': 'ACTIVE',
            'STATUS_REASON': None,
            'TIME_CREATED': pd.Timestamp.now(),
            'TIME_UPDATED': pd.Timestamp.now(),
            'WEIGHT': random.uniform(5.0, 80.0),
            'ALLERGIES': 'None', 
            'PHOTO_COUNT': random.randint(0, 5),
            'PET_BREED_ID': random.randint(1, 100),
            'PET_TYPE_ID': random.randint(1, 10),
            'PET_NEW': random.choice([True, False]),
            'FIRST_BIRTHDAY': None
        }
        
        # Set adoption date if adopted
        if pet_data['ADOPTED']:
            pet_data['ADOPTION_DATE'] = pet_data['BIRTHDAY'] + pd.Timedelta(days=random.randint(30, 365))
        
        pets_data.append(pet_data)
    
    return pd.DataFrame(pets_data)

def generate_sample_user_data():
    """Generate sample user data"""
    users_data = []
    
    for i in range(1, 11):  # 10 users
        user_data = {
            'CUSTOMER_KEY': i,
            'CUSTOMER_ID': i,
            'PASSWORD': 'password123',  # In real app, this would be hashed
            'NAME': f'User {i}',
            'EMAIL': f'user{i}@example.com',
            'OPERATING_REVENUE_TRAILING_365': random.uniform(100.0, 5000.0),
            'CUSTOMER_ORDER_FIRST_PLACED_DTTM': pd.Timestamp.now() - pd.Timedelta(days=random.randint(30, 365)),
            'CUSTOMER_ADDRESS_ZIP': f'{random.randint(10000, 99999)}',
            'CUSTOMER_ADDRESS_CITY': random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']),
            'CUSTOMER_ADDRESS_STATE': random.choice(['NY', 'CA', 'IL', 'TX', 'AZ']),
            'PERSONA_SUMMARY': f'Customer {i} is a pet owner who loves their pets.',
            'PREFERRED_BRANDS': '["Chewy", "Royal Canin", "Purina"]',
            'SPECIAL_DIET': '["Grain-free", "High-protein"]',
            'POSSIBLE_NEXT_BUYS': 'Pet food, treats, toys',
            'PRICE_RANGE_FOOD': '{"min": 20, "max": 100}',
            'PRICE_RANGE_TREATS': '{"min": 5, "max": 30}',
            'PRICE_RANGE_WASTE_MANAGEMENT': '{"min": 10, "max": 50}',
            'PRICE_RANGE_BEDS': '{"min": 15, "max": 80}',
            'PRICE_RANGE_FEEDERS': '{"min": 20, "max": 150}',
            'PRICE_RANGE_LEASHES_AND_COLLARS': '{"min": 10, "max": 60}'
        }
        users_data.append(user_data)
    
    return pd.DataFrame(users_data)

def create_pet_profiles_table():
    """Create the pet_profiles table with proper schema and auto-increment"""
    db = next(get_db())
    
    try:
        print("=== Creating pet_profiles table with proper schema ===")
        
        # Drop existing table if it exists
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
        db.commit()
        print("Successfully created pet_profiles table!")
        
        # Verify the table schema
        result = db.execute(text("PRAGMA table_info(pet_profiles)")).fetchall()
        print("\n=== Pet profiles table schema ===")
        for row in result:
            print(f"Column: {row}")
            
    except Exception as e:
        print(f"Error creating pet_profiles table: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def load_pet_data(pets_df):
    """Load pet data into the database with proper handling"""
    db = next(get_db())
    
    try:
        print("=== Loading pet data ===")
        
        # Filter out any rows with NULL PET_PROFILE_ID
        valid_pets = pets_df[pets_df['PET_PROFILE_ID'].notna()].copy()
        print(f"Loading {len(valid_pets)} valid pets (filtered from {len(pets_df)} total)")
        
        # Insert pet data using parameterized queries
        for _, pet in valid_pets.iterrows():
            # Convert pandas Timestamp objects to strings and handle NaN values
            def convert_value(value):
                if pd.isna(value):
                    return None
                elif isinstance(value, pd.Timestamp):
                    return value.isoformat()
                elif isinstance(value, bool):
                    return 1 if value else 0  # Convert boolean to integer for SQLite
                else:
                    return value
            
            params = {
                'pet_profile_id': int(pet['PET_PROFILE_ID']),
                'customer_id': convert_value(pet['CUSTOMER_ID']),
                'pet_name': convert_value(pet['PET_NAME']),
                'pet_type': convert_value(pet['PET_TYPE']),
                'pet_breed': convert_value(pet['PET_BREED']),
                'pet_breed_size_type': convert_value(pet['PET_BREED_SIZE_TYPE']),
                'gender': convert_value(pet['GENDER']),
                'weight_type': convert_value(pet['WEIGHT_TYPE']),
                'size_type': convert_value(pet['SIZE_TYPE']),
                'birthday': convert_value(pet['BIRTHDAY']),
                'life_stage': convert_value(pet['LIFE_STAGE']),
                'adopted': convert_value(pet['ADOPTED']),
                'adoption_date': convert_value(pet['ADOPTION_DATE']),
                'status': convert_value(pet['STATUS']),
                'status_reason': convert_value(pet['STATUS_REASON']),
                'time_created': convert_value(pet['TIME_CREATED']),
                'time_updated': convert_value(pet['TIME_UPDATED']),
                'weight': convert_value(pet['WEIGHT']),
                'allergies': convert_value(pet['ALLERGIES']),
                'photo_count': convert_value(pet['PHOTO_COUNT']),
                'pet_breed_id': convert_value(pet['PET_BREED_ID']),
                'pet_type_id': convert_value(pet['PET_TYPE_ID']),
                'pet_new': convert_value(pet['PET_NEW']),
                'first_birthday': convert_value(pet['FIRST_BIRTHDAY'])
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
        print(f"Successfully loaded {len(valid_pets)} pets into database!")
        
    except Exception as e:
        print(f"Error loading pet data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def test_pet_data_loading():
    """Test function to verify pet data was loaded correctly"""
    db = next(get_db())
    
    try:
        print("=== Testing pet data loading ===")
        
        # Check table exists
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='pet_profiles'")).fetchone()
        if not result:
            print("❌ pet_profiles table does not exist!")
            return False
        
        # Check row count
        count_result = db.execute(text("SELECT COUNT(*) FROM pet_profiles")).fetchone()
        pet_count = count_result[0] if count_result else 0
        print(f"✅ pet_profiles table exists with {pet_count} pets")
        
        # Check auto-increment is working
        max_id_result = db.execute(text("SELECT MAX(PET_PROFILE_ID) FROM pet_profiles")).fetchone()
        max_id = max_id_result[0] if max_id_result and max_id_result[0] else 0
        print(f"✅ Max PET_PROFILE_ID: {max_id}")
        
        # Check for any NULL PET_PROFILE_ID values
        null_id_result = db.execute(text("SELECT COUNT(*) FROM pet_profiles WHERE PET_PROFILE_ID IS NULL")).fetchone()
        null_count = null_id_result[0] if null_id_result else 0
        print(f"✅ NULL PET_PROFILE_ID count: {null_count}")
        
        # Show sample data
        sample_result = db.execute(text("SELECT PET_PROFILE_ID, PET_NAME, PET_TYPE, CUSTOMER_ID FROM pet_profiles LIMIT 5")).fetchall()
        print("\n=== Sample pet data ===")
        for row in sample_result:
            print(f"ID: {row[0]}, Name: {row[1]}, Type: {row[2]}, Customer: {row[3]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing pet data: {e}")
        return False
    finally:
        db.close()

def main():
    # ensure all ORM tables are created
    Base.metadata.create_all(bind=engine)

    # Updated paths to new structure
    BASE = Path(__file__).resolve().parent.parent.parent 
    DATA = BASE / "data" / "backend"
    USERS_TSV = DATA / "customers" / "customers_with_personas.tsv"  
    PETS_TSV = DATA / "pets" / "pet_profiles.tsv"

    try:
        # Check if data files exist, if not generate sample data
        if not USERS_TSV.exists() or not PETS_TSV.exists():
            print("Sample data files not found. Generating sample data...")
            
            # Create directories if they don't exist
            USERS_TSV.parent.mkdir(parents=True, exist_ok=True)
            PETS_TSV.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate sample data
            users_df = generate_sample_user_data()
            pets_df = generate_sample_pet_data()
            
            # Save to TSV files
            users_df.to_csv(USERS_TSV, sep="\t", index=False)
            pets_df.to_csv(PETS_TSV, sep="\t", index=False)
            
            print(f"Generated sample data files:")
            print(f"  • {USERS_TSV}")
            print(f"  • {PETS_TSV}")
        else:
            # Load existing data
            users_df = pd.read_csv(
                USERS_TSV, sep="\t",
                parse_dates=["CUSTOMER_ORDER_FIRST_PLACED_DTTM"]
            )
            pets_df = pd.read_csv(
                PETS_TSV, sep="\t",
                parse_dates=[
                    "BIRTHDAY", "ADOPTION_DATE",
                    "TIME_CREATED", "TIME_UPDATED",
                    "FIRST_BIRTHDAY"
                ]
            )
            
            print(f"Loaded existing data files:")
            print(f"  • {USERS_TSV}")
            print(f"  • {PETS_TSV}")
        
        # Load users
        # if "password_hash" not in users_df.columns:
        #     users_df = users_df.drop(columns=["password_hash"])
            
        users_df.to_sql(
            name="customers_full",
            con=engine,
            if_exists="replace",
            index=False
        )
        print(f"  • Loaded {len(users_df)} users with persona data")

        # Create pet_profiles table with proper schema
        create_pet_profiles_table()
        
        # Load pets using custom function
        load_pet_data(pets_df)
        
        # Test the data loading
        test_pet_data_loading()

    except SQLAlchemyError as e:
        print("Error loading data:", e)
        raise

if __name__ == "__main__":
    main()