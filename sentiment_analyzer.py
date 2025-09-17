# sentiment_analyzer.py
import re
from transformers import pipeline

# --- Model Initialization ---
# This initializes the pre-trained model and tokenizer.
# It will be downloaded from Hugging Face the first time it's run.
# We use a specific model fine-tuned on millions of tweets for high accuracy.
print("Loading sentiment analysis model (this may take a moment)...")
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    token=False  # <-- Add this line
)
print("✅ Model loaded successfully.")


def preprocess_tweet(text: str) -> str:
    """Cleans tweet text by removing URLs and user mentions."""
    # Remove user mentions (@username)
    text = re.sub(r'@\w+', '', text)
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    # Replace common HTML entities
    text = text.replace('&amp;', 'and').replace('&gt;', '>').replace('&lt;', '<')
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text


def classify_sentiment(text: str) -> str:
    """
    Classifies the sentiment of a given text using a transformer model.
    Returns 'Positive', 'Negative', or 'Neutral'.
    """
    if not text:
        return 'Neutral'

    # 1. Clean the tweet text for better model performance
    cleaned_text = preprocess_tweet(text)

    # 2. The pipeline returns a list of dictionaries, e.g., [{'label': 'positive', 'score': 0.9...}]
    result = sentiment_pipeline(cleaned_text)
    
    # 3. We extract the label and capitalize it to match our existing system's output
    # ('positive' -> 'Positive')
    label = result[0]['label'].capitalize()
    
    return label