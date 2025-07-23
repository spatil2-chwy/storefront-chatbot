from pathlib import Path
import pandas as pd
import random
from sqlalchemy.exc import SQLAlchemyError
from database import engine, Base

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

def main():
    # ensure all ORM tables are created
    Base.metadata.create_all(bind=engine)

    # Updated paths to new structure
    BASE = Path(__file__).resolve().parent.parent.parent 
    DATA = BASE / "data" / "backend"
    USERS_TSV = DATA / "customers" / "customers_with_personas.tsv"  
    PETS_TSV  = DATA / "pets" / "pet_profiles.tsv"

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
        if "password_hash" not in users_df.columns:
            users_df = users_df.drop(columns=["password_hash"])
            
        users_df.to_sql(
            name="customers_full",
            con=engine,
            if_exists="replace",
            index=False
        )
        print(f"  • Loaded {len(users_df)} users with persona data")

        # Load pets
        pets_df.to_sql(
            name="pet_profiles",
            con=engine,
            if_exists="replace",
            index=False
        )
        print(f"Loaded {len(pets_df)} pets")

    except SQLAlchemyError as e:
        print("Error loading data:", e)
        raise

if __name__ == "__main__":
    main()