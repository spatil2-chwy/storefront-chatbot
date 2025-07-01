# Generate random user credentials (username, name, and password) so the UI looks pretty
from pathlib import Path
import pandas as pd
from faker import Faker
from passlib.context import CryptContext
import re

# setup
BASE    = Path(__file__).resolve().parent  
DATA    = BASE / "../data/server-data"
IN_TSV  = DATA / "customers_full.tsv"
OUT_TSV = DATA / "customers_full_with_creds.tsv"

faker      = Faker()
pwd_ctx    = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_email_from_name(name):
    """Generate a realistic email from a person's name"""
    # Clean the name and split into parts
    name_parts = re.sub(r'[^\w\s]', '', name).lower().split()
    
    if len(name_parts) >= 2:
        first_name = name_parts[0]
        last_name = name_parts[-1]
        
        # Common email patterns
        email_patterns = [
            f"{first_name}.{last_name}@gmail.com",
            f"{first_name}{last_name}@gmail.com",
            f"{first_name[0]}{last_name}@gmail.com",
            f"{first_name}_{last_name}@gmail.com",
            f"{first_name}{last_name[0]}@gmail.com",
            f"{first_name}.{last_name[0]}@gmail.com",
        ]
        
        # Return the first pattern
        return email_patterns[0]
    else:
        # Fallback for single names
        return f"{name_parts[0]}@gmail.com"

def main():
    # 1) load the original customers
    df = pd.read_csv(IN_TSV, sep="\t")
    
    # 2) generate names first
    names = [faker.name() for _ in range(len(df))]
    df["name"] = names
    
    # 3) generate emails based on names
    df["email"] = [generate_email_from_name(name) for name in names]
    
    # raw passwords and their hashes
    raw_pwds = [faker.password(length=12) for _ in range(len(df))]
    df["password_hash"] = [pwd_ctx.hash(p) for p in raw_pwds]
    df["password"] = raw_pwds  
    
    # 4) write out
    df.to_csv(OUT_TSV, sep="\t", index=False)
    print(f"Wrote {len(df)} records with credentials → {OUT_TSV}")
    
    # 5) Show some examples
    print("\nExample generated credentials:")
    for i in range(min(5, len(df))):
        print(f"  {df.iloc[i]['name']} → {df.iloc[i]['email']}")

if __name__ == "__main__":
    main()
