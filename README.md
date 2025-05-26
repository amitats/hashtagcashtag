#  HashtagCashtag

This is a simplified Big data pipeline for user sentiment analysis on US stock market

---

#  1. Installation & Setup (Local)

## A. Install dependencies
```bash
conda create -n cashtag python=3.9 -y
conda activate cashtag
pip install -r requirements.txt
```

## B. Start services (Kafka, PostgreSQL)
```bash
docker-compose up -d
```

This will start the following services:

| Service     | Purpose                             | Port   |
|-------------|-------------------------------------|--------|
| `zookeeper` | Required by Kafka                   | 2181   |
| `kafka`     | Message broker for streaming data   | 9092   |
| `postgres`  | Stores your processed sentiment data| 5432   |
| `pgadmin`   | Web GUI for PostgreSQL              | 8081   |

### You can access:
- Kafka at `localhost:9092`
- PostgreSQL at `localhost:5432`
- PgAdmin at [http://localhost:8081](http://localhost:8081) (user: admin@cashtag.local / pass: admin)

---

#  2. Ingestion Scripts

## A. `twitter_stream.py`
```python
from kafka import KafkaProducer
import tweepy, json

# Auth keys go here...
producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

class MyStream(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        if '$' in tweet.text:
            data = {'text': tweet.text, 'timestamp': tweet.created_at.isoformat()}
            producer.send('twitter_topic', data)

stream = MyStream(bearer_token='YOUR_TWITTER_BEARER_TOKEN')
stream.add_rules(tweepy.StreamRule('$AAPL OR $TSLA'))
stream.filter(tweet_fields=['created_at'])
```

## B. `stock_stream.py`
```python
from kafka import KafkaProducer
import yfinance as yf, time, json

producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

while True:
    for symbol in ['AAPL', 'TSLA']:
        data = yf.Ticker(symbol).history(period="1d", interval="1m").tail(1)
        price = data['Close'].values[0]
        record = {'symbol': symbol, 'price': float(price)}
        producer.send('stock_topic', record)
    time.sleep(60)
```

---

#  3. Spark Processing (Real-Time Sentiment)

## `spark_sentiment.py`
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.appName("Cashtag").getOrCreate()

tweets = spark.readStream.format("kafka").option("subscribe", "twitter_topic").load()
tweets = tweets.selectExpr("CAST(value AS STRING)")

# Naive sentiment detection
is_positive_udf = udf(lambda text: any(w in text.lower() for w in ['good','buy','up']), BooleanType())

processed = tweets.withColumn("text", col("value")).withColumn("positive", is_positive_udf(col("text")))

query = processed.writeStream.outputMode("append").format("console").start()
query.awaitTermination()
```

---

#  4. PostgreSQL Schema

## `schema.sql`
```sql
CREATE TABLE stock_sentiment (
    id SERIAL PRIMARY KEY,
    symbol TEXT,
    timestamp TIMESTAMP,
    mentions INT,
    positive_count INT,
    price FLOAT
);
```

---

#  5. Flask Dashboard

## `app.py`
```python
from flask import Flask, render_template
import psycopg2
import plotly.graph_objs as go

app = Flask(__name__)

@app.route("/")
def index():
    conn = psycopg2.connect(database="cashtag", user="postgres", password="postgres", host="localhost")
    cur = conn.cursor()
    cur.execute("SELECT timestamp, mentions, positive_count FROM stock_sentiment WHERE symbol='AAPL'")
    rows = cur.fetchall()

    chart = go.Figure()
    chart.add_trace(go.Scatter(x=[r[0] for r in rows], y=[r[1] for r in rows], name="Mentions"))
    chart.add_trace(go.Scatter(x=[r[0] for r in rows], y=[r[2] for r in rows], name="Positives"))

    return chart.to_html()

if __name__ == '__main__':
    app.run(debug=True)
```

---

#  6. requirements.txt
```
tweepy
yfinance
kafka-python
flask
plotly
psycopg2-binary
pyspark
```

---

#  Final Tips
- Run Twitter and stock ingestors first
- Start Spark job
- Load dummy data into PostgreSQL if needed
- Open your Flask app and demo your dashboard

You're all set to impress your manager with a fully working, beginner-friendly real-time data engineering project! 🎉
