from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, TimestampType

# Initialize Spark session
spark = SparkSession.builder \
    .appName("KafkaToPostgres_FakeNews") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.5,org.postgresql:postgresql:42.7.5") \
    .getOrCreate()

# Kafka Config
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "fake_news_stream"

# Kafka message schema (no ID column now)
schema = StructType([
    StructField("type", StringType(), True),
    StructField("source", StringType(), True),
    StructField("author", StringType(), True),
    StructField("title", StringType(), True),
    StructField("content", StringType(), True),
    StructField("published_date", TimestampType(), True),
    StructField("url", StringType(), True),
    StructField("platform", StringType(), True),
    StructField("predictions", StringType(), True)
])

# Read stream from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

# Parse JSON from Kafka
df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Function to write each batch to PostgreSQL
def write_to_postgres(batch_df, batch_id):
    print(f"✅ Writing batch {batch_id}")
    try:
        batch_df.write \
            .format("jdbc") \
            .option("url", "jdbc:postgresql://localhost:5432/text_streams_db") \
            .option("dbtable", "result_text_streams") \
            .option("user", "<your_username>") \
            .option("password", "<your_password>") \
            .option("driver", "org.postgresql.Driver") \
            .mode("append") \
            .save()
        print("✅ Batch saved to result_text_streams!")
    except Exception as e:
        print(f"❌ Failed to write batch {batch_id}: {e}")

# Start streaming
df.writeStream \
    .foreachBatch(write_to_postgres) \
    .outputMode("append") \
    .start() \
    .awaitTermination()
