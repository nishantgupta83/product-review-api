from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import asyncio, httpx, re, subprocess
from bs4 import BeautifulSoup
import openai
import json
import os

import spacy
import nltk

try:
    nltk.data.find("sentiment/vader_lexicon")
except LookupError:
    nltk.download("vader_lexicon")

from nltk.sentiment.vader import SentimentIntensityAnalyzer
# Initialize VADER sentiment analyzer
sid = SentimentIntensityAnalyzer()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Load SpaCy model with fallback
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run(["python3", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# Initialize FastAPI
app = FastAPI()

# Allow all CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class ReviewRequest(BaseModel):
    url: str

# Main endpoint
@app.post("/api/review")
async def extract_review_data(payload: ReviewRequest):
    product_url = payload.url
    product_name = extract_title_from_url(product_url)
    review_sources = await fetch_reviews_from_serpapi(product_name)

    reviews = [r["snippet"] for r in review_sources if r.get("snippet")]
    text_blob = " ".join(reviews)

   # categorized = categorize_sentiment(text_blob)
    categorized = categorize_sentiment_llm(text_blob)
    enhancements = extract_enhancements(text_blob)

    return {
        "enhancements": enhancements,
        "categories": categorized,
        "sources": review_sources[:5],
    }

# GET handler (optional)
@app.get("/api/review")
def read_only_warning():
    return {"message": "Please use POST method to submit product URL"}

# Helpers
def extract_title_from_url(url: str) -> str:
    slug = re.sub(r"https?://|www\.|\.com.*", "", url)
    parts = slug.split("/")
    return " ".join([p.replace("-", " ") for p in parts if p])

async def search_review_sites(product_name: str):
    # Simulated search result URLs
    return [
        {"name": "Amazon", "url": f"https://www.amazon.com/s?k={product_name}"},
        {"name": "BestBuy", "url": f"https://www.bestbuy.com/site/searchpage.jsp?st={product_name}"},
        {"name": "Reddit", "url": f"https://www.reddit.com/search/?q={product_name}"},
        {"name": "YouTube", "url": f"https://www.youtube.com/results?search_query={product_name}+review"},
        {"name": "Blogs", "url": f"https://medium.com/search?q={product_name}"},
    ]

async def fetch_all_reviews(sites):
    async def fetch(site):
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(site["url"])
                soup = BeautifulSoup(response.text, "html.parser")
                return soup.get_text(separator=" ", strip=True)[:5000]
            except Exception as e:
                print(f"Error fetching {site['url']}: {e}")
                return ""
    return await asyncio.gather(*(fetch(site) for site in sites))

def consolidate_reviews(raw_reviews):
    return " ".join(filter(None, raw_reviews))
    
async def fetch_reviews_from_serpapi(query: str):
    SERPAPI_KEY = "5a6c447319fd3b6b30dc589acf74bc6a688745d78e5ec4a8cfdd72185d12a7eb"
    url = "https://serpapi.com/search.json"
    params = {
        "q": f"{query} reviews",
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "num": 10
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            results = resp.json().get("organic_results", [])
            return [
                {"name": r.get("title", ""), "url": r.get("link", ""), "snippet": r.get("snippet", "")}
                for r in results
            ]
    except Exception as e:
        print("SerpAPI error:", e)
        return []



def categorize_sentiment(text):
    categories = {
        "Product Functionality": ["feature", "bug", "performance", "hardware", "battery"],
        "User Experience": ["design", "interface", "navigation", "ease"],
        "Customer Support": ["support", "help", "service", "agent"],
        "Pricing and Value": ["price", "value", "cost", "worth"]
    }
    doc = nlp(text)
    results = {}

    for cat, keywords in categories.items():
        cat_sentences = [sent.text for sent in doc.sents if any(kw in sent.text.lower() for kw in keywords)]
        if cat_sentences:
            scores = [sid.polarity_scores(sent)["compound"] for sent in cat_sentences]
            avg_score = sum(scores) / len(scores)
            results[cat] = int((avg_score + 1) * 50)
        else:
            results[cat] = 50  # Neutral default

    return results
    
def categorize_sentiment_llm(text: str):
    prompt = f"""
You are an AI assistant analyzing customer product reviews. Based on the content below, return a JSON object with percentage scores (0-100) for the following categories:

- Product Functionality
- User Experience
- Customer Support
- Pricing and Value

Respond ONLY in this format:
{{
  "Product Functionality": 75,
  "User Experience": 85,
  "Customer Support": 60,
  "Pricing and Value": 70
}}

Text:
{text[:3000]}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300,
        )
        reply = response.choices[0].message.content
        return json.loads(reply)
    except Exception as e:
        print("OpenAI API error:", e)
        return categorize_sentiment(text)


def extract_enhancements(text):
    candidates = re.findall(r"(needs improvement|could be better|fails to|doesn’t work|wish it had.*?)\.", text, re.IGNORECASE)
    
    common = list(set([c.strip().capitalize() for c in candidates]))
    return common[:5] if common else [
        "Improve battery performance",
        "Reduce product weight",
        "Add more durability",
        "Refine physical design",
        "Enhance material quality"
    ]
