import asyncio
import json
import aiohttp
import asyncpg
from aiokafka import AIOKafkaConsumer

# Config
KAFKA_TOPIC = "fake_news_stream"
KAFKA_BOOTSTRAP = "localhost:9092"
FASTAPI_ENDPOINT = "http://localhost:8000/bulk_predict"
POSTGRES_URI = "postgresql://<username>:<password>@localhost:5432/text_streams_db"


# Async function to insert predictions into PostgreSQL
async def insert_predictions(pg_pool, predictions):
    async with pg_pool.acquire() as conn:
        for item in predictions:
            try:
                # Safely serialize predictions field
                prediction_data = item.get("predictions", {})
                if not isinstance(prediction_data, str):
                    prediction_data = json.dumps(prediction_data)

                await conn.execute("""
                    INSERT INTO result_text_streams 
                    (type, source, author, title, content, published_date, url, platform, predictions)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                item.get("type"),
                item.get("source"),
                item.get("author"),
                item.get("title"),
                item.get("content"),
                item.get("published_date"),
                item.get("url"),
                item.get("platform"),
                prediction_data
                )
            except Exception as e:
                print(f"❌ Error inserting item into DB: {e}")


# Main Kafka-to-FastAPI-to-Postgres loop
async def consume_and_process():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        enable_auto_commit=True,
        auto_offset_reset="latest"
    )
    await consumer.start()
    print("✅ Kafka consumer started...")

    pg_pool = await asyncpg.create_pool(POSTGRES_URI)
    print("✅ PostgreSQL pool created...")

    async with aiohttp.ClientSession() as session:
        try:
            batch = []
            last_send = asyncio.get_event_loop().time()

            while True:
                records = await consumer.getmany(timeout_ms=1000)

                for tp, msgs in records.items():
                    for msg in msgs:
                        batch.append(msg.value)

                now = asyncio.get_event_loop().time()

                if len(batch) >= 10 or (now - last_send > 5 and batch):
                    print(f"📤 Sending batch of {len(batch)} to FastAPI...")

                    try:
                        async with session.post(FASTAPI_ENDPOINT, json=batch) as resp:
                            if resp.status == 200:
                                predictions = await resp.json()

                                if isinstance(predictions, list):
                                    # await insert_predictions(pg_pool, predictions)
                                    print(f"✅ Inserted {len(predictions)} predictions into PostgreSQL")
                                else:
                                    print("❌ FastAPI response format invalid. Expected list.")
                            else:
                                print(f"❌ FastAPI returned status {resp.status}")
                    except Exception as e:
                        print(f"❌ Error calling FastAPI: {e}")

                    batch = []
                    last_send = now

        finally:
            await consumer.stop()
            await pg_pool.close()

# Run the async loop
if __name__ == "__main__":
    asyncio.run(consume_and_process())
