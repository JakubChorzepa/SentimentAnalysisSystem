from transformers import pipeline
from dotenv import load_dotenv
import os
from huggingface_hub import login
from confluent_kafka import Consumer, KafkaError, KafkaException
import json

load_dotenv("../.env")

class SentimentAnalyzer:
    def __init__(self):
        self._initialize_huggingface()
        self.pipeline = self._create_pipeline()

    @staticmethod
    def _initialize_huggingface():
        login(token=os.getenv('HF_TOKEN'))

    @staticmethod
    def _create_pipeline():
        return pipeline(
            "sentiment-analysis",
            model="finiteautomata/bertweet-base-sentiment-analysis",
            top_k=None,
            truncation=True,
            max_length=128,
        )

    def analyze(self, text):
        result = self.pipeline(text)
        return result[0]

class KafkaConsumer:
    def __init__(self, conf, topic):
        self.consumer = Consumer(conf)
        self.topic = topic
        self.running = False

    def start_consuming(self, process_callback):
        self.consumer.subscribe([self.topic])
        self.running = True
        print("Consumer started, waiting for messages...")
        
        while self.running:
            msg = self.consumer.poll(1.0)
            
            if msg is None:
                continue
                
            if msg.error():
                self._handle_error(msg.error())
                continue
                
            try:
                post_data = json.loads(msg.value())
                process_callback(post_data)
            except json.JSONDecodeError as e:
                print(f"Błąd dekodowania JSON: {e}")
            except Exception as e:
                print(f"Błąd przetwarzania: {e}")

    def _handle_error(self, error):
        if error.code() == KafkaError._PARTITION_EOF: 
            print("Koniec partii")
            return
        raise KafkaException(error)

    def stop(self):
        self.running = False
        self.consumer.close()

def process_message(sentiment_analyzer):
    def wrapper(post_data):
        print(f"Odebrano wiadomość: {post_data}")

        if 'text' not in post_data:
            print("Brak pola 'text' w wiadomości")
            return
            
        try:
            sentiment_result = sentiment_analyzer.analyze(post_data['text'])
            
            print(f"Wynik analizy: {sentiment_result}")

            top_sentiment = sentiment_result[0]

            post_data['label'] = top_sentiment['label']
            post_data['score'] = top_sentiment['score']
            print(f"Wynik analizy: {post_data['label']} {post_data['score']}")
            
        except Exception as e:
            print(f"Błąd analizy: {e}")
    
    return wrapper

if __name__ == "__main__":
    sentiment_analyzer = SentimentAnalyzer()
    
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'sentiment-group-v3',
        'auto.offset.reset': 'earliest'
    }

    consumer = KafkaConsumer(conf, 'reddit-mental-health-posts')
    
    try:
        consumer.start_consuming(process_message(sentiment_analyzer))
    except KeyboardInterrupt:
        print("\nZatrzymywanie konsumenta...")
    finally:
        consumer.stop()
        print("Konsument zatrzymany.")