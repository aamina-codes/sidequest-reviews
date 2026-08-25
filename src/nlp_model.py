import re
from pathlib import Path

import nltk
import pandas as pd

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)


# ==================================================
# CONFIGURATION
# ==================================================

INPUT_FILE = Path("data/processed/reviews.csv")
OUTPUT_FILE = Path("data/processed/reviews_with_predictions.csv")

RANDOM_STATE = 42


# ==================================================
# NLTK RESOURCES
# ==================================================

print("📦 Checking NLTK resources...")

nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")

print("✅ NLTK resources ready.")


# ==================================================
# LOAD DATASET
# ==================================================

print("\n📂 Loading dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"✅ Loaded {len(df):,} reviews")


# ==================================================
# TEXT PREPROCESSING
# ==================================================

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()


def clean_text(text):
    """
    Clean and normalize review text.
    """

    # Convert to lowercase
    text = str(text).lower()

    # Remove HTML tags
    text = re.sub(r"<.*?>", " ", text)

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", " ", text)

    # Keep alphabetic characters only
    text = re.sub(r"[^a-z\s]", " ", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Tokenization
    words = text.split()

    # Stopword removal + lemmatization
    words = [
        lemmatizer.lemmatize(word)
        for word in words
        if word not in stop_words
    ]

    return " ".join(words)


print("\n🧹 Cleaning review text...")

df["cleaned_text"] = df["text"].apply(clean_text)

print("✅ Text preprocessing complete.")


# ==================================================
# REMOVE EMPTY REVIEWS
# ==================================================

df = df[df["cleaned_text"].str.strip() != ""].copy()

print(
    f"Reviews after cleaning: {len(df):,}"
)


# ==================================================
# TRAIN / TEST SPLIT
# ==================================================

X = df["cleaned_text"]
y = df["actual_sentiment"]


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y,
)


print("\n📚 Dataset split:")

print(f"Training reviews: {len(X_train):,}")
print(f"Testing reviews:  {len(X_test):,}")


# ==================================================
# TF-IDF VECTORIZATION
# ==================================================

print("\n🔢 Creating TF-IDF features...")

vectorizer = TfidfVectorizer(
    max_features=10_000,
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
)


X_train_tfidf = vectorizer.fit_transform(X_train)

X_test_tfidf = vectorizer.transform(X_test)


print("✅ TF-IDF complete.")

print(
    f"Training matrix shape: {X_train_tfidf.shape}"
)

print(
    f"Testing matrix shape:  {X_test_tfidf.shape}"
)


# ==================================================
# TRAIN NAIVE BAYES MODEL
# ==================================================

print("\n🧠 Training Multinomial Naive Bayes...")

model = MultinomialNB()

model.fit(
    X_train_tfidf,
    y_train,
)

print("✅ Model training complete.")


# ==================================================
# EVALUATE MODEL
# ==================================================

print("\n🔮 Generating test predictions...")

y_pred = model.predict(X_test_tfidf)

accuracy = accuracy_score(
    y_test,
    y_pred,
)


print("\n" + "=" * 55)
print("🧠 MODEL PERFORMANCE")
print("=" * 55)

print(
    f"\nAccuracy: {accuracy:.2%}"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
    )
)

print("Confusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred,
    )
)


# ==================================================
# PREDICT ALL REVIEWS
# ==================================================

print("\n🔮 Generating predictions for all reviews...")

# Transform ALL cleaned reviews using
# the TF-IDF vectorizer fitted on the training data.

X_all_tfidf = vectorizer.transform(
    df["cleaned_text"]
)


# Predict sentiment for every review

all_predictions = model.predict(
    X_all_tfidf
)


# Get probability/confidence for every prediction

all_probabilities = model.predict_proba(
    X_all_tfidf
)

all_confidence = all_probabilities.max(
    axis=1
)


print(
    f"✅ Predictions generated for "
    f"{len(df):,} reviews."
)


# ==================================================
# CREATE FINAL ANALYTICS DATASET
# ==================================================

final_df = df.copy()

final_df["predicted_sentiment"] = all_predictions

final_df["prediction_confidence"] = all_confidence


# ==================================================
# SAVE FINAL DATASET
# ==================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)


final_df.to_csv(
    OUTPUT_FILE,
    index=False,
)


# ==================================================
# FINAL SUMMARY
# ==================================================

print("\n" + "=" * 55)
print("🎮 SIDEQUEST REVIEWS DATASET READY")
print("=" * 55)

print(
    f"\nFinal analytics dataset: "
    f"{len(final_df):,} reviews"
)

print(
    f"\nModel accuracy: "
    f"{accuracy:.2%}"
)

print("\nActual sentiment:")

print(
    final_df["actual_sentiment"].value_counts()
)

print("\nPredicted sentiment:")

print(
    final_df["predicted_sentiment"].value_counts()
)

print("\nPrediction confidence:")

print(
    final_df["prediction_confidence"].describe()
)

print(
    f"\n💾 Saved to:\n{OUTPUT_FILE}"
)

print(
    "\n🎉 Sidequest Reviews NLP pipeline complete!"
)