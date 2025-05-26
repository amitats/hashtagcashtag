import tweepy
from kafka import KafkaProducer
import json

# Auth
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)

# Producer
producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Stream
class MyStream(tweepy.Stream):
    def on_status(self, status):
        tweet = {
            'text': status.text,
            'user': status.user.screen_name,
            'timestamp': str(status.created_at)
        }
        producer.send('twitter_topic', tweet)

stream = MyStream(api_key, api_secret, access_token, access_token_secret)
stream.filter(track=['$AAPL', '$TSLA', '$AMZN'])
