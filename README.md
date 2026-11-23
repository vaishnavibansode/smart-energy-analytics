# Smart Energy Analytics Using Big Data Technologies

## 1. Project Overview

Smart Energy Analytics is a Big Data Analytics project that analyzes household electricity consumption using distributed data processing technologies.

The project uses the **Individual Household Electric Power Consumption** dataset from the UCI Machine Learning Repository. It contains minute-level electricity measurements collected from a single household over approximately four years, from December 2006 to November 2010.

The objective is to process large volumes of electricity consumption data, identify usage patterns, analyze peak demand, examine appliance-level consumption, detect unusual consumption days, and present the findings through visualizations and an interactive dashboard.

## 2. Objectives

- Process a large household electricity consumption dataset using Big Data technologies.
- Store and manage the dataset using Hadoop Distributed File System (HDFS).
- Clean and transform raw data using Apache Pig.
- Perform distributed analytical processing using Apache Spark.
- Execute analytical queries using Spark SQL.
- Analyze hourly, daily, and monthly electricity consumption patterns.
- Identify peak-demand readings and unusual consumption days.
- Examine the contribution of individual appliance sub-metering measurements.
- Present analytical findings through static visualizations and an interactive dashboard.

## 3. Dataset Description

**Dataset:** Individual Household Electric Power Consumption  
**Source:** UCI Machine Learning Repository  
**Time period:** December 2006 – November 2010  
**Original size:** Approximately 2.07 million records, including the header  
**Valid cleaned records:** 2,049,280

The dataset contains the following attributes:

| Attribute | Description |
|---|---|
| Date | Date of the electricity measurement |
| Time | Time of the measurement |
| Global_active_power | Household global active power (kW) |
| Global_reactive_power | Household global reactive power (kW) |
| Voltage | Voltage (V) |
| Global_intensity | Current intensity (A) |
| Sub_metering_1 | Energy sub-metering for kitchen appliances |
| Sub_metering_2 | Energy sub-metering for laundry appliances |
| Sub_metering_3 | Energy sub-metering for water-heating and air-conditioning appliances |

The raw dataset contains missing values represented by `?`. These records are handled during the data-cleaning stage.

**Dataset limitation:** The dataset represents one household, not a collection of households. Therefore, the results describe the consumption patterns observed in this household and should not be generalized to all households.

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| Hadoop HDFS | Distributed data storage |
| Apache Pig | Data cleaning and preprocessing |
| Apache Spark | Distributed data processing and analytics |
| Spark SQL | Structured analytical queries |
| Python | Data analysis and visualization |
| Pandas | Local analytical data handling |
| Matplotlib / Seaborn | Static visualizations |
| Streamlit | Interactive dashboard |
| Plotly | Interactive charts |
| Git and GitHub | Version control and project hosting |

## 5. System Architecture

The project follows a data-processing pipeline:

1. **Data ingestion:** The original household electricity dataset is obtained and made available for processing.
2. **Distributed storage:** The input data is stored in HDFS.
3. **Data cleaning:** Apache Pig removes invalid and missing records, performs required type conversions, and writes cleaned data back to HDFS.
4. **Distributed analytics:** PySpark processes the cleaned data to calculate hourly, daily, and monthly consumption, peak demand, appliance-level totals, and consumption anomalies.
5. **SQL analytics:** Spark SQL executes structured queries over the cleaned dataset to produce corresponding analytical result sets.
6. **Visualization:** Python scripts generate static charts from the processed analytical CSV files.
7. **Dashboard:** Streamlit and Plotly provide an interactive interface for exploring the processed results.

## 6. Data Processing and Analytics

### 6.1 Data Cleaning Using Apache Pig

The Pig script `pig/clean_energy_data.pig` performs preprocessing operations, including:

- Loading the raw dataset.
- Removing the header and records containing missing values.
- Converting fields into appropriate data types.
- Preparing the cleaned dataset for downstream Spark processing.
- Storing the cleaned output in HDFS.

The cleaned dataset contains 2,049,280 valid records.

### 6.2 PySpark DataFrame Analytics

The script `spark/energy_analytics.py` performs distributed analytical operations.

The main analytical activities include:

- Dataset summary and descriptive statistics.
- Hourly electricity consumption analysis.
- Daily electricity consumption analysis.
- Monthly consumption trends.
- Peak-demand identification.
- Appliance-level sub-metering analysis.
- Daily consumption anomaly detection using the Interquartile Range (IQR) method.

Energy consumption per minute is calculated from global active power using:

`energy_kwh = global_active_power / 60`

Daily anomaly detection considers complete days with at least 1,200 readings. The IQR method uses the first and third quartiles to calculate the upper and lower anomaly thresholds.

### 6.3 Spark SQL Analytics

The separate script `spark/energy_sql_queries.py` performs structured analysis using Spark SQL.

It registers the cleaned dataset as a temporary SQL view and executes six analytical queries:

