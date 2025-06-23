
# Product Review API

This FastAPI service scrapes product reviews from the web, analyzes sentiment, and returns enhancement insights.

## Setup

```bash
pip install -r requirements.txt
python nltk_download.py
python -m spacy download en_core_web_sm
uvicorn main:app --reload

product-review-ui/
├── public/
│   └── index.html
├── src/
│   ├── App.jsx         ✅ (core app logic)
│   ├── index.js        ✅ (React entry point)
│   └── components/
│       └── ui/         ✅ (UI components if using shadcn/ui or Tailwind)
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── vite.config.js
└── README.md
