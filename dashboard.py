
import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Household Energy Analytics | Research Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

# Academic colour palette
NAVY = "#183153"
BLUE = "#2878B5"
TEAL = "#168C83"
ORANGE = "#D58A32"
RED = "#C94C4C"
GREY = "#64748B"
LIGHT_BLUE = "#EAF1F8"

# ============================================================
# 2. PAGE STYLING
# ============================================================

st.markdown("""

<style>
    /* Use Streamlit's active theme variables */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4, p, label {
        color: var(--text-color);
    }

    .main-title {
        color: var(--text-color);
        font-size: 2.15rem;
        font-weight: 750;
        margin-bottom: 0.15rem;
    }

    .subtitle {
        color: var(--text-color);
        opacity: 0.72;
        font-size: 1rem;
        margin-bottom: 1.2rem;
    }

    .section-label {
        color: var(--primary-color);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    .metric-card {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 9px;
        padding: 17px 18px;
        min-height: 112px;
    }

    .metric-label {
        color: var(--text-color);
        opacity: 0.75;
        font-size: 0.82rem;
        font-weight: 600;
    }

    .metric-value {
        color: var(--text-color);
        font-size: 1.65rem;
        font-weight: 750;
        margin-top: 7px;
    }

    .metric-note {
        color: var(--text-color);
        opacity: 0.65;
        font-size: 0.75rem;
        margin-top: 3px;
    }

    .info-panel {
        background-color: var(--secondary-background-color);
        border-left: 4px solid var(--primary-color);
        border-radius: 5px;
        padding: 13px 16px;
        color: var(--text-color);
        font-size: 0.91rem;
        margin: 8px 0 18px 0;
    }

    .method-card {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 8px;
        padding: 15px;
        min-height: 125px;
    }

    .method-heading {
        color: var(--text-color);
        font-weight: 700;
        margin-bottom: 7px;
    }

    [data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 1px solid rgba(128,128,128,0.25);
        padding: 14px;
        border-radius: 8px;
    }

    [data-testid="stSidebar"] {
        background-color: var(--secondary-background-color);
    }

    [data-testid="stSidebar"] * {
        color: var(--text-color);
    }

    hr {
        border-color: rgba(128,128,128,0.3);
    }

    /* Tables and expanders */
    [data-testid="stDataFrame"],
    [data-testid="stTable"],
    [data-testid="stExpander"] {
        color: var(--text-color);
    }

    /* Sidebar controls */
    [data-testid="stSidebar"] input {
        color: var(--text-color);
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. DATA LOADING
# ============================================================

@st.cache_data
def load_data():

    hourly = pd.read_csv(os.path.join(DATA_DIR, "hourly.csv"))
    daily = pd.read_csv(os.path.join(DATA_DIR, "daily.csv"))
    monthly = pd.read_csv(os.path.join(DATA_DIR, "monthly.csv"))
    peaks = pd.read_csv(os.path.join(DATA_DIR, "peak_demand.csv"))
    appliance = pd.read_csv(os.path.join(DATA_DIR, "appliance.csv"))
    anomalies = pd.read_csv(os.path.join(DATA_DIR, "anomalies.csv"))

    daily["date"] = pd.to_datetime(daily["date"])
    monthly["month"] = pd.to_datetime(monthly["month"])
    peaks["timestamp"] = pd.to_datetime(peaks["timestamp"])
    anomalies["date"] = pd.to_datetime(anomalies["date"])

    hourly["date"] = pd.to_datetime(hourly["date"])
    hourly["hour"] = pd.to_numeric(hourly["hour"], errors="coerce")

    return hourly, daily, monthly, peaks, appliance, anomalies


try:
    hourly, daily, monthly, peaks, appliance, anomalies = load_data()

except Exception as error:
    st.error(f"Data loading failed: {error}")
    st.info(
        "Check that all six CSV files are available in "
        "the data/processed directory."
    )
    st.stop()


# ============================================================
# 4. REUSABLE CHART CONFIGURATION
# ============================================================


def style_chart(fig, height=390):

    fig.update_layout(
        height=height,
        template="plotly",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Arial",
            size=12
        ),
        title_font=dict(size=17),
        margin=dict(l=45, r=25, t=65, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        hoverlabel=dict(
            font_size=12
        )
    )

    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linecolor="rgba(128,128,128,0.35)"
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(128,128,128,0.18)",
        zerolinecolor="rgba(128,128,128,0.3)"
    )

    return fig



def show_explanation(text):

    st.markdown(
        f'<div class="info-panel">{text}</div>',
        unsafe_allow_html=True
    )


def show_metric(label, value, note):

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# 5. HEADER
# ============================================================

st.markdown(
    '<div class="section-label">BIG DATA ANALYTICS PROJECT</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-title">Household Energy Analytics</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Analysis of electricity consumption patterns, demand behaviour '
    'and high-consumption anomalies'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    **Dataset:** UCI Individual Household Electric Power Consumption

    **Study period:** December 2006 – November 2010  
    **Study scope:** Electricity consumption measurements from one household
    """,
)

