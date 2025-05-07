import sys
from transformers import pipeline

# Pobierz tekst z argumentu
text = sys.argv[1] if len(sys.argv) > 1 else ""

if text:
    # Analiza sentymentu
    model = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')
    result = model(text[:512])[0]  # Model obsługuje max 512 tokenów
    
    print(f"""
    ===== ANALIZA SENTYMENTU =====
    Tekst: {text[:100]}... 
    Sentiment: {result['label'].upper()}
    Pewność: {result['score']:.2f}
    """)
else:
    print("Brak tekstu do analizy!")