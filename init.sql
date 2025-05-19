-- Initialize table for storing mental health posts

CREATE TABLE IF NOT EXISTS mental_health_posts (
  id VARCHAR(50) PRIMARY KEY,
  title TEXT NOT NULL,
  text TEXT NOT NULL,
  subreddit VARCHAR(100),
  created_utc TIMESTAMP,
  sentiment_label VARCHAR(20),
  sentiment_score FLOAT,
  analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)