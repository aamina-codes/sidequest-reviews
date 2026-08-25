-- ============================================================
-- SIDEQUEST REVIEWS — ANALYTICS QUERIES
-- ============================================================


-- ============================================================
-- 01. OVERALL SENTIMENT DISTRIBUTION
-- ============================================================

SELECT
    actual_sentiment,
    COUNT(*) AS review_count,
    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM reviews
GROUP BY actual_sentiment
ORDER BY review_count DESC;


-- ============================================================
-- 02. RATING DISTRIBUTION
-- ============================================================

SELECT
    rating,
    COUNT(*) AS review_count,
    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM reviews
GROUP BY rating
ORDER BY rating;


-- ============================================================
-- 03. SENTIMENT BY RATING
-- ============================================================

SELECT
    rating,
    actual_sentiment,
    COUNT(*) AS review_count
FROM reviews
GROUP BY
    rating,
    actual_sentiment
ORDER BY
    rating,
    actual_sentiment;


-- ============================================================
-- 04. VERIFIED VS UNVERIFIED PURCHASE
-- ============================================================

SELECT
    verified_purchase,
    COUNT(*) AS review_count,
    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage
FROM reviews
GROUP BY verified_purchase
ORDER BY verified_purchase DESC;


-- ============================================================
-- 05. SENTIMENT BY VERIFIED PURCHASE
-- ============================================================

SELECT
    verified_purchase,
    actual_sentiment,
    COUNT(*) AS review_count
FROM reviews
GROUP BY
    verified_purchase,
    actual_sentiment
ORDER BY
    verified_purchase DESC,
    actual_sentiment;


-- ============================================================
-- 06. AVERAGE RATING BY SENTIMENT
-- ============================================================

SELECT
    actual_sentiment,
    ROUND(AVG(rating), 2) AS average_rating,
    COUNT(*) AS review_count
FROM reviews
GROUP BY actual_sentiment
ORDER BY average_rating DESC;


-- ============================================================
-- 07. HELPFUL REVIEWS
-- ============================================================

SELECT
    actual_sentiment,
    COUNT(*) AS review_count,
    SUM(helpful_votes) AS total_helpful_votes,
    ROUND(AVG(helpful_votes), 2) AS avg_helpful_votes
FROM reviews
GROUP BY actual_sentiment
ORDER BY total_helpful_votes DESC;


-- ============================================================
-- 08. TOP 10 MOST HELPFUL NEGATIVE REVIEWS
-- ============================================================

SELECT
    review_id,
    title,
    rating,
    helpful_votes,
    verified_purchase,
    review_date,
    review_text
FROM reviews
WHERE actual_sentiment = 'Negative'
ORDER BY helpful_votes DESC
LIMIT 10;


-- ============================================================
-- 09. TOP 10 MOST HELPFUL POSITIVE REVIEWS
-- ============================================================

SELECT
    review_id,
    title,
    rating,
    helpful_votes,
    verified_purchase,
    review_date,
    review_text
FROM reviews
WHERE actual_sentiment = 'Positive'
ORDER BY helpful_votes DESC
LIMIT 10;


-- ============================================================
-- 10. MODEL PREDICTION PERFORMANCE
-- ============================================================

SELECT
    COUNT(*) AS total_predictions,

    SUM(
        CASE
            WHEN actual_sentiment = predicted_sentiment
            THEN 1
            ELSE 0
        END
    ) AS correct_predictions,

    SUM(
        CASE
            WHEN actual_sentiment <> predicted_sentiment
            THEN 1
            ELSE 0
        END
    ) AS incorrect_predictions,

    ROUND(
        SUM(
            CASE
                WHEN actual_sentiment = predicted_sentiment
                THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*),
        2
    ) AS accuracy_percentage

FROM reviews;


-- ============================================================
-- 11. PREDICTION CONFIDENCE
-- ============================================================

SELECT
    predicted_sentiment,
    COUNT(*) AS prediction_count,
    ROUND(
        AVG(prediction_confidence),
        4
    ) AS avg_confidence,
    ROUND(
        MIN(prediction_confidence),
        4
    ) AS min_confidence,
    ROUND(
        MAX(prediction_confidence),
        4
    ) AS max_confidence
FROM reviews
GROUP BY predicted_sentiment
ORDER BY predicted_sentiment;


-- ============================================================
-- 12. SENTIMENT OVER TIME
-- ============================================================

SELECT
    DATE_TRUNC(
        'year',
        review_date
    ) AS review_year,
    actual_sentiment,
    COUNT(*) AS review_count
FROM reviews
WHERE review_date IS NOT NULL
GROUP BY
    review_year,
    actual_sentiment
ORDER BY
    review_year,
    actual_sentiment;