# NOTE: DO NOT RUN THIS SCRIPT.
# This script is used to assign pets to users in the database, because the original data only has pets without owners.
# I am using the fake user data and user ids from the old mockup

import pandas as pd
import numpy as np
import os

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
DATA_DIR      = os.path.normpath(os.path.join(BASE_DIR, "..", "data"))

CUSTOMERS_TSV = os.path.join(DATA_DIR, "customers_full.tsv")
PETS_TSV      = os.path.join(DATA_DIR, "pet_profiles.tsv")
OUTPUT_TSV    = os.path.join(DATA_DIR, "pet_profiles_assigned.tsv")

# load data
users_df = pd.read_csv(
    CUSTOMERS_TSV, sep="\t",
    parse_dates=["CUSTOMER_ORDER_FIRST_PLACED_DTTM"]
)
pets_df = pd.read_csv(
    PETS_TSV, sep="\t",
    parse_dates=[
        "BIRTHDAY","ADOPTION_DATE",
        "TIME_CREATED","TIME_UPDATED",
        "FIRST_BIRTHDAY"
    ]
)

# get valid user IDs
user_ids = users_df["CUSTOMER_ID"].unique()

# randomly pick an owner for each pet
pets_df["CUSTOMER_ID"] = np.random.choice(user_ids, size=len(pets_df))

# sanity check: no nulls, all CUSTOMER_IDs are valid
assert pets_df["CUSTOMER_ID"].notna().all()
assert set(pets_df["CUSTOMER_ID"].unique()).issubset(set(user_ids))

# write out new pet_profiles.tsv
pets_df.to_csv(OUTPUT_TSV, sep="\t", index=False)
print(f"Written assigned file to {OUTPUT_TSV}")
