import json
import random
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Configuration
# --------------------------------------------------

INPUT_FILE = Path("data/raw/All_Beauty.jsonl")
OUTPUT_FILE = Path("data/processed/reviews.csv")

SAMPLE_SIZE = 20_000
RANDOM_STATE = 42


# --------------------------------------------------
# Load reviews
# --------------------------------------------------

print("📂 Loading Amazon reviews...")

reviews = []

with open(INPUT_FILE, "r", encoding="utf-8") as file:

    for line in file:
        review = json.loads(line)
        reviews.append(review)

print(f"✅ Loaded {len(reviews):,} reviews")


# --------------------------------------------------
# Convert to DataFrame
# --------------------------------------------------

df = pd.DataFrame(reviews)

print("\n📊 Original columns:")
print(df.columns.tolist())


# --------------------------------------------------
# Keep relevant columns
# --------------------------------------------------

columns_to_keep = [
    "rating",
    "title",
    "text",
    "asin",
    "parent_asin",
    "user_id",
    "timestamp",
    "helpful_vote",
    "verified_purchase",
]

df = df[columns_to_keep]


# --------------------------------------------------
# Remove missing reviews
# --------------------------------------------------

df = df.dropna(subset=["text", "rating"])

# Remove empty review text
df["text"] = df["text"].astype(str).str.strip()

df = df[df["text"] != ""]


# --------------------------------------------------
# Create sentiment labels
# --------------------------------------------------

def assign_sentiment(rating):

    if rating <= 2:
        return "Negative"

    elif rating >= 4:
        return "Positive"

    return None


df["actual_sentiment"] = df["rating"].apply(assign_sentiment)


# Remove neutral 3-star reviews
df = df.dropna(subset=["actual_sentiment"])


# --------------------------------------------------
# Balance the dataset
# --------------------------------------------------

positive_reviews = df[
    df["actual_sentiment"] == "Positive"
]

negative_reviews = df[
    df["actual_sentiment"] == "Negative"
]


print("\n📊 Available sentiment distribution:")
print(f"Positive: {len(positive_reviews):,}")
print(f"Negative: {len(negative_reviews):,}")


samples_per_class = SAMPLE_SIZE // 2


positive_sample = positive_reviews.sample(
    n=samples_per_class,
    random_state=RANDOM_STATE
)

negative_sample = negative_reviews.sample(
    n=samples_per_class,
    random_state=RANDOM_STATE
)


df = pd.concat(
    [
        positive_sample,
        negative_sample
    ]
)


# Shuffle the final dataset

df = df.sample(
    frac=1,
    random_state=RANDOM_STATE
).reset_index(drop=True)


# --------------------------------------------------
# Create review IDs
# --------------------------------------------------

df.insert(
    0,
    "review_id",
    range(1, len(df) + 1)
)


# --------------------------------------------------
# Convert timestamp
# --------------------------------------------------

df["review_date"] = pd.to_datetime(
    df["timestamp"],
    unit="ms",
    errors="coerce"
).dt.date


# --------------------------------------------------
# Rename columns
# --------------------------------------------------

df = df.rename(
    columns={
        "asin": "product_id",
        "parent_asin": "parent_product_id",
        "helpful_vote": "helpful_votes",
    }
)


# --------------------------------------------------
# Select final columns
# --------------------------------------------------

final_columns = [
    "review_id",
    "product_id",
    "parent_product_id",
    "title",
    "text",
    "rating",
    "actual_sentiment",
    "verified_purchase",
    "helpful_votes",
    "review_date",
]

df = df[final_columns]


# --------------------------------------------------
# Save processed dataset
# --------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\n" + "=" * 50)
print("🎮 SIDEQUEST REVIEWS DATASET READY")
print("=" * 50)

print(f"\nTotal reviews: {len(df):,}")

print("\nSentiment distribution:")
print(df["actual_sentiment"].value_counts())

print("\nRating distribution:")
print(df["rating"].value_counts().sort_index())

print("\nVerified purchase:")
print(df["verified_purchase"].value_counts())

print("\nOutput:")
print(OUTPUT_FILE)

print("\n✅ Dataset preparation complete!")