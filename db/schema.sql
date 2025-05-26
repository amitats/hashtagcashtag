CREATE TABLE stock_sentiment (
    id SERIAL PRIMARY KEY,
    symbol TEXT,
    timestamp TIMESTAMP,
    mentions INT,
    positive_count INT,
    price FLOAT
);
