# from confluent_kafka import Producer
import praw
import subprocess
import os
import time
from dotenv import load_dotenv

load_dotenv("../.env")

reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent='SentimentAnalysis',
)


def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

subreddit = reddit.subreddit('politics+trump+news+gaming+funny')


if(__name__ == '__main__'):
    for post in subreddit.stream.submissions(skip_existing=True):
        post_data = {
            'id': post.id,
            'title': post.title,
            'text': post.selftext,
            'author': str(post.author),
            'created_utc': post.created_utc
        }

        text = post_data['text'] or post_data['title']

        print(f'Producing message: {post_data}')

        subprocess.run([
            'python3',
            '../consumer/app.py',
            text[:512]
        ])

        time.sleep(1)