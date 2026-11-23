from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType
)

# ============================================================
# 1. START SPARK SESSION
# ============================================================

spark = SparkSession.builder \
    .appName("SmartEnergySparkSQLAnalytics") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# ============================================================
# 2. HDFS INPUT AND OUTPUT PATHS
# ============================================================

input_path = (
    "hdfs://localhost:9000/user/vaishnavi/"
    "smart-energy/processed/cleaned_energy/part-m-00000"
)

output_base = (
    "hdfs://localhost:9000/user/vaishnavi/"
    "smart-energy/sql-results"
)

# ============================================================
# 3. DEFINE DATASET SCHEMA
# ============================================================

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

# ============================================================
# 4. READ CLEANED DATA FROM HDFS
# ============================================================

df = spark.read \
    .option("sep", "\t") \
    .schema(schema) \
    .csv(input_path)

# Prepare date and timestamp columns
from pyspark.sql.functions import (
    col, to_date, to_timestamp, concat_ws, date_format
)

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

df = df.withColumn(
    "hour_num",
    col("hour").cast("int")
)

df = df.withColumn(
    "month",
    date_format(col("date"), "yyyy-MM")
)

df = df.withColumn(
    "energy_kwh",
    col("global_active_power") / 60.0
)

df = df.filter(col("date").isNotNull())

# Register a temporary SQL view
df.createOrReplaceTempView("energy_data")

print("\n============================================")
print("       SPARK SQL ENERGY ANALYTICS")
print("============================================")

print("Total valid records:", df.count())

# ============================================================
# QUERY 1: HOURLY ELECTRICITY CONSUMPTION
# ============================================================

print("\n========== QUERY 1: HOURLY CONSUMPTION ==========")

hourly_sql = spark.sql("""
    SELECT
        hour_num AS hour,
        SUM(energy_kwh) AS total_energy_kwh,
        AVG(global_active_power) AS average_power_kw,
        MAX(global_active_power) AS peak_power_kw,
        COUNT(*) AS readings
    FROM energy_data
    GROUP BY hour_num
    ORDER BY hour_num
""")

hourly_sql.show(24, truncate=False)

# ============================================================
# QUERY 2: TOP 10 HIGHEST-CONSUMPTION DAYS
# ============================================================

print("\n========== QUERY 2: TOP 10 CONSUMPTION DAYS ==========")

daily_top_sql = spark.sql("""
    SELECT
        date,
        SUM(energy_kwh) AS daily_energy_kwh,
        AVG(global_active_power) AS average_power_kw,
        MAX(global_active_power) AS peak_power_kw,
        COUNT(*) AS readings
    FROM energy_data
    GROUP BY date
    HAVING COUNT(*) >= 1200
    ORDER BY daily_energy_kwh DESC
    LIMIT 10
""")

daily_top_sql.show(10, truncate=False)

# ============================================================
# QUERY 3: MONTHLY ELECTRICITY CONSUMPTION
# ============================================================

print("\n========== QUERY 3: MONTHLY CONSUMPTION ==========")

monthly_sql = spark.sql("""
    SELECT
        month,
        SUM(energy_kwh) AS monthly_energy_kwh,
        AVG(global_active_power) AS average_power_kw,
        MAX(global_active_power) AS peak_power_kw,
        COUNT(*) AS readings
    FROM energy_data
    GROUP BY month
    ORDER BY month
""")

monthly_sql.show(60, truncate=False)

# ============================================================
# QUERY 4: TOP 20 PEAK-DEMAND READINGS
# ============================================================

print("\n========== QUERY 4: PEAK DEMAND ==========")

peak_sql = spark.sql("""
    SELECT
        timestamp,
        global_active_power,
        global_intensity,
        voltage
    FROM energy_data
    ORDER BY global_active_power DESC
    LIMIT 20
""")

peak_sql.show(20, truncate=False)

# ============================================================
# QUERY 5: SUB-METERING ENERGY CONSUMPTION
# ============================================================

