from dotenv import load_dotenv
import os
from kafka_consumer import KafkaConsumer
from sentiment_analyzer import SentimentAnalyzer

load_dotenv("../.env")


def create_callback(sentiment_analyzer):
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

    consumer = KafkaConsumer(kafka_conf, KAFKA_TOPIC)
    processor = create_callback(sentiment_analyzer)
    
    try:
        consumer.start_consuming(processor)
    except KeyboardInterrupt:
        print("\nZatrzymywanie konsumenta...")
    finally:
        consumer.stop()
        print("Konsument zatrzymany.")