| Query | Analytical purpose |
|---|---|
| Hourly Consumption | Calculates total energy, average power, peak power, and reading count for each hour |
| Top Daily Consumption | Identifies the ten highest-consumption complete days |
| Monthly Consumption | Summarizes electricity consumption by month |
| Peak Demand | Retrieves the twenty highest power-demand readings |
| Sub-metering | Calculates the total energy contribution of the three sub-metering categories |
| Anomaly Detection | Uses daily aggregation and IQR-based thresholds to identify unusual consumption days |

The SQL query outputs are written to HDFS under:

`/user/vaishnavi/smart-energy/sql-results/`

The exported SQL result CSV files are maintained separately from the existing DataFrame analytics outputs in `data/processed/sql_results/`.

This separation allows both analytical approaches and their outputs to be inspected independently.

## 7. Important Analytical Findings

The analysis of the cleaned household dataset produced the following findings:

| Metric | Result |
|---|---:|
| Valid records | 2,049,280 |
| Average active power | Approximately 1.0916 kW |
| Maximum active power | 11.122 kW |
| Average voltage | Approximately 240.84 V |
| Highest recorded demand | 11.122 kW |
| Peak-demand timestamp | 22 February 2009, 17:09 |
| High-consumption anomaly days | 34 |

### Appliance-level consumption

| Sub-meter | Total consumption |
|---|---:|
| Sub-meter 1 | 2,299.135 kWh |
| Sub-meter 2 | 2,661.031 kWh |
| Sub-meter 3 | 13,235.167 kWh |

Sub-meter 3 accounts for the largest recorded contribution among the three sub-metering categories.

### Anomaly detection

The IQR-based analysis identifies unusually high daily electricity consumption.

The calculated upper threshold is approximately 49.408 kWh per day. A total of 34 high-consumption anomaly days were identified among the complete days considered by the analysis.

The highest recorded daily consumption anomaly occurred on 23 December 2006, at approximately 79.556 kWh.

## 8. Visualizations

The project includes static visualizations for:

- Monthly electricity consumption.
- Daily electricity consumption.
- Hourly electricity consumption.
- Peak-demand readings.
- Appliance-level consumption.
- Daily peak demand.
- Consumption anomaly detection.

The generated charts are available in the `visualizations/` directory.

## 9. Interactive Dashboard

The Streamlit dashboard provides an interactive way to explore the processed electricity consumption data.

It uses Pandas for data handling and Plotly for interactive visualizations.

The dashboard is designed to display analytical results without requiring the Hadoop, Pig, or Spark processing jobs to run every time a user opens it. It reads the processed CSV outputs included in the project.

### Run the dashboard locally

Clone the repository:

```bash
git clone https://github.com/vaishnavibansode/smart-energy-analytics.git
cd smart-energy-analytics
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Start the dashboard:

```bash
streamlit run dashboard.py
```

Open the local URL displayed in the terminal.

## 10. Project Structure

```text
smart-energy-analytics/
│
├── data/
│   └── processed/
│       ├── anomalies.csv
│       ├── appliance.csv
│       ├── daily.csv
│       ├── hourly.csv
│       ├── monthly.csv
│       ├── peak_demand.csv
│       │
│       └── sql_results/
│           ├── hourly_consumption.csv
│           ├── top_daily_consumption.csv
│           ├── monthly_consumption.csv
│           ├── peak_demand.csv
│           ├── sub_metering.csv
│           └── anomalies.csv
│
├── pig/
│   └── clean_energy_data.pig
│
├── spark/
│   ├── energy_analytics.py
│   └── energy_sql_queries.py
│
├── visualizations/
│   ├── generate_visualizations.py
│   └── generated chart images
│
├── dashboard.py
├── requirements.txt
├── .gitignore
└── README.md
```

The original raw dataset and Python virtual environment are excluded from version control. The processed analytical outputs and SQL result CSV files are included for reproducibility and inspection.

## 11. Limitations

- The dataset represents only one household.
- The analysis describes historical consumption and does not provide a real-time electricity monitoring system.
- The project focuses on data processing, analytical querying, anomaly identification, and visualization rather than predictive model deployment.
- The dashboard uses precomputed CSV outputs; it does not execute Hadoop, Pig, or Spark jobs interactively.
- Anomaly detection identifies statistical outliers and does not independently establish the cause of unusual electricity consumption.

## 12. Conclusion

The project demonstrates how Big Data technologies can be combined to process and analyze a large household electricity consumption dataset.

Hadoop HDFS provides distributed storage, Apache Pig performs data cleaning, and Apache Spark supports distributed data processing and analytical queries. Spark SQL adds structured query-based analysis, while Python visualizations and the Streamlit dashboard make the findings easier to interpret.

The analysis identifies consumption trends, peak-demand periods, appliance-level usage contributions, and unusual daily consumption patterns. Together, these components demonstrate an end-to-end Big Data Analytics workflow, from raw data preprocessing to analytical reporting and visualization.

## 13. Repository

GitHub: https://github.com/vaishnavibansode/smart-energy-analytics

