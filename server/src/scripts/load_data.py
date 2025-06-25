from pathlib import Path
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from src.database import engine, Base

def main():
    # ensure all ORM tables are created
    Base.metadata.create_all(bind=engine)

    BASE = Path(__file__).resolve().parent.parent  # server/src
    DATA = BASE / "data"
    USERS_TSV = DATA / "customers_full.tsv"
    PETS_TSV  = DATA / "pet_profiles_assigned.tsv"

    try:
        # 1) load users
        users_df = pd.read_csv(
            USERS_TSV, sep="\t",
            parse_dates=["CUSTOMER_ORDER_FIRST_PLACED_DTTM"]
        )
        users_df.to_sql(
            name="customers_full",
            con=engine,
            if_exists="append",
            index=False
        )
        print(f"  • Loaded {len(users_df)} users")

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
            if_exists="append",
            index=False
        )
        print(f"  • Loaded {len(pets_df)} pets")

    except SQLAlchemyError as e:
        print("Error loading data:", e)
        raise

if __name__ == "__main__":
    main()
