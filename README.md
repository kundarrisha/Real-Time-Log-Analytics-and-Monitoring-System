# 📊 Real-Time Log Analytics & Monitoring System

A lightweight, end-to-end platform that simulates enterprise-grade log monitoring — from log generation to real-time ingestion, big-data storage, analytics, and live dashboarding. Built to demonstrate core big-data and observability concepts using accessible, low-spec-friendly tooling.

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-hot%20storage-47A248?logo=mongodb&logoColor=white)
![HDFS](https://img.shields.io/badge/Hadoop%20HDFS-cold%20storage-66CCFF?logo=apachehadoop&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Overview

This project simulates the log pipeline of a multi-service application: logs are continuously generated, streamed into a hot-storage database for real-time queries and a cold-storage data lake for long-term retention, then processed into analytics and visualized on a live dashboard.

It's designed to run entirely on a single Windows machine with modest specs, while still reflecting the architecture patterns used in production observability stacks (hot/cold storage tiers, stream ingestion, scheduled analytics, BI export).

## Architecture

![System Architecture](./images/diagram.png)

**Pipeline flow:**

```
Log Generator → application.log → Log Ingestion (watchdog) → MongoDB (hot storage)
                                 → HDFS Uploader              → HDFS (cold storage)

MongoDB → Log Processor / Analytics → JSON Reports (outputs/reports)
MongoDB → Streamlit Dashboard (live view)
MongoDB → Power BI Export (CSV)
```

## Key Features

- **Synthetic log generation** — realistic, multi-service logs (Auth, Payment, User, Notification, Database) with configurable log levels, response times, and error scenarios via Faker.
- **Real-time ingestion** — a `watchdog`-based file watcher tails the log file and streams parsed entries into MongoDB as they're written.
- **Dual storage tiers** — MongoDB for fast, queryable "hot" storage and HDFS for durable "cold" archival storage.
- **Analytics engine** — Pandas-based processing over MongoDB data: log-level breakdowns, per-service activity, response-time statistics, and error/anomaly detection against configurable thresholds.
- **Live dashboard** — a Streamlit + Plotly dashboard for real-time visualization of log volume, error rates, and service health.
- **Automated reporting** — periodic JSON analytics reports written to `outputs/reports/`.
- **BI-ready export** — one-click export of recent log data to CSV for Power BI.

## Tech Stack

| Layer | Technology |
|---|---|
| Log generation | Python, Faker |
| Ingestion / streaming | Python, Watchdog |
| Hot storage | MongoDB |
| Cold storage | HDFS (Hadoop) |
| Processing / analytics | Python, Pandas |
| Dashboard | Streamlit, Plotly |
| BI export | Power BI (via CSV) |

## Project Structure

```
├── config/
│   └── config.json          # MongoDB, log path, and analytics settings
├── dashboard/
│   └── streamlit_dashboard.py
├── scripts/
│   ├── log_generator.py     # Simulates multi-service application logs
│   ├── log_ingestion.py     # Watches log file, parses & writes to MongoDB
│   ├── log_processor.py     # Analytics engine (stats, anomaly detection, reports)
│   ├── upload_logs_to_hdfs.py
│   └── export_for_powerbi.py
├── outputs/
│   └── reports/             # Generated JSON analytics reports
├── logs/
│   └── application.log      # Generated log output
└── images/
    └── diagram.png          # Architecture diagram
```

## Getting Started

### Prerequisites

- Python 3.9+
- MongoDB Community Edition
- Hadoop / HDFS (or an HDFS client) — optional, only needed for cold-storage archival
- Python packages: `faker`, `pymongo`, `watchdog`, `pandas`, `streamlit`, `plotly`, `hdfs`

Install dependencies:

```bash
pip install faker pymongo watchdog pandas streamlit plotly hdfs
```

### 1. Clone the repository

```bash
git clone https://github.com/kundarrisha/Real-Time-Log-Analytics-and-Monitoring-System.git
cd Real-Time-Log-Analytics-and-Monitoring-System
```

### 2. Start MongoDB

```bash
net start MongoDB
```

Ensure the database directory (e.g. `C:\data\db`) exists.

### 3. (Optional) Start HDFS

```bash
cd C:\hadoop\hadoop-3.4.2\sbin
hdfs namenode -format
start-dfs.cmd
```

### 4. Configure paths

Update `config/config.json` with your local log directory and MongoDB settings.

### 5. Run the pipeline

Open separate terminals for each component:

```bash
# Terminal 1 — generate logs
cd scripts
python log_generator.py

# Terminal 2 — ingest logs into MongoDB
cd scripts
python log_ingestion.py

# Terminal 3 — launch the live dashboard
cd dashboard
streamlit run streamlit_dashboard.py

# Terminal 4 — run analytics & generate reports
cd scripts
python log_processor.py

# Terminal 5 (optional) — archive logs to HDFS
cd scripts
python upload_logs_to_hdfs.py
```

## Sample Output

A generated analytics report includes log-level distribution, per-service breakdowns, response-time statistics, and detected anomalies:

```json
{
  "statistics": {
    "total_logs": 25677,
    "log_levels": { "INFO": 15404, "WARNING": 5226, "ERROR": 2511 },
    "avg_response_time": 651.37,
    "error_count": 3002
  },
  "anomalies": [
    { "type": "High Response Time", "count": 2191, "threshold": 2809.87 }
  ]
}
```

## Roadmap

- [ ] Containerize with Docker Compose for one-command startup
- [ ] Add alerting (email/Slack) on anomaly detection
- [ ] Replace polling-based HDFS upload with a streaming connector
- [ ] Add unit tests for log parsing and analytics functions

## License

This project is available under the MIT License.
