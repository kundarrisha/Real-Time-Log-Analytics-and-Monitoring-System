import time
import re
import json
from datetime import datetime
from pymongo import MongoClient
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

class LogIngestion:
    def __init__(self, config):
        self.config = config
        mongo_config = config['mongodb']
        
        # Connect to MongoDB
        self.client = MongoClient(
            f"mongodb://{mongo_config['host']}:{mongo_config['port']}"
        )
        self.db = self.client[mongo_config['database']]
        self.collection = self.db[mongo_config['collection']]
        
        # Create indexes for better query performance
        self.collection.create_index([('timestamp', -1)])
        self.collection.create_index([('level', 1)])
        self.collection.create_index([('service', 1)])
        
        self.log_file_path = os.path.join(
            config['log_settings']['log_directory'],
            config['log_settings']['log_file']
        )
        self.last_position = 0
        
    def parse_log_line(self, line):
        """Parse a log line into structured data"""
        pattern = (
            r'(?P<timestamp>[\d\-\: \.]+) \| '
            r'(?P<level>\w+)\s+\| '
            r'(?P<service>[\w]+)\s+\| '
            r'UserID: (?P<user_id>[\w_]+) \| '
            r'IP: (?P<ip_address>[\d\.]+)\s+\| '
            r'ResponseTime: (?P<response_time>\d+)ms \| '
            r'Message: (?P<message>.+)'
        )
        
        match = re.match(pattern, line)
        if match:
            data = match.groupdict()
            # Convert timestamp to datetime object
            data['timestamp'] = datetime.strptime(
                data['timestamp'], 
                '%Y-%m-%d %H:%M:%S.%f'
            )
            data['response_time'] = int(data['response_time'])
            data['ingestion_time'] = datetime.now()
            return data
        return None
    
    def ingest_logs(self):
        """Read and ingest logs from file"""
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                # Seek to last read position
                f.seek(self.last_position)
                
                lines = f.readlines()
                if lines:
                    parsed_logs = []
                    for line in lines:
                        line = line.strip()
                        if line:
                            parsed_log = self.parse_log_line(line)
                            if parsed_log:
                                parsed_logs.append(parsed_log)
                    
                    if parsed_logs:
                        self.collection.insert_many(parsed_logs)
                        print(f"Ingested {len(parsed_logs)} log entries")
                
                # Update position
                self.last_position = f.tell()
                
        except FileNotFoundError:
            print(f"Log file not found: {self.log_file_path}")
        except Exception as e:
            print(f"Error ingesting logs: {e}")
    
    def start_continuous_ingestion(self, interval=5):
        """Continuously ingest logs at specified interval"""
        print(f"Starting log ingestion from {self.log_file_path}")
        print(f"Storing in MongoDB: {self.config['mongodb']['database']}")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.ingest_logs()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nLog ingestion stopped.")
            self.client.close()

if __name__ == "__main__":
    # Load config
    with open('../config/config.json', 'r') as f:
        config = json.load(f)
    
    ingestion = LogIngestion(config)
    ingestion.start_continuous_ingestion(interval=3)