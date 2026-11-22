# Household Energy Analytics Using Big Data Technologies

An academic Big Data analytics project that analyses household electricity consumption using Hadoop HDFS, Apache Pig, Apache Spark and Python-based interactive visualizations.

## Project Overview

This project analyses the Individual Household Electric Power Consumption dataset published by the UCI Machine Learning Repository.

The dataset contains minute-level electricity measurements collected from a single household over approximately four years.

The objective is to understand electricity consumption patterns, analyse demand behaviour, compare sub-metering measurements and identify unusually high daily energy consumption.

## Objectives

- Process large-scale electricity consumption data.
- Clean missing and invalid records.
- Store and process data using Hadoop ecosystem technologies.
- Perform hourly, daily and monthly consumption analysis.
- Analyse peak electricity demand.
- Compare sub-metering energy consumption.
- Detect unusually high daily consumption using the Interquartile Range (IQR) method.
- Present analytical results through an interactive Streamlit dashboard.

## Technology Stack

| Technology | Purpose |
|---|---|
| Hadoop HDFS | Distributed storage |
| Apache Pig | Data cleaning and preprocessing |
| Apache Spark | Large-scale data aggregation and analytics |
| Python | Data analysis and visualization |
| Pandas | Processed data handling |
| Plotly | Interactive charts |
| Streamlit | Research dashboard |

## Architecture

1. Raw electricity consumption dataset
2. Hadoop Distributed File System (HDFS)
3. Apache Pig data cleaning
4. Apache Spark analytics
5. Processed CSV analytical outputs
6. Python visualizations and Streamlit dashboard

## Dataset

**Individual Household Electric Power Consumption**

Source: UCI Machine Learning Repository

https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption

The original dataset is not included in this repository because of its size. Download it from the official source to reproduce the complete processing pipeline.

## Analytical Modules

### 1. Monthly Consumption
Examines long-term household energy consumption trends.

### 2. Daily Consumption
Studies day-to-day electricity usage variations.

### 3. Hourly Consumption
Identifies average power consumption patterns across the 24 hours of a day.

### 4. Peak Demand Analysis
Examines daily maximum power demand and the highest recorded demand readings.

### 5. Sub-metering Analysis
Compares electricity consumption across the three recorded sub-metering categories.

### 6. Anomaly Detection
Uses the Interquartile Range (IQR) statistical method to identify unusually high daily energy consumption.

## Key Results

- Valid readings after preprocessing: 2,049,280
- Average active power: approximately 1.092 kW
- Maximum recorded active power: 11.122 kW
- High-consumption anomaly days: 34
- Highest detected daily consumption: approximately 79.556 kWh

These results are based on the processed dataset generated during the project execution.

## Repository Structure

```text
smart-energy-analytics/
├── dashboard.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── processed/
│       ├── hourly.csv
│       ├── daily.csv
│       ├── monthly.csv
│       ├── peak_demand.csv
│       ├── appliance.csv
│       └── anomalies.csv
├── pig/
│   └── clean_energy_data.pig
├── spark/
│   └── energy_analytics.py
└── visualizations/
    ├── generate_visualizations.py
    └── generated charts