st.divider()


# ============================================================
# 6. SIDEBAR FILTERS
# ============================================================

st.sidebar.title("Research Controls")
st.sidebar.caption("Configure the analysis period.")

min_date = daily["date"].min().date()
max_date = daily["date"].max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

if start_date > end_date:
    st.sidebar.error("Invalid date range.")
    st.stop()

# Apply selected date range
filtered_daily = daily[
    (daily["date"].dt.date >= start_date) &
    (daily["date"].dt.date <= end_date)
].copy()

filtered_hourly = hourly[
    (hourly["date"].dt.date >= start_date) &
    (hourly["date"].dt.date <= end_date)
].copy()

filtered_monthly = monthly[
    (monthly["month"].dt.date >=
     pd.Timestamp(start_date).replace(day=1).date()) &
    (monthly["month"].dt.date <= end_date)
].copy()

filtered_anomalies = anomalies[
    (anomalies["date"].dt.date >= start_date) &
    (anomalies["date"].dt.date <= end_date)
].copy()

filtered_peaks = peaks[
    (peaks["timestamp"].dt.date >= start_date) &
    (peaks["timestamp"].dt.date <= end_date)
].copy()

st.sidebar.markdown("---")
st.sidebar.markdown("### Project Pipeline")
st.sidebar.markdown("""
1. HDFS – Distributed storage
2. Apache Pig – Data cleaning
3. Apache Spark – Data analytics
4. Python – Data visualization
5. Streamlit – Interactive dashboard
""")

st.sidebar.markdown("---")
st.sidebar.caption(
    "The selected date range applies to daily, monthly, "
    "hourly and date-specific demand and anomaly analysis."
)


# ============================================================
# 7. KEY PERFORMANCE INDICATORS
# ============================================================

st.markdown(
    '<div class="section-label">01 / RESEARCH OVERVIEW</div>',
    unsafe_allow_html=True
)

st.header("Energy Consumption Summary")

total_readings = int(filtered_daily["readings"].sum())

total_energy = filtered_daily["daily_energy_kwh"].sum()

if total_readings > 0:
    average_power = (
        (filtered_daily["average_power_kw"] *
         filtered_daily["readings"]).sum() / total_readings
    )
else:
    average_power = 0

maximum_power = (
    filtered_daily["peak_power_kw"].max()
    if not filtered_daily.empty else 0
)

anomaly_count = len(filtered_anomalies)

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    show_metric(
        "Valid Readings",
        f"{total_readings:,}",
        "One-minute observations"
    )

with k2:
    show_metric(
        "Total Energy",
        f"{total_energy:,.2f}",
        "kWh in selected period"
    )

with k3:
    show_metric(
        "Average Active Power",
        f"{average_power:.3f}",
        "kW, weighted by readings"
    )

with k4:
    show_metric(
        "Maximum Daily Peak",
        f"{maximum_power:.3f}",
        "kW"
    )

with k5:
    show_metric(
        "Anomaly Days",
        f"{anomaly_count}",
        "High-consumption records"
    )

show_explanation(
    "These indicators provide a summary of household electricity "
    "consumption for the selected period. Energy is measured in kWh, "
    "while active power is measured in kW."
)


# ============================================================
# 8. DASHBOARD TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Consumption Trends",
    "Time-Based Analysis",
    "Demand Analysis",
    "Sub-metering",
    "Anomaly Detection"
])


# ============================================================
# TAB 1: CONSUMPTION TRENDS
# ============================================================

