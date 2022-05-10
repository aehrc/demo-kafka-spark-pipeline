#!/bin/python

appName = "Kafka, Spark and FHIR Data"
master = "spark://spark:7077"
kafka_topic = "fhir.post-gateway-kdb"

# https://engineering.cerner.com/bunsen/0.5.10-SNAPSHOT/
from pyspark.sql import SparkSession
from pathling.etc import find_jar
from pathling.r4 import bundles

if __name__ == "__main__":

    spark = SparkSession \
        .builder \
        .appName(appName) \
        .master(master) \
        .config('spark.jars', find_jar()) \
        .getOrCreate()

    df = spark \
        .readStream  \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka1:19092") \
        .option("subscribe", kafka_topic) \
        .option("startingOffsets", "earliest") \
        .load()

    df.printSchema()

    query = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
            .writeStream \
            .queryName("gettable")\
            .format("memory")\
            .start()

    # close connection after 15 seconds
    query.awaitTermination(15)

    kafka_data = spark.sql("select * from gettable")
    kafka_data.show()
    type(kafka_data)

    resources = bundles.from_json(kafka_data, 'value')
    patients = bundles.extract_entry(spark, resources, 'Patient')
    encounter = bundles.extract_entry(spark, resources, 'Encounter')
    condition = bundles.extract_entry(spark, resources, 'Condition')

    patients.toPandas()
    encounter.toPandas()
    condition.toPandas()
