CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY,
    product_id VARCHAR(50),
    parent_product_id VARCHAR(50),
    title TEXT,
    review_text TEXT NOT NULL,
    rating NUMERIC(2,1),
    actual_sentiment VARCHAR(20),
    cleaned_text TEXT,
    predicted_sentiment VARCHAR(20),
    prediction_confidence NUMERIC(6,5),
    verified_purchase BOOLEAN,
    helpful_votes INTEGER DEFAULT 0,
    review_date DATE
);