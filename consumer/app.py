from dotenv import load_dotenv
import os
from kafka_consumer import KafkaConsumer
from sentiment_analyzer import SentimentAnalyzer
from postgres_client import PostgresClient

load_dotenv("../.env")


def create_callback(sentiment_analyzer, postgres_client):
    def process_message(post_data):
        print(f"Received message: {post_data}")

        if 'text' not in post_data:
            print("No text field in post data")
            return
            
        try:
            sentiment_result = sentiment_analyzer.analyze(post_data['text'])
            
            print(f"Analysis result: {sentiment_result}")

            top_sentiment = sentiment_result[0]

            post_data['label'] = top_sentiment['label']
            post_data['score'] = top_sentiment['score']

            postgres_client.insert_post(post_data)
            
        except Exception as e:
            print(f"Analysis error : {e}")
    
    return process_message

if __name__ == "__main__":
    hf_token = os.getenv("HF_TOKEN")
    sentiment_analyzer = SentimentAnalyzer(hf_token)
    KAFKA_TOPIC = 'reddit-mental-health-posts'
    
    kafka_conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'mental-health-consumer',
        'auto.offset.reset': 'earliest'
    }

    postgres_conf = {
        'host': 'localhost',
        'database': 'reddit_db',
        'user': 'reddit_user',
        'password': 'reddit_pass',
        'port': 5440
    }

    consumer = KafkaConsumer(kafka_conf, KAFKA_TOPIC)
    postgres_client = PostgresClient(**postgres_conf)
    processor = create_callback(sentiment_analyzer, postgres_client)
    
    try:
        consumer.start_consuming(processor)
    except KeyboardInterrupt:
        print("\nZatrzymywanie konsumenta...")
    finally:
        consumer.stop()
        postgres_client.close()
        print("Konsument zatrzymany.")