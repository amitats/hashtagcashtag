from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.appName("CashtagApp").getOrCreate()

# Read tweets
tweets = spark.readStream.format("kafka").option("subscribe", "twitter_topic").load()
tweets = tweets.selectExpr("CAST(value AS STRING)").withColumn("text", col("value"))

# Basic sentiment classification
def is_positive(text):
    positive_words = ['good', 'buy', 'great', 'up']
    return any(word in text.lower() for word in positive_words)

from pyspark.sql.functions import udf
from pyspark.sql.types import BooleanType
is_positive_udf = udf(is_positive, BooleanType())

tweets = tweets.withColumn("positive", is_positive_udf(col("text")))

# Aggregate by symbol and time
tweets_grouped = tweets.groupBy(window(col("timestamp"), "10 minutes"), "symbol").agg(
    count("*").alias("mentions"),
    sum(col("positive").cast("int")).alias("positive_count")
)

# Write to PostgreSQL or Cassandra
tweets_grouped.writeStream.outputMode("update").format("console").start().awaitTermination()
