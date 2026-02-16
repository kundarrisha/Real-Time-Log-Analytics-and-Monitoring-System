import json
from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta

# Load config
with open('../config/config.json', 'r') as f:
    config = json.load(f)

# Connect to MongoDB
mongo_config = config['mongodb']
client = MongoClient(f"mongodb://{mongo_config['host']}:{mongo_config['port']}")
db = client[mongo_config['database']]
collection = db[mongo_config['collection']]

# Get last 24 hours of data
start_time = datetime.now() - timedelta(hours=24)
logs = list(collection.find({'timestamp': {'$gte': start_time}}, {'_id': 0}))

# Convert to DataFrame and export
df = pd.DataFrame(logs)
output_file = '../outputs/powerbi_export.csv'
df.to_csv(output_file, index=False)

print(f"Exported {len(df)} records to {output_file}")
print("Import this file into Power BI Desktop")