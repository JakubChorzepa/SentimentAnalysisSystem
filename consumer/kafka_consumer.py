import json
from confluent_kafka import Consumer, KafkaError, KafkaException
from time import sleep

"""
  KafkaConsumer class for consuming messages from a Kafka topic.
  This class handles the connection to the Kafka broker, subscribes to a specified topic,
  and processes incoming messages using a provided callback function.
"""

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
                print(f"Error converting JSON: {e}")
            except Exception as e:
                print(f"Error converting: {e}")

    def _handle_error(self, error):
        if error.code() == KafkaError._PARTITION_EOF: 
            print("End of partition reached")
            return
        if error.code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
            print("Topic or partition not found yet, continuing to poll...")
        else:
          raise KafkaException(error)

    def stop(self):
        self.running = False
        self.consumer.close()