print("\n========== QUERY 5: SUB-METERING ANALYSIS ==========")

appliance_sql = spark.sql("""
    SELECT
        SUM(sub_metering_1) / 1000.0 AS meter_1_kwh,
        SUM(sub_metering_2) / 1000.0 AS meter_2_kwh,
        SUM(sub_metering_3) / 1000.0 AS meter_3_kwh
    FROM energy_data
""")

appliance_sql.show(truncate=False)

# ============================================================
# QUERY 6: DAILY ANOMALY DETECTION USING IQR
# ============================================================

print("\n========== QUERY 6: IQR ANOMALY DETECTION ==========")

anomaly_sql = spark.sql("""
    WITH daily_stats AS (
        SELECT
            date,
            SUM(energy_kwh) AS daily_energy_kwh,
            AVG(global_active_power) AS average_power_kw,
            MAX(global_active_power) AS peak_power_kw,
            COUNT(*) AS readings
        FROM energy_data
        GROUP BY date
    ),

    full_days AS (
        SELECT *
        FROM daily_stats
        WHERE readings >= 1200
    ),

    quartiles AS (
        SELECT
            percentile_approx(
                daily_energy_kwh, 0.25, 100
            ) AS q1,

            percentile_approx(
                daily_energy_kwh, 0.75, 100
            ) AS q3
        FROM full_days
    ),

    bounds AS (
        SELECT
            q1,
            q3,
            q3 - q1 AS iqr,
            GREATEST(0.0, q1 - 1.5 * (q3 - q1))
                AS lower_bound,
            q3 + 1.5 * (q3 - q1)
                AS upper_bound
        FROM quartiles
    )

    SELECT
        d.date,
        d.daily_energy_kwh,
        d.average_power_kw,
        d.peak_power_kw,
        d.readings,
        b.q1,
        b.q3,
        b.iqr,
        b.lower_bound,
        b.upper_bound,

        CASE
            WHEN d.daily_energy_kwh > b.upper_bound
                THEN 'HIGH_CONSUMPTION'
            ELSE 'LOW_CONSUMPTION'
        END AS anomaly_type

    FROM full_days d
    CROSS JOIN bounds b

    WHERE
        d.daily_energy_kwh < b.lower_bound
        OR d.daily_energy_kwh > b.upper_bound

    ORDER BY d.daily_energy_kwh DESC
""")

anomaly_sql.show(50, truncate=False)

print(
    "Total anomalous days:",
    anomaly_sql.count()
)

# ============================================================
# 5. SAVE ALL QUERY RESULTS TO HDFS
# ============================================================

query_results = {
    "hourly_consumption": hourly_sql,
    "top_daily_consumption": daily_top_sql,
    "monthly_consumption": monthly_sql,
    "peak_demand": peak_sql,
    "sub_metering": appliance_sql,
    "anomalies": anomaly_sql
}

print("\n========== SAVING SQL RESULTS TO HDFS ==========")

for name, result in query_results.items():

    destination = output_base + "/" + name

    result.write \
        .mode("overwrite") \
        .option("header", True) \
        .csv(destination)

    print("Saved:", destination)

print("\n============================================")
print("ALL SPARK SQL QUERIES EXECUTED SUCCESSFULLY")
print("============================================")

spark.stop()


# ============================================================
# 6. SPARK SQL EXECUTION PLAN
# ============================================================

print("\n========== SPARK SQL EXECUTION PLAN ==========")

plan_query = spark.sql("""
    SELECT
        date,
        SUM(energy_kwh) AS daily_energy_kwh,
        AVG(global_active_power) AS average_power_kw,
        MAX(global_active_power) AS peak_power_kw
    FROM energy_data
    GROUP BY date
    ORDER BY date
""")

print("\n--- EXTENDED EXECUTION PLAN ---")
plan_query.explain(mode="extended")

print("\n--- FORMATTED EXECUTION PLAN ---")
plan_query.explain(mode="formatted")

print("\n--- COST EXECUTION PLAN ---")
plan_query.explain(mode="cost")
