from confluent_kafka import Producer
import praw
import os
import time
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv("../.env")

reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent='SentimentAnalysis',
)

conf = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'reddit-producer'
}

producer = Producer(**conf)
topic_name = 'reddit-mental-health-posts'

def generate_datetime_now():
    return datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')

def delivery_report(err, msg):
    if err is not None:
        print(f'{generate_datetime_now()} Message delivery failed: {err}') 
    else:
        print(f'{generate_datetime_now()} Message delivered to {msg.topic()} [{msg.partition()}]')


def stream_reddit_posts():
    TEXT_CONTENT_MIN_LENGTH = 20
    watched_subreddits_list = ['MentalHealth', 'MentalHealthUK', 'depression', 'anxiety', 'mentalillness', 'socialanxiety', 'MentalHealthSupport', 'bipolar', 'BPD']
    print(f"{generate_datetime_now()} Watching subreddits: {watched_subreddits_list}")
    subreddits = reddit.subreddit('+'.join(watched_subreddits_list))
    for submission in subreddits.stream.submissions(skip_existing=True):
        if len(submission.selftext) < TEXT_CONTENT_MIN_LENGTH:
            continue

        post_data = {
            'id': submission.id,
            'title': submission.title,
            'text': submission.selftext,
            'created_utc': submission.created_utc,
            'subreddit': submission.subreddit.display_name
        }

        print(f'{generate_datetime_now()} Producing message: {post_data}')

        producer.produce(
            topic_name,
            key=submission.id.encode('utf-8'),
            value=json.dumps(post_data).encode('utf-8'),
            callback=delivery_report
        )
        
        producer.poll(0)


if(__name__ == '__main__'):
    while True:
        try:
            stream_reddit_posts()
        except Exception as e:
            print(f"{generate_datetime_now()} Error: {e}")
            time.sleep(5)
        finally:
            producer.flush()