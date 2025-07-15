from pathlib import Path
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from .database import engine, Base

def main():
    # ensure all ORM tables are created
    Base.metadata.create_all(bind=engine)

    # Updated paths
    BASE = Path(__file__).resolve().parent.parent.parent  # storefront-chatbot
    DATA = BASE / "data" / "core"
    USERS_TSV = DATA / "customers_with_personas.tsv"  # Use enhanced customer data
    PETS_TSV  = DATA / "pet_profiles.tsv"

    try:
        # 1) load users with persona data
        users_df = pd.read_csv(
            USERS_TSV, sep="\t",
            parse_dates=["CUSTOMER_ORDER_FIRST_PLACED_DTTM"]
        )
        
        if "password_hash" not in users_df.columns:
            users_df = users_df.drop(columns=["password_hash"])
            
        users_df.to_sql(
            name="customers_full",
            con=engine,
            if_exists="replace",
            index=False
        )
        print(f"  • Loaded {len(users_df)} users with persona data")

        # 2) load pets
        pets_df = pd.read_csv(
            PETS_TSV, sep="\t",
            parse_dates=[
                "BIRTHDAY", "ADOPTION_DATE",
                "TIME_CREATED", "TIME_UPDATED",
                "FIRST_BIRTHDAY"
            ]
        )
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
