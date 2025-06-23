from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import asyncio, httpx, re
from bs4 import BeautifulSoup
import spacy
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk_download  # ensure this runs
import nltk


nltk.download("vader_lexicon")


import spacy
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import os
    os.system("python3 -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

sid = SentimentIntensityAnalyzer()

app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReviewRequest(BaseModel):
    url: str

@app.post("/api/review")
async def extract_review_data(payload: ReviewRequest):
    product_url = payload.url
    product_name = extract_title_from_url(product_url)
    review_sources = await search_review_sites(product_name)

    reviews = await fetch_all_reviews(review_sources)
    consolidated = consolidate_reviews(reviews)

    categorized = categorize_sentiment(consolidated)
    enhancements = extract_enhancements(consolidated)

    top_sources = review_sources[:5]

    return {
        "enhancements": enhancements,
        "categories": categorized,
        "sources": top_sources,
    }

@app.get("/api/review")
def read_only_warning():
    return {"message": "Please use POST method to submit product URL"}

def extract_title_from_url(url: str) -> str:
    slug = re.sub(r"https?://|www\.|\.com.*", "", url)
    parts = slug.split("/")
    return " ".join([p.replace("-", " ") for p in parts if p])

async def search_review_sites(product_name: str):
    # Simulated search results
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
                text = soup.get_text(separator=" ", strip=True)
                return text[:5000]
            except Exception:
                return ""
    return await asyncio.gather(*(fetch(site) for site in sites))

def consolidate_reviews(raw_reviews):
    return " ".join(filter(None, raw_reviews))

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