with tab1:

    st.subheader("Daily Energy Consumption")

    if not filtered_daily.empty:

        fig = px.line(
            filtered_daily,
            x="date",
            y="daily_energy_kwh",
            title="Daily Household Electricity Consumption",
            labels={
                "date": "Date",
                "daily_energy_kwh": "Daily Energy Consumption (kWh)"
            },
            color_discrete_sequence=[BLUE],
            hover_data={
                "average_power_kw": ":.3f",
                "peak_power_kw": ":.3f",
                "readings": True
            }
        )

        fig.update_traces(line_width=1.5)
        fig.update_xaxes(rangeslider_visible=True)

        st.plotly_chart(
            style_chart(fig, 440),
            use_container_width=True,
            theme="streamlit"
        )

        show_explanation(
            "This time-series graph shows how much electrical energy "
            "the household consumed each day. Peaks and sudden changes "
            "help identify periods of unusually high or low consumption."
        )

    else:
        st.warning("No daily data is available for this period.")

    st.divider()

    st.subheader("Monthly Energy Consumption")

    if not filtered_monthly.empty:

        fig = px.bar(
            filtered_monthly,
            x="month",
            y="monthly_energy_kwh",
            title="Monthly Household Electricity Consumption",
            labels={
                "month": "Month",
                "monthly_energy_kwh": "Energy Consumption (kWh)"
            },
            color="monthly_energy_kwh",
            color_continuous_scale="Blues"
        )

        fig.update_layout(coloraxis_showscale=False)

        st.plotly_chart(
            style_chart(fig, 420),
            use_container_width=True,
            theme="streamlit"
)

        highest_month = filtered_monthly.loc[
            filtered_monthly["monthly_energy_kwh"].idxmax()
        ]

        show_explanation(
            f"The highest monthly consumption in the selected period "
            f"was {highest_month['monthly_energy_kwh']:.2f} kWh, "
            f"recorded in {highest_month['month'].strftime('%B %Y')}. "
            "Monthly aggregation helps reveal longer-term usage trends."
        )

    else:
        st.warning("No monthly records found.")


# ============================================================
# TAB 2: TIME-BASED ANALYSIS
# ============================================================

with tab2:

    st.subheader("Average Power Consumption by Hour")

    if not filtered_hourly.empty:
               hourly_data = filtered_hourly.copy()

               hourly_data["weighted_power"] = (
                  hourly_data["average_power_kw"] * hourly_data["readings"]
                 )

               hourly_pattern = hourly_data.groupby("hour").agg(
                  total_weighted_power=("weighted_power", "sum"),
                  total_readings=("readings", "sum")
                 )

               hourly_pattern["average_power_kw"] = (
               hourly_pattern["total_weighted_power"]
               / hourly_pattern["total_readings"]
                 )

               hourly_pattern = hourly_pattern.reindex(range(24))

               hourly_pattern = (
                   hourly_pattern[["average_power_kw"]]
                   .dropna()
                   .reset_index()
                   )

        fig = px.bar(
            hourly_pattern,
            x="hour",
            y="average_power_kw",
            title="Average Household Active Power by Hour of Day",
            labels={
                "hour": "Hour of Day (0–23)",
                "average_power_kw": "Average Active Power (kW)"
            },
            color="average_power_kw",
            color_continuous_scale="Teal"
        )

        fig.update_xaxes(
            tickmode="linear",
            dtick=1
        )

        fig.update_layout(coloraxis_showscale=False)

        st.plotly_chart(
            style_chart(fig, 420),
            use_container_width=True,
            theme="streamlit"
)

        if not hourly_pattern.empty:
            highest_hour = hourly_pattern.loc[
                hourly_pattern["average_power_kw"].idxmax()
            ]

            show_explanation(
                f"The highest average hourly power consumption occurred "
                f"at {int(highest_hour['hour']):02d}:00, with an average "
                f"of {highest_hour['average_power_kw']:.3f} kW. "
                "This analysis helps identify hours with relatively "
                "higher electricity demand."
            )

    else:
        st.warning("No hourly records found for this date range.")

    st.divider()

    st.subheader("Daily Average Power")

    if not filtered_daily.empty:

        fig = px.line(
            filtered_daily,
            x="date",
            y="average_power_kw",
            title="Daily Average Active Power",
            labels={
                "date": "Date",
                "average_power_kw": "Average Active Power (kW)"
            },
            color_discrete_sequence=[TEAL]
        )

        st.plotly_chart(
            style_chart(fig, 390),
            use_container_width=True,
        theme="streamlit"
        )

        show_explanation(
            "Average active power represents the average rate of "
            "electricity consumption over the recorded readings "
            "for each day."
        )


# ============================================================
# TAB 3: DEMAND ANALYSIS
# ============================================================

