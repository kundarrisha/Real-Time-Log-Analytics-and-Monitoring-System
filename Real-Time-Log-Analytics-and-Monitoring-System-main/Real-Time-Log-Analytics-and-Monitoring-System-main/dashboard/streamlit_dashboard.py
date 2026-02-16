import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient
from datetime import datetime, timedelta
import json
import time

# Page config
st.set_page_config(
    page_title="Real-Time Log Analytics",
    page_icon="📊",
    layout="wide"
)

# Load config
@st.cache_resource
def get_mongo_connection():
    with open('../config/config.json', 'r') as f:
        config = json.load(f)
    
    mongo_config = config['mongodb']
    client = MongoClient(
        f"mongodb://{mongo_config['host']}:{mongo_config['port']}"
    )
    db = client[mongo_config['database']]
    collection = db[mongo_config['collection']]
    return collection

def get_logs_data(hours=1):
    """Fetch logs from MongoDB"""
    collection = get_mongo_connection()
    start_time = datetime.now() - timedelta(hours=hours)
    
    logs = list(collection.find(
        {'timestamp': {'$gte': start_time}},
        {'_id': 0}
    ).sort('timestamp', -1))
    
    if logs:
        return pd.DataFrame(logs)
    return pd.DataFrame()

# Title
st.title("📊 Real-Time Log Analysis Dashboard")
st.markdown("---")

# Sidebar
st.sidebar.header("Settings")
time_range = st.sidebar.selectbox(
    "Time Range",
    ["Last 1 Hour", "Last 6 Hours", "Last 24 Hours"]
)

hours_map = {
    "Last 1 Hour": 1,
    "Last 6 Hours": 6,
    "Last 24 Hours": 24
}
selected_hours = hours_map[time_range]

# Auto-refresh
auto_refresh = st.sidebar.checkbox("Auto Refresh (30s)", value=True)
if auto_refresh:
    time.sleep(30)
    st.rerun()

# Fetch data
df = get_logs_data(hours=selected_hours)

if df.empty:
    st.warning("No log data available. Make sure the log generator and ingestion scripts are running.")
    st.stop()

# Convert timestamp to datetime if it's not already
if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
    df['timestamp'] = pd.to_datetime(df['timestamp'])

# Key Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Logs", f"{len(df):,}")

with col2:
    error_count = len(df[df['level'].isin(['ERROR', 'CRITICAL'])])
    st.metric("Errors", error_count, delta=None)

with col3:
    avg_response = df['response_time'].mean()
    st.metric("Avg Response Time", f"{avg_response:.0f}ms")

with col4:
    services_count = df['service'].nunique()
    st.metric("Active Services", services_count)

st.markdown("---")

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("Log Levels Distribution")
    level_counts = df['level'].value_counts()
    fig = px.pie(
        values=level_counts.values,
        names=level_counts.index,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Logs Over Time")
    df_time = df.set_index('timestamp').resample('5min').size().reset_index(name='count')
    fig = px.line(df_time, x='timestamp', y='count', markers=True)
    fig.update_layout(xaxis_title="Time", yaxis_title="Log Count")
    st.plotly_chart(fig, use_container_width=True)

# Charts Row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("Service Activity")
    service_counts = df['service'].value_counts().head(10)
    fig = px.bar(
        x=service_counts.values,
        y=service_counts.index,
        orientation='h',
        labels={'x': 'Count', 'y': 'Service'}
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Response Time Distribution")
    fig = px.histogram(
        df, x='response_time', nbins=30,
        labels={'response_time': 'Response Time (ms)'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Error Analysis
st.markdown("---")
st.subheader("🔴 Error Analysis")

error_df = df[df['level'].isin(['ERROR', 'CRITICAL'])]
if not error_df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Most Frequent Errors**")
        error_msgs = error_df['message'].value_counts().head(5)
        st.dataframe(error_msgs, use_container_width=True)
    
    with col2:
        st.write("**Errors by Service**")
        error_by_service = error_df['service'].value_counts()
        st.dataframe(error_by_service, use_container_width=True)
else:
    st.success("No errors in the selected time range!")

# Recent Logs Table
st.markdown("---")
st.subheader("Recent Logs")
recent_logs = df.head(50)[['timestamp', 'level', 'service', 'user_id', 'message', 'response_time']]
st.dataframe(recent_logs, use_container_width=True, height=300)

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")