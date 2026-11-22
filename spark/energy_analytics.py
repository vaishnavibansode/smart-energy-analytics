
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, to_date, to_timestamp, concat_ws, lit,
    sum as spark_sum, avg, max as spark_max,
    count, date_format, desc, when
)
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType
)

# 1. Start Spark
spark = SparkSession.builder \
    .appName("SmartEnergyConsumptionAnalytics") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# 2. HDFS input and output locations
input_path = (
    "hdfs://localhost:9000/user/vaishnavi/"
    "smart-energy/processed/cleaned_energy/part-m-00000"
)

output_base = (
    "hdfs://localhost:9000/user/vaishnavi/"
    "smart-energy/analytics"
)

# 3. Define the cleaned dataset schema
schema = StructType([
    StructField("reading_date", StringType(), True),
    StructField("reading_time", StringType(), True),
    StructField("hour", StringType(), True),
    StructField("global_active_power", DoubleType(), True),
    StructField("global_reactive_power", DoubleType(), True),
    StructField("voltage", DoubleType(), True),
    StructField("global_intensity", DoubleType(), True),
    StructField("sub_metering_1", DoubleType(), True),
    StructField("sub_metering_2", DoubleType(), True),
    StructField("sub_metering_3", DoubleType(), True)
])

# 4. Read cleaned data from HDFS
df = spark.read \
    .option("sep", "\t") \
    .schema(schema) \
    .csv(input_path)

# 5. Prepare analytical columns
df = df.withColumn(
    "date",
    to_date(col("reading_date"), "d/M/yyyy")
)

df = df.withColumn(
    "timestamp",
    to_timestamp(
        concat_ws(" ", col("reading_date"), col("reading_time")),
        "d/M/yyyy HH:mm:ss"
    )
)

# One reading represents one minute.
# Convert average power in kW into energy in kWh.
df = df.withColumn(
    "energy_kwh",
    col("global_active_power") / 60.0
)

df = df.withColumn(
    "month",
    date_format(col("date"), "yyyy-MM")
)

# Remove invalid parsed dates
df = df.filter(col("date").isNotNull())

# 6. Basic dataset statistics
print("\n========== DATASET SUMMARY ==========")
print("Total valid records:", df.count())
df.select(
    avg("global_active_power").alias("average_power_kw"),
    spark_max("global_active_power").alias("maximum_power_kw"),
    avg("voltage").alias("average_voltage")
).show(truncate=False)

# 7. Hourly consumption analysis
hourly = df.groupBy("date", "hour").agg(
    spark_sum("energy_kwh").alias("energy_kwh"),
    avg("global_active_power").alias("average_power_kw"),
    spark_max("global_active_power").alias("peak_power_kw"),
    count("*").alias("readings")
).orderBy("date", "hour")

hourly.write.mode("overwrite") \
    .option("header", True) \
    .csv(output_base + "/hourly")

# 8. Daily consumption analysis
daily = df.groupBy("date").agg(
    spark_sum("energy_kwh").alias("daily_energy_kwh"),
    avg("global_active_power").alias("average_power_kw"),
    spark_max("global_active_power").alias("peak_power_kw"),
    count("*").alias("readings")
).orderBy("date")

daily.write.mode("overwrite") \
    .option("header", True) \
    .csv(output_base + "/daily")

# 9. Monthly consumption analysis
monthly = df.groupBy("month").agg(
    spark_sum("energy_kwh").alias("monthly_energy_kwh"),
    avg("global_active_power").alias("average_power_kw"),
    spark_max("global_active_power").alias("peak_power_kw"),
    count("*").alias("readings")
).orderBy("month")

monthly.write.mode("overwrite") \
    .option("header", True) \
    .csv(output_base + "/monthly")


# 10. Daily Consumption Anomaly Detection using IQR

print("\n========== ANOMALY DETECTION ==========")

# Exclude incomplete days
full_days = daily.filter(col("readings") >= 1200)

# Calculate first and third quartiles
quartiles = full_days.approxQuantile(
    "daily_energy_kwh",
    [0.25, 0.75],
    0.01
)

q1 = quartiles[0]
q3 = quartiles[1]

iqr = q3 - q1

lower_bound = max(0, q1 - 1.5 * iqr)
upper_bound = q3 + 1.5 * iqr

print("Q1:", q1)
print("Q3:", q3)
print("IQR:", iqr)
print("Lower anomaly threshold:", lower_bound)
print("Upper anomaly threshold:", upper_bound)

# Identify unusually low and high consumption days
anomalies = full_days.filter(
    (col("daily_energy_kwh") < lower_bound) |
    (col("daily_energy_kwh") > upper_bound)
).withColumn(
    "anomaly_type",
    when(
        col("daily_energy_kwh") > upper_bound,
        lit("HIGH_CONSUMPTION")
    ).otherwise(
        lit("LOW_CONSUMPTION")
    )
).orderBy(desc("daily_energy_kwh"))

# Save anomaly results to HDFS
anomalies.write.mode("overwrite") \
    .option("header", True) \
    .csv(output_base + "/anomalies")

# Display detected anomalies
print("\nDetected anomalous days:")
anomalies.show(30, truncate=False)

print("Total anomalous days:", anomalies.count())
 
# 10. Top 20 peak-demand readings
peaks = df.select(
    "timestamp",
    "global_active_power",
    "global_intensity",
    "voltage"
).orderBy(desc("global_active_power")).limit(20)

peaks.write.mode("overwrite") \
    .option("header", True) \
    .csv(output_base + "/peak_demand")

# 11. Appliance-wise sub-metering analysis
appliance = df.agg(
    (spark_sum("sub_metering_1") / 1000.0).alias("meter_1_kwh"),
    (spark_sum("sub_metering_2") / 1000.0).alias("meter_2_kwh"),
    (spark_sum("sub_metering_3") / 1000.0).alias("meter_3_kwh")
)

appliance.write.mode("overwrite") \
    .option("header", True) \
    .csv(output_base + "/appliance")

# 12. Display sample results
print("\n========== HOURLY CONSUMPTION ==========")
hourly.show(10, truncate=False)

print("\n========== DAILY CONSUMPTION ==========")
daily.show(10, truncate=False)

print("\n========== MONTHLY CONSUMPTION ==========")
monthly.show(10, truncate=False)

print("\n========== TOP 20 PEAK DEMAND ==========")
peaks.show(20, truncate=False)

print("\n========== APPLIANCE CONSUMPTION ==========")
appliance.show(truncate=False)

print("\nAll analytical outputs saved successfully to HDFS.")

spark.stop()
