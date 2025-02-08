import requests
import pandas as pd
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from scipy.special import softmax
import numpy as np

API_KEY = "pub_6830389454d2be3370f4b9fd5786223c9d6ad"
BASE_URL = "https://newsdata.io/api/1/news"
MODEL_NAME = "yiyanghkust/finbert-tone"

tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = BertForSequenceClassification.from_pretrained(MODEL_NAME)

def fetch_news(company: str):
    params = {
        "apikey": API_KEY,
        "q": company,
        "country": "in",
        "language": "en"
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    news_list = []
    for article in data.get("results", []):
        title = article.get("title", "")
        description = article.get("description", "")
        news_text = (title if title else "") + " " + (description if description else "")
        news_list.append((news_text.strip(), title))  # Store title for reason
    
    return news_list

def analyze_sentiment(news_list):
    scores = []
    reasons = []
    
    for news, title in news_list:
        inputs = tokenizer(news, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs).logits

        probabilities = softmax(outputs.numpy()[0])
        
        negative, neutral, positive = probabilities
        sentiment_score = (positive - negative) * 10  # Increased scale factor
        
        # Debugging output
        print(f"\nNews: {news[:100]}...")  # Show first 100 chars of news
        print(f"Sentiment Probabilities -> Negative: {negative:.4f}, Neutral: {neutral:.4f}, Positive: {positive:.4f}")
        print(f"Calculated Sentiment Score: {sentiment_score:.4f}")
        
        scores.append(sentiment_score)
        reasons.append((sentiment_score, title))

    avg_score = np.mean(scores) if scores else 0
    return avg_score, reasons

def estimate_impact(sentiment_score):
    if sentiment_score < -0.5:
        return round(sentiment_score * 2, 2)  # Increased impact scale
    elif sentiment_score > 0.5:
        return round(sentiment_score * 2, 2)  # Increased impact scale
    else:
        return round(sentiment_score * 1, 2)  # Reduce neutral threshold effect

def get_stock_news_impact(company: str):
    news_list = fetch_news(company)
    if not news_list:
        print("No news found for this company.")
        return 0, [("No news found", "Neutral")]

    sentiment_score, reasons = analyze_sentiment(news_list)
    impact = estimate_impact(sentiment_score)
    
    # Debugging output
    print(f"\n===== Final Impact Calculation =====")
    print(f"Company: {company}")
    print(f"Average Sentiment Score: {sentiment_score:.4f}")
    print(f"Predicted Impact: {impact}%\n")

    return impact, reasons

if __name__ == "__main__":
    company_name = input("Enter company name: ")
    impact, reasons = get_stock_news_impact(company_name)
    print(f"\nPredicted news impact on {company_name}: {impact}%")
    print("\nReasons for impact:")
    for score, reason in reasons:
        sentiment = "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"
        print(f"- [{sentiment}] {reason}")
