
# Product Review API

This FastAPI service scrapes product reviews from the web, analyzes sentiment, and returns enhancement insights.

## Setup

```bash
pip install -r requirements.txt
python nltk_download.py
python -m spacy download en_core_web_sm
uvicorn main:app --reload
