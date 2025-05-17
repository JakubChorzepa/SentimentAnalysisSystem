from transformers import pipeline
from dotenv import load_dotenv
import os
from huggingface_hub import login
from confluent_kafka import Consumer, KafkaError, KafkaException
import json

load_dotenv("../.env")


login(
  token=os.getenv('HF_TOKEN'),
)

#sentiment_analyzer = pipeline(
#  "text-classification",
#  model="mental/mental-bert-base-uncased",
#  return_all_scores=True,
#  token=os.getenv('HF_TOKEN'),
#)

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'sentiment-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)

if __name__ == "__main__":
  try:
    consumer.subscribe(['reddit-mental-health-posts'])
    print("Consumer started, waiting for messages...")
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                raise KafkaException(msg.error())
        else:
            post_data = json.loads(msg.value())
            print(f"Received message: {post_data}")
            # sentiment = sentiment_analyzer(post_data['text'])
            # print(f"Sentiment: {sentiment}")
  finally:
        consumer.close()