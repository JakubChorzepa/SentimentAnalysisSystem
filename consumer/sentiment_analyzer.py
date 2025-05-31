from huggingface_hub import login
from transformers import pipeline

"""
  SentimentAnalyzer is a class that initializes a sentiment analysis pipeline using Hugging Face's Transformers library.
  It uses the 'finiteautomata/bertweet-base-sentiment-analysis' model for sentiment analysis.
  The class provides a method to analyze the sentiment of a given text input.
"""

class SentimentAnalyzer:
    def __init__(self, hf_token):
        self.hf_token = hf_token
        self._initialize_huggingface(self.hf_token)
        self.pipeline = self._create_pipeline()

    @staticmethod
    def _initialize_huggingface(hf_token):
        login(hf_token)

    @staticmethod
    def _create_pipeline():
        return pipeline(
            "sentiment-analysis",
            model="waimoe/mental-health-sentiment-analysis-model",
            top_k=None,
            truncation=True,
            max_length=1024,
        )

    def analyze(self, text):
        result = self.pipeline(text)
        return result[0]