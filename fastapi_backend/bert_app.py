from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from databases import Database

import torch
import joblib
import numpy as np
from transformers import DistilBertTokenizerFast, DistilBertModel

# ---- Device Setup ----
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---- Load BERT & XGBoost ----
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
bert_model = DistilBertModel.from_pretrained("distilbert-base-uncased").to(device)
bert_model.eval()

xgb_model = joblib.load("xgboost_fake_news.pkl")

# ---- FastAPI Init ----
app = FastAPI()

# ---- Database Config ----
DATABASE_URL = "postgresql+asyncpg://postgres:i@sql60@localhost:5432/text_streams_db"
database = Database(DATABASE_URL)

# ---- Schema ----
class NewsItem(BaseModel):
    type: Optional[str] = None
    source: Optional[str] = None
    author: Optional[str] = None
    title: str
    content: str
    published_date: Optional[datetime] = None
    url: Optional[str] = None
    platform: Optional[str] = None
    predictions: Optional[str] = None

# ---- BERT Embedding ----
def get_embedding(text: str):
    with torch.no_grad():
        encoded = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512).to(device)
        outputs = bert_model(**encoded)
        cls_embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
    return cls_embedding

# ---- Events ----
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# ---- Health Check ----
@app.get("/health")
async def health():
    return {"status": "✅ Service is running"}

# ---- Single Prediction ----
@app.post("/predict")
async def predict(news: NewsItem):
    full_text = (news.title or "") + " " + (news.content or "")
    embedding = get_embedding(full_text)
    probs = xgb_model.predict_proba(embedding)[0]
    confidence = max(probs)

    label = "fake" if confidence > 0.80 else "real"
    news.predictions = label

    query = """
        INSERT INTO result_text_streams (
            type, source, author, title, content,
            published_date, url, platform, predictions
        ) VALUES (
            :type, :source, :author, :title, :content,
            :published_date, :url, :platform, :predictions
        )
    """
    await database.execute(query=query, values=news.dict(exclude_unset=True))

    return {"prediction": label, "confidence": round(float(confidence), 4)}

# ---- Bulk Prediction ----
@app.post("/bulk_predict")
async def bulk_predict(news_items: List[NewsItem] = Body(...)):
    results = []

    query = """
        INSERT INTO result_text_streams (
            type, source, author, title, content,
            published_date, url, platform, predictions
        ) VALUES (
            :type, :source, :author, :title, :content,
            :published_date, :url, :platform, :predictions
        )
    """

    for news in news_items:
        full_text = (news.title or "") + " " + (news.content or "")
        embedding = get_embedding(full_text)
        probs = xgb_model.predict_proba(embedding)[0]
        confidence = max(probs)

        label = "fake" if confidence > 0.80 else "real"
        news.predictions = label

        # ✅ Only insert if title + content exists
        if news.title and news.content:
            await database.execute(query=query, values=news.dict())

            results.append({
                "title": news.title,
                "prediction": label,
                "confidence": round(float(confidence), 4)
            })

    return results
