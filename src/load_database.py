from pathlib import Path
import os

import pandas as pd
from sqlalchemy import create_engine, text


# ==================================================
# CONFIGURATION
# ==================================================

INPUT_FILE = Path(
    "data/processed/reviews_with_predictions.csv"
)

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "sidequest_reviews"
DB_USER = "sidequest"


# ==================================================
# LOAD DATASET
# ==================================================

print("📂 Loading final analytics dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"✅ Loaded {len(df):,} reviews")


# ==================================================
# PREPARE COLUMNS
# ==================================================

# Rename CSV columns to match PostgreSQL

df = df.rename(
    columns={
        "text": "review_text",
        "asin": "product_id",
        "parent_asin": "parent_product_id",
        "helpful_vote": "helpful_votes",
        "timestamp": "review_date",
    }
)


# Keep only columns that exist in our SQL table

columns = [
    "review_id",
    "product_id",
    "parent_product_id",
    "title",
    "review_text",
    "rating",
    "actual_sentiment",
    "cleaned_text",
    "predicted_sentiment",
    "prediction_confidence",
    "verified_purchase",
    "helpful_votes",
    "review_date",
]

df = df[columns].copy()

# ==================================================
# DATA QUALITY CLEANUP
# ==================================================

before = len(df)

df = df[
    df["review_text"].notna()
    & (df["review_text"].str.strip() != "")
].copy()

removed = before - len(df)

print(
    f"🧹 Removed {removed:,} reviews "
    "with missing review text"
)

print(
    f"📊 Reviews ready for database: "
    f"{len(df):,}"
)


# ==================================================
# DATA TYPE CLEANUP
# ==================================================

df["review_id"] = (
    pd.to_numeric(
        df["review_id"],
        errors="coerce"
    )
    .astype("Int64")
)


df["rating"] = pd.to_numeric(
    df["rating"],
    errors="coerce"
)


df["prediction_confidence"] = pd.to_numeric(
    df["prediction_confidence"],
    errors="coerce"
)


df["helpful_votes"] = (
    pd.to_numeric(
        df["helpful_votes"],
        errors="coerce"
    )
    .fillna(0)
    .astype(int)
)


df["review_date"] = pd.to_datetime(
    df["review_date"],
    errors="coerce"
).dt.date


# ==================================================
# DATABASE PASSWORD
# ==================================================

DB_PASSWORD = os.getenv(
    "SIDEQUEST_DB_PASSWORD"
)

if not DB_PASSWORD:
    raise RuntimeError(
        "SIDEQUEST_DB_PASSWORD is not set."
    )


# ==================================================
# DATABASE CONNECTION
# ==================================================

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/"
    f"{DB_NAME}"
)


print("\n🐘 Connecting to PostgreSQL...")

engine = create_engine(
    DATABASE_URL
)


# Test connection

with engine.connect() as connection:

    result = connection.execute(
        text(
            "SELECT current_database(), current_user;"
        )
    )

    database, user = result.fetchone()


print(
    f"✅ Connected to database: {database}"
)

print(
    f"👤 Connected as: {user}"
)


# ==================================================
# INSERT DATA
# ==================================================

print("\n📤 Uploading reviews...")
print("This may take a little while...")


df.to_sql(
    name="reviews",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=500,
)


print(
    f"✅ Uploaded {len(df):,} reviews!"
)


# ==================================================
# VERIFY
# ==================================================

with engine.connect() as connection:

    result = connection.execute(
        text(
            "SELECT COUNT(*) FROM reviews;"
        )
    )

    count = result.scalar()


print("\n" + "=" * 55)

print(
    f"📊 Reviews currently in database: "
    f"{count:,}"
)

print("=" * 55)


if count == len(df):

    print(
        "\n🎉 ALL REVIEWS SUCCESSFULLY LOADED!"
    )

else:

    print(
           "\n⚠️ Row count does not match."
    )