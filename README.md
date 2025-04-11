# 🚨 Real-Time AI Fake News Detection System  
[![Status](https://img.shields.io/badge/Status-Completed-brightgreen)](#)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue)](https://www.apache.org/licenses/LICENSE-2.0)
[![Python](https://img.shields.io/badge/Python-3.8%2B-yellow)](https://www.python.org/)

A scalable, end-to-end real-time fake news detection pipeline powered by Apache Kafka, Apache Spark Streaming, PostgreSQL, FastAPI, Streamlit, and Hugging Face Transformers. This project detects fake or real news from streaming sources in real time and stores predictions in a cloud/local database for downstream analysis.


---  

## 📌 Table of Contents  
- ⚙️ Architecture  
- 🧠 ML Model  
- 🚀 Pipeline Flow  
- 🛠️ Tech Stack  
- 📁 Project Structure  
- 📦 Setup & Run  
- 📡 REST API for Prediction  
- 📊 Results & Insights  
- 📎 Related Links  

---  

## ⚙️ Architecture  

- A[Kafka Producer] --> B[Kafka Topic: news_data]
- B --> C[Spark Structured Streaming]
- C --> D[FastAPI Model Endpoint]
- D --> E[Prediction: Fake or Real]
- E --> F[PostgreSQL Database]
- F --> G[Superset Dashboard]

---  

## 🧠 ML Model
- **Base Model:** DistilBERT (Hugging Face Transformers)  
- **Feature Fusion:** TF-IDF + BERT embeddings  
- **Classifier:** XGBoostClassifier  
- **Training:** Local Jupyter Notebook (notebooks/training.ipynb)  
- **Deployment:** FastAPI + Streamlit + Hugging Face Spaces  

---

## 🚀 Pipeline Flow
- 📰 News content is streamed into **Kafka topic**  
- 🔥 **PySpark consumer** reads the stream  
- 🧠 **FastAPI** endpoint makes prediction (real/fake)  
- 🧾 Result is written to **PostgreSQL** (result_text_streams)  
- 🎯 Data is visualized via **Streamlit App** and **Superset Dashboard**  

---

## 🛠️ Tech Stack  

- **Python** (NLTK, Scikit-learn, Transformers, Pandas)  
- **Apache Kafka** (Streaming news data)  
- **Apache Spark** Structured Streaming  
- **FastAPI** (Model API)  
- **PostgreSQL** (Local storage)  
- **Streamlit** (Frontend for real-time results)  
- **Apache Superset** (Analytics Dashboard)  
- **Docker** (Kafka setup)  
- **Hugging Face Hub** (Model hosting)

---

## 📁 Project Structure  

AI-Real-Time-Fake-News-Detection/  
├── notebooks/  
│   └── training.ipynb  
├── kafka_streaming/  
│   ├── producer.py  
│   └── consumer_spark.py  
├── fastapi_backend/  
│   ├── main.py  
│   ├── model/  
│   │   └── saved_fake_news_model/  
│   │       ├── bert/  
│   │       ├── vectorizer.pkl  
│   │       └── classifier.pkl  
├── superset_charts/  
│   └── chart_configs.json  
├── data/  
│   └── sample_text_data.json  
├── Dockerfile  
├── requirements.txt  
├── README.md  
└── .gitignore  

---

## 📡 REST API for Prediction  

- Endpoint URL: http://your-fastapi-endpoint/predict  
- Sample Payload:  
  {  
  "type": "news",  
  "source": "Example News",  
  "author": "John Doe",  
  "title": "Breaking: Something unbelievable happened",  
  "content": "This just in, something truly astonishing occurred...",  
  "published_date": "2025-04-10",  
  "url": "https://example.com/article",  
  "platform": "Twitter"  
}  

- Response :  
  
{
  "prediction": "fake",  
  "confidence": 0.91  
}  

---

## 📊 Results & Insights  

- ✅ Accuracy: ~93% on test set  
- 🧠 Real-time prediction latency: ~250ms  
- ⚡ High throughput with Spark Streaming  
- 📈 Superset dashboards with 6 key visualizations

---

## 📎 Related Links  

- Hugging Face Model Repo  
- Streamlit App on HF Spaces  
- Kafka in Docker Setup  
- Spark Streaming Script  
- FastAPI Endpoint  
- Superset Dashboard Setup  