with tab3:

    st.subheader("Daily Peak Demand")

    if not filtered_daily.empty:

        fig = px.line(
            filtered_daily,
            x="date",
            y="peak_power_kw",
            title="Maximum Recorded Power Demand per Day",
            labels={
                "date": "Date",
                "peak_power_kw": "Peak Active Power (kW)"
            },
            color_discrete_sequence=[ORANGE]
        )

        fig.update_traces(
            line_width=1.5,
            fill="tozeroy",
            fillcolor="rgba(213,138,50,0.10)"
        )

        st.plotly_chart(
            style_chart(fig, 410),
            use_container_width=True,
            theme="streamlit"
        )

        show_explanation(
            "Daily peak demand is the highest one-minute active power "
            "reading recorded during each day. It helps identify "
            "short-duration periods of high electrical demand."
        )

    st.divider()

    st.subheader("Highest Recorded Demand Events")

    if not filtered_peaks.empty:

        top_peaks = filtered_peaks.nlargest(
            10, "global_active_power"
        ).copy()

        fig = px.bar(
            top_peaks.sort_values("global_active_power"),
            x="global_active_power",
            y="timestamp",
            orientation="h",
            title="Top 10 Recorded Active Power Readings",
            labels={
                "global_active_power": "Active Power (kW)",
                "timestamp": "Date and Time"
            },
            color="global_active_power",
            color_continuous_scale="Oranges",
            hover_data=["global_intensity", "voltage"]
        )

        fig.update_layout(coloraxis_showscale=False)

        st.plotly_chart(
            style_chart(fig, 440),
            use_container_width=True,
            theme="streamlit"
        )

        st.markdown("**Peak demand event details**")

        display_peaks = top_peaks[
            [
                "timestamp",
                "global_active_power",
                "global_intensity",
                "voltage"
            ]
        ].rename(columns={
            "timestamp": "Date and Time",
            "global_active_power": "Active Power (kW)",
            "global_intensity": "Intensity (A)",
            "voltage": "Voltage (V)"
        })

        st.dataframe(
            display_peaks.sort_values(
                "Active Power (kW)",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )

        show_explanation(
            "The table and chart show the highest available demand "
            "events in the selected period. Voltage and current intensity "
            "provide additional electrical context for these events."
        )

    else:
        st.info(
            "No peak-demand records are available for the selected "
            "period. The peak-demand file contains the records "
            "exported by the Spark analysis."
        )


# ============================================================
# TAB 4: SUB-METERING ANALYSIS
# ============================================================

with tab4:

    st.subheader("Sub-metering Energy Distribution")

    meter_values = appliance.iloc[0]

    meter_data = pd.DataFrame({
        "Sub-meter": [
            "Sub-meter 1",
            "Sub-meter 2",
            "Sub-meter 3"
        ],
        "Energy (kWh)": [
            meter_values["meter_1_kwh"],
            meter_values["meter_2_kwh"],
            meter_values["meter_3_kwh"]
        ]
    })

    fig = px.bar(
        meter_data,
        x="Sub-meter",
        y="Energy (kWh)",
        title="Total Energy Recorded by Each Sub-meter",
        labels={
            "Sub-meter": "Sub-meter Category",
            "Energy (kWh)": "Energy Consumption (kWh)"
        },
        color="Sub-meter",
        color_discrete_sequence=[BLUE, TEAL, ORANGE],
        text_auto=".2f"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(
        style_chart(fig, 410),
        use_container_width=True,
        theme="streamlit"
    )

    st.dataframe(
        meter_data,
        use_container_width=True,
        hide_index=True
    )

    show_explanation(
        "The dataset contains three sub-metering variables that record "
        "energy use for specific electrical categories. The graph "
        "compares their cumulative recorded energy. The dataset does "
        "not establish that these categories correspond to named "
        "individual appliances."
    )

    st.info(
        "Sub-metering totals represent the complete dataset period. "
        "They are not recalculated when the date filter changes."
    )


# ============================================================
# TAB 5: ANOMALY DETECTION
# ============================================================

with tab5:

    st.subheader("High-Consumption Anomaly Analysis")

    st.markdown(
        "The Spark analytics stage identified unusual daily "
        "energy consumption records using an IQR-based method."
    )

    if not filtered_daily.empty:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=filtered_daily["date"],
                y=filtered_daily["daily_energy_kwh"],
                mode="lines",
                name="Daily Consumption",
                line=dict(color=BLUE, width=1.5)
            )
        )

        if not filtered_anomalies.empty:

            fig.add_trace(
                go.Scatter(
                    x=filtered_anomalies["date"],
                    y=filtered_anomalies["daily_energy_kwh"],
                    mode="markers",
                    name="High-Consumption Anomaly",
                    marker=dict(
                        color=RED,
                        size=9,
                        symbol="diamond"
                    ),
                    customdata=filtered_anomalies[
                        ["peak_power_kw", "average_power_kw"]
                    ],
                    hovertemplate=(
                        "Date: %{x|%d %b %Y}<br>"
                        "Energy: %{y:.2f} kWh<br>"
                        "Peak Power: %{customdata[0]:.3f} kW<br>"
                        "Average Power: %{customdata[1]:.3f} kW"
                        "<extra></extra>"
                    )
                )
            )

        fig.update_layout(
            title="Daily Consumption with Detected Anomalies",
            xaxis_title="Date",
            yaxis_title="Daily Energy Consumption (kWh)"
        )

        st.plotly_chart(
            style_chart(fig, 440),
            use_container_width=True,
            theme="streamlit"    )

        if not filtered_anomalies.empty:

            highest_anomaly = filtered_anomalies.loc[
                filtered_anomalies["daily_energy_kwh"].idxmax()
            ]

            a1, a2, a3 = st.columns(3)

            a1.metric(
                "Detected Anomaly Days",
                len(filtered_anomalies)
            )

            a2.metric(
                "Highest Anomaly",
                f"{highest_anomaly['daily_energy_kwh']:.2f} kWh"
            )

            a3.metric(
                "Highest Anomaly Date",
                highest_anomaly["date"].strftime("%d %b %Y")
            )

            st.markdown("**Anomaly records**")

            display_anomalies = filtered_anomalies.sort_values(
                "daily_energy_kwh",
                ascending=False
            )

            st.dataframe(
                display_anomalies,
                use_container_width=True,
                hide_index=True
            )

            show_explanation(
                "Red diamond markers represent daily records flagged "
                "as high-consumption anomalies by the Spark processing "
                "stage. These are statistically unusual observations, "
                "not proof of equipment failure or electricity theft."
            )

        else:
            st.success(
                "No detected anomaly records occur within this "
                "selected period."
            )

    else:
        st.warning("No daily data is available for this period.")


