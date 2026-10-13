"""
01
# kafka_stream.py


"""
 
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    DoubleType,
    TimestampType,
)

# Keep the checkpoint in this project's folder.
checkpoint_dir = Path("checkpoints/kafka-device-events").resolve()
checkpoint_dir.mkdir(parents=True, exist_ok=True)

spark = (
    SparkSession.builder
    .appName("KafkaDeviceEvents")
    .master("local[*]")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

event_schema = StructType([
    StructField("device_id", StringType(), nullable=True),
    StructField("event_time", TimestampType(), nullable=True),
    StructField("temperature", DoubleType(), nullable=True),
])

raw_events = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "device-events")
    .option("startingOffsets", "latest")
    .load()
)

events = (
    raw_events
    .select(from_json(col("value").cast("string"), event_schema).alias("event"))
    .select("event.*")
    .where(col("device_id").isNotNull())
)

query = (
    events.writeStream
    .format("console")
    .outputMode("append")
    .option("truncate", "false")
    .option("checkpointLocation", checkpoint_dir.as_uri())
    .trigger(processingTime="10 seconds")
    .start()
)

query.awaitTermination()