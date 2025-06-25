# Generate random user credentials (username, name, and password) so the UI looks pretty
from pathlib import Path
import pandas as pd
from faker import Faker
from passlib.context import CryptContext

# setup
BASE    = Path(__file__).resolve().parent.parent  
DATA    = BASE / "data"
IN_TSV  = DATA / "customers_full.tsv"
OUT_TSV = DATA / "customers_full_with_creds.tsv"

faker      = Faker()
pwd_ctx    = CryptContext(schemes=["bcrypt"], deprecated="auto")

def main():
    # 1) load the original customers
    df = pd.read_csv(IN_TSV, sep="\t")
    
    # 2) generate
    df["name"] = [faker.name() for _ in range(len(df))]
    df["email"] = [f"{faker.unique.user_name()}@gmail.com" for _ in range(len(df))]
    
    # raw passwords (if you want to inspect them; omit if you only need hashes)
    raw_pwds = [faker.password(length=12) for _ in range(len(df))]
    df["password_hash"] = [pwd_ctx.hash(p) for p in raw_pwds]
    df["password"] = raw_pwds  
    
    # 3) write out
    df.to_csv(OUT_TSV, sep="\t", index=False)
    print(f"Wrote {len(df)} records with credentials → {OUT_TSV}")

if __name__ == "__main__":
    main()