# ============================================================
# 10. METHODOLOGY AND DATASET INFORMATION
# ============================================================

st.divider()

st.markdown(
    '<div class="section-label">02 / RESEARCH METHODOLOGY</div>',
    unsafe_allow_html=True
)

st.header("Data Processing Architecture")

st.markdown(
    "The project follows a distributed data processing workflow. "
    "Each technology performs a specific role in transforming "
    "raw electricity measurements into analytical results."
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown("""
    <div class="method-card">
        <div class="method-heading">01. HDFS</div>
        Distributed storage of the raw household electricity dataset.
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="method-card">
        <div class="method-heading">02. Apache Pig</div>
        Filtering invalid records, handling missing values and preparing
        cleaned data.
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="method-card">
        <div class="method-heading">03. Apache Spark</div>
        Aggregation, consumption analysis, peak demand and anomaly
        detection.
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown("""
    <div class="method-card">
        <div class="method-heading">04. Python & Streamlit</div>
        Visualization, interactive filtering and analytical presentation.
    </div>
    """, unsafe_allow_html=True)

st.markdown("### Dataset characteristics")

dataset_info = pd.DataFrame({
    "Parameter": [
        "Dataset",
        "Source",
        "Study scope",
        "Time period",
        "Sampling frequency",
        "Original observations",
        "Valid processed observations"
    ],
    "Description": [
        "Individual Household Electric Power Consumption",
        "UCI Machine Learning Repository",
        "One household",
        "December 2006 – November 2010",
        "One-minute intervals",
        "2,075,259 measurement records",
        "2,049,280 valid records"
    ]
})

st.dataframe(
    dataset_info,
    use_container_width=True,
    hide_index=True
)

st.markdown("### Analytical methods")

st.markdown("""
- **Daily aggregation:** Summarizes energy consumption and peak power
  for each day.
- **Monthly aggregation:** Examines longer-term electricity consumption.
- **Hourly analysis:** Compares average power consumption across the
  24 hours of a day.
- **Peak demand analysis:** Identifies high active-power readings.
- **Anomaly detection:** Uses the Interquartile Range (IQR) method to
  identify unusually high daily energy consumption.
""")

with st.expander("About the IQR anomaly detection method"):

    st.markdown("""
    The Interquartile Range method identifies observations that lie
    unusually far from the middle 50% of the data.

    - Q1: First quartile (25th percentile)
    - Q3: Third quartile (75th percentile)
    - IQR: Q3 minus Q1
    - Upper threshold: Q3 + 1.5 × IQR

    Daily energy values above the upper threshold are flagged as
    high-consumption anomalies in this project.

    These are statistical flags and require further investigation
    before any real-world operational conclusion can be made.
    """)


# ============================================================
# 11. FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; padding:12px; color:#64748B;">
        <b style="color:#183153;">Household Energy Analytics</b><br>
        Big Data Analytics Project<br>
        Hadoop HDFS | Apache Pig | Apache Spark | Python | Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
