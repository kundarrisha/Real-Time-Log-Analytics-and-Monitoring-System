import time
from hdfs import InsecureClient

# HDFS settings
HDFS_URL = 'http://localhost:9870'  # NameNode WebHDFS URL
HDFS_USER = 'Dell'
HDFS_DIR = '/logs'
HDFS_FILE = f'{HDFS_DIR}/application.log'

# Local log path
LOCAL_LOG_PATH = r"C:\Users\Dell\Documents\RealTimeLogAnalysis\logs\application.log"

# Connect to HDFS
client = InsecureClient(HDFS_URL, user=HDFS_USER)

# Ensure HDFS directory exists
if not client.status(HDFS_DIR, strict=False):
    client.makedirs(HDFS_DIR)
    print(f"✅ Created HDFS directory: {HDFS_DIR}")

# Ensure HDFS file exists
if not client.status(HDFS_FILE, strict=False):
    client.write(HDFS_FILE, '', encoding='utf-8', overwrite=True)
    print(f"✅ Created empty HDFS file: {HDFS_FILE}")

# Track file position
last_position = 0

while True:
    try:
        with open(LOCAL_LOG_PATH, 'r', encoding='utf-8') as f:
            # Move to last read position
            f.seek(last_position)
            # Read new lines
            new_lines = f.readlines()
            # Update file position
            last_position = f.tell()

            if new_lines:
                # Append new lines to HDFS file
                client.write(HDFS_FILE, ''.join(new_lines), encoding='utf-8', append=True)
                print(f"✅ Uploaded {len(new_lines)} new lines to HDFS")
            else:
                print("ℹ️ No new lines to upload")

    except FileNotFoundError:
        print(f"❌ Local log file not found: {LOCAL_LOG_PATH}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")

    time.sleep(5)  # Check for new logs every 5 seconds
