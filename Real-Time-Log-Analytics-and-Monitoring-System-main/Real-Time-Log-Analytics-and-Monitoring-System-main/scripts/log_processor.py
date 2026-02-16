import json
import os
from datetime import datetime, timedelta
from pymongo import MongoClient, errors
import pandas as pd
from collections import Counter


class LogProcessor:
    """A class for processing and analyzing log data stored in MongoDB."""

    def __init__(self, config):
        self.config = config
        mongo_config = config.get('mongodb', {})

        try:
            self.client = MongoClient(
                f"mongodb://{mongo_config['host']}:{mongo_config['port']}",
                serverSelectionTimeoutMS=5000
            )
            # Validate connection
            self.client.server_info()
        except errors.ServerSelectionTimeoutError as e:
            raise ConnectionError("❌ Could not connect to MongoDB server.") from e

        self.db = self.client[mongo_config['database']]
        self.collection = self.db[mongo_config['collection']]

        # Ensure output directory exists
        os.makedirs("../outputs/reports", exist_ok=True)

    # ------------------- CORE DATA FUNCTIONS -------------------

    def get_logs_dataframe(self, hours=24):
        """
        Retrieve logs from the last N hours as a pandas DataFrame.
        Returns an empty DataFrame if no data is found.
        """
        start_time = datetime.now() - timedelta(hours=hours)

        try:
            logs = list(self.collection.find(
                {'timestamp': {'$gte': start_time}},
                {'_id': 0}
            ))
        except Exception as e:
            print(f"⚠️ Error retrieving logs: {e}")
            return pd.DataFrame()

        if logs:
            df = pd.DataFrame(logs)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df

        return pd.DataFrame()

    # ------------------- ANALYTICS FUNCTIONS -------------------

    def calculate_statistics(self):
        """Calculate real-time log statistics for the past hour."""
        df = self.get_logs_dataframe(hours=1)

        if df.empty:
            return None

        # Safeguard for missing columns
        for col in ['level', 'service', 'response_time']:
            if col not in df.columns:
                df[col] = None

        stats = {
            'total_logs': len(df),
            'log_levels': df['level'].value_counts().to_dict(),
            'services': df['service'].value_counts().to_dict(),
            'avg_response_time': df['response_time'].mean() if not df['response_time'].isnull().all() else None,
            'max_response_time': df['response_time'].max() if not df['response_time'].isnull().all() else None,
            'min_response_time': df['response_time'].min() if not df['response_time'].isnull().all() else None,
            'error_count': len(df[df['level'].isin(['ERROR', 'CRITICAL'])]),
            'timestamp': datetime.now().isoformat()
        }
        return stats

    def detect_anomalies(self):
        """Detect anomalies in log data such as high response time or high error rate."""
        df = self.get_logs_dataframe(hours=1)

        if df.empty or len(df) < 10 or 'response_time' not in df.columns:
            return []

        anomalies = []

        # High response time anomaly
        if df['response_time'].notnull().any():
            avg_response = df['response_time'].mean()
            std_response = df['response_time'].std() or 0
            threshold = avg_response + (2 * std_response)

            slow_requests = df[df['response_time'] > threshold]
            if len(slow_requests) > 0:
                anomalies.append({
                    'type': 'High Response Time',
                    'count': len(slow_requests),
                    'threshold': round(threshold, 2),
                    'avg_value': round(slow_requests['response_time'].mean(), 2)
                })

        # High error rate anomaly
        if 'level' in df.columns:
            error_rate = (len(df[df['level'] == 'ERROR']) / len(df)) * 100
            if error_rate > 15:  # more than 15% errors
                anomalies.append({
                    'type': 'High Error Rate',
                    'rate': round(error_rate, 2),
                    'count': len(df[df['level'] == 'ERROR'])
                })

        return anomalies

    def get_peak_hours(self):
        """Identify peak usage hours in the last 24 hours."""
        df = self.get_logs_dataframe(hours=24)
        if df.empty or 'timestamp' not in df.columns:
            return {}

        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        hourly_counts = df['hour'].value_counts().sort_index()

        return hourly_counts.to_dict()

    def get_frequent_errors(self, top_n=5):
        """Return the most frequent error messages from the past 24 hours."""
        df = self.get_logs_dataframe(hours=24)
        if df.empty or 'level' not in df.columns or 'message' not in df.columns:
            return []

        error_df = df[df['level'].isin(['ERROR', 'CRITICAL'])]
        if error_df.empty:
            return []

        error_counts = error_df['message'].value_counts().head(top_n)
        return [{'message': msg, 'count': int(count)} for msg, count in error_counts.items()]

    # ------------------- REPORT GENERATION -------------------

    def generate_report(self):
        """Generate a comprehensive analytics report and save as JSON."""
        stats = self.calculate_statistics()
        anomalies = self.detect_anomalies()
        peak_hours = self.get_peak_hours()
        frequent_errors = self.get_frequent_errors()

        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': stats,
            'anomalies': anomalies,
            'peak_hours': peak_hours,
            'frequent_errors': frequent_errors
        }

        # Save report to JSON file
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"../outputs/reports/report_{timestamp_str}.json"

        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n✅ Report generated successfully: {report_file}")
        except Exception as e:
            print(f"⚠️ Failed to save report: {e}")

        return report


# ------------------- MAIN SCRIPT -------------------

if __name__ == "__main__":
    # Load configuration file
    try:
        with open('../config/config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("❌ Config file not found at '../config/config.json'")

    processor = LogProcessor(config)
    report = processor.generate_report()

    print("\n=== 📊 Analytics Summary ===")
    if report.get('statistics'):
        stats = report['statistics']
        print(f"Total Logs (last hour): {stats['total_logs']}")
        print(f"Error Count: {stats['error_count']}")
        if stats['avg_response_time'] is not None:
            print(f"Avg Response Time: {stats['avg_response_time']:.2f} ms")

    if report.get('anomalies'):
        print("\n=== ⚠️ Anomalies Detected ===")
        for anomaly in report['anomalies']:
            print(f"- {anomaly}")
