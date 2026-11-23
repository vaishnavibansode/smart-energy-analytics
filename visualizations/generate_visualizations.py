
import os
import pandas as pd
import matplotlib.pyplot as plt

# Project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUT_DIR = os.path.join(BASE_DIR, "visualizations")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load Spark analytical results
hourly = pd.read_csv(os.path.join(DATA_DIR, "hourly.csv"))
daily = pd.read_csv(os.path.join(DATA_DIR, "daily.csv"))
monthly = pd.read_csv(os.path.join(DATA_DIR, "monthly.csv"))
peaks = pd.read_csv(os.path.join(DATA_DIR, "peak_demand.csv"))
appliance = pd.read_csv(os.path.join(DATA_DIR, "appliance.csv"))
anomalies = pd.read_csv(os.path.join(DATA_DIR, "anomalies.csv"))

# Convert dates
daily["date"] = pd.to_datetime(daily["date"])
monthly["month"] = pd.to_datetime(monthly["month"])

# 1. Monthly Energy Consumption
plt.figure(figsize=(12, 6))
plt.plot(
    monthly["month"],
    monthly["monthly_energy_kwh"],
    marker="o"
)
plt.title("Monthly Household Energy Consumption")
plt.xlabel("Month")
plt.ylabel("Energy Consumption (kWh)")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "monthly_consumption.png"), dpi=300)
plt.close()

# 2. Daily Energy Consumption
plt.figure(figsize=(13, 6))
plt.plot(
    daily["date"],
    daily["daily_energy_kwh"]
)
plt.title("Daily Household Energy Consumption")
plt.xlabel("Date")
plt.ylabel("Energy Consumption (kWh)")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "daily_consumption.png"), dpi=300)
plt.close()


# 3. Average Consumption by Hour

# Convert columns to numeric values
hourly["hour"] = pd.to_numeric(hourly["hour"], errors="coerce")
hourly["average_power_kw"] = pd.to_numeric(
    hourly["average_power_kw"], errors="coerce"
)
hourly["readings"] = pd.to_numeric(
    hourly["readings"], errors="coerce"
)

# Remove invalid records
hourly_valid = hourly.dropna(
    subset=["hour", "average_power_kw", "readings"]
).copy()

hourly_valid = hourly_valid[
    hourly_valid["hour"].between(0, 23)
    & (hourly_valid["readings"] > 0)
]

# Calculate weighted average power for each hour
hourly_valid["weighted_power"] = (
    hourly_valid["average_power_kw"] * hourly_valid["readings"]
)

hourly_pattern = hourly_valid.groupby("hour").agg(
    total_weighted_power=("weighted_power", "sum"),
    total_readings=("readings", "sum")
)

hourly_pattern["average_power_kw"] = (
    hourly_pattern["total_weighted_power"]
    / hourly_pattern["total_readings"]
)

# Ensure all 24 hours are represented
hourly_pattern = hourly_pattern.reindex(range(24))

# Retain the calculated average for plotting
hourly_pattern = hourly_pattern["average_power_kw"]

plt.figure(figsize=(11, 6))
hourly_pattern.plot(kind="bar")

plt.title("Average Household Power Consumption by Hour")
plt.xlabel("Hour of Day")
plt.ylabel("Average Active Power (kW)")
plt.xticks(range(24), [f"{i:02d}" for i in range(24)], rotation=0)
plt.grid(axis="y")
plt.tight_layout()

plt.savefig(
    os.path.join(OUTPUT_DIR, "hourly_consumption.png"),
    dpi=300
)
plt.close()


# 4. Top 10 Peak Demand Readings
top_peaks = peaks.head(10).copy()
top_peaks["timestamp"] = pd.to_datetime(top_peaks["timestamp"])

plt.figure(figsize=(12, 6))
plt.bar(
    top_peaks["timestamp"].dt.strftime("%d-%m-%Y %H:%M"),
    top_peaks["global_active_power"]
)
plt.title("Top 10 Peak Household Demand Readings")
plt.xlabel("Date and Time")
plt.ylabel("Active Power (kW)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "peak_demand.png"), dpi=300)
plt.close()

# 5. Appliance-wise Consumption
meter_values = appliance.iloc[0][
    ["meter_1_kwh", "meter_2_kwh", "meter_3_kwh"]
]

plt.figure(figsize=(9, 6))
plt.bar(
    ["Sub-meter 1", "Sub-meter 2", "Sub-meter 3"],
    meter_values.values
)
plt.title("Appliance Sub-metering Energy Consumption")
plt.xlabel("Sub-meter")
plt.ylabel("Energy Consumption (kWh)")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "appliance_consumption.png"), dpi=300)
plt.close()

# 6. Daily Peak Demand
plt.figure(figsize=(13, 6))
plt.plot(
    daily["date"],
    daily["peak_power_kw"]
)
plt.title("Daily Peak Power Demand")
plt.xlabel("Date")
plt.ylabel("Peak Active Power (kW)")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "daily_peak_demand.png"), dpi=300)
plt.close()

print("\nAll visualizations generated successfully.")

for filename in sorted(os.listdir(OUTPUT_DIR)):
    if filename.endswith(".png"):
        print(filename)


# 7. Daily Consumption Anomaly Detection
plt.figure(figsize=(13, 6))

plt.plot(
    daily["date"],
    daily["daily_energy_kwh"],
    label="Daily Energy Consumption",
    alpha=0.7
)

plt.scatter(
    pd.to_datetime(anomalies["date"]),
    anomalies["daily_energy_kwh"],
    label="Detected Anomalies",
    marker="x",
    s=60
)

plt.axhline(
    49.40753333333338,
    linestyle="--",
    label="Upper IQR Threshold"
)

plt.title("Household Energy Consumption Anomaly Detection")
plt.xlabel("Date")
plt.ylabel("Daily Energy Consumption (kWh)")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    os.path.join(OUTPUT_DIR, "anomaly_detection.png"),
    dpi=300
)
plt.close()
