import random
import time
import json
from datetime import datetime
from faker import Faker
import os

fake = Faker()

class LogGenerator:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.log_levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG', 'CRITICAL']
        self.services = ['AuthService', 'PaymentService', 'UserService', 
                        'NotificationService', 'DatabaseService']
        self.error_messages = [
            'Connection timeout',
            'Invalid credentials',
            'Database connection failed',
            'Memory limit exceeded',
            'Null pointer exception',
            'Service unavailable',
            'Rate limit exceeded'
        ]
        self.info_messages = [
            'User logged in successfully',
            'Payment processed',
            'Email sent',
            'Cache updated',
            'Request completed'
        ]
        
    def generate_log_entry(self):
        """Generate a single log entry"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        level = random.choices(
            self.log_levels, 
            weights=[60, 20, 10, 8, 2]  # INFO is most common
        )[0]
        service = random.choice(self.services)
        user_id = f"USER_{random.randint(1000, 9999)}"
        ip_address = fake.ipv4()
        
        if level in ['ERROR', 'CRITICAL']:
            message = random.choice(self.error_messages)
            response_time = random.randint(2000, 5000)
        else:
            message = random.choice(self.info_messages)
            response_time = random.randint(50, 500)
        
        log_entry = (
            f"{timestamp} | {level:8} | {service:20} | "
            f"UserID: {user_id} | IP: {ip_address:15} | "
            f"ResponseTime: {response_time}ms | Message: {message}"
        )
        
        return log_entry
    
    def generate_continuous_logs(self, interval=2):
        """Generate logs continuously"""
        print(f"Starting log generation... Writing to {self.log_file_path}")
        print("Press Ctrl+C to stop\n")
        
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                while True:
                    # Generate 5-15 logs per batch
                    num_logs = random.randint(5, 15)
                    for _ in range(num_logs):
                        log_entry = self.generate_log_entry()
                        f.write(log_entry + '\n')
                        print(log_entry)
                    
                    f.flush()  # Ensure logs are written immediately
                    time.sleep(interval)
                    
        except KeyboardInterrupt:
            print("\nLog generation stopped.")

if __name__ == "__main__":
    # Load config
    with open('../config/config.json', 'r') as f:
        config = json.load(f)
    
    log_dir = config['log_settings']['log_directory']
    log_file = config['log_settings']['log_file']
    log_path = os.path.join(log_dir, log_file)
    print("✅ Log directory:", log_dir)
    print("✅ Log file:", log_file)
    print("✅ Full path:", log_path)
    
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)
    
    generator = LogGenerator(log_path)
    generator.generate_continuous_logs(
        interval=config['log_settings']['generation_interval']
    )