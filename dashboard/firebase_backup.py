"""
Firebase Backup Service for Weather Dashboard
Handles automatic backup of sensor data to Firebase Firestore
"""

import firebase_admin
from firebase_admin import credentials, firestore
import sqlite3
import json
import logging
from datetime import datetime, timedelta
import threading
import time
import os
from typing import Dict, List, Optional

class FirebaseBackupService:
    def __init__(self, config_path: str = None, db_path: str = "weather.db"):
        """
        Initialize Firebase Backup Service
        
        Args:
            config_path: Path to Firebase service account JSON file
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.config_path = config_path
        self.db = None
        self.backup_enabled = False
        self.backup_thread = None
        self.stop_backup = threading.Event()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize Firebase if config is provided
        if config_path and os.path.exists(config_path):
            self.initialize_firebase(config_path)
    
    def initialize_firebase(self, config_path: str) -> bool:
        """Initialize Firebase Admin SDK"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(config_path)
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            self.backup_enabled = True
            self.logger.info("Firebase initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Firebase: {e}")
            self.backup_enabled = False
            return False
    
    def get_local_data(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Retrieve data from local SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            query = "SELECT * FROM sensor_data"
            params = []
            
            if start_date and end_date:
                query += " WHERE timestamp BETWEEN ? AND ?"
                params = [start_date, end_date]
            elif start_date:
                query += " WHERE timestamp >= ?"
                params = [start_date]
            
            query += " ORDER BY timestamp ASC"
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            data = []
            for row in rows:
                data.append({
                    'id': row['id'],
                    'timestamp': row['timestamp'],
                    'temperature': row['temperature'],
                    'humidity': row['humidity'],
                    'pressure': row['pressure'] if row['pressure'] else None
                })
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error retrieving local data: {e}")
            return []
    
    def backup_single_record(self, record: Dict) -> bool:
        """Backup a single sensor record to Firebase"""
        if not self.backup_enabled or not self.db:
            return False
        
        try:
            # Use timestamp as document ID to avoid duplicates
            doc_id = f"{record['timestamp'].replace(' ', '_').replace(':', '-')}"
            
            # Prepare document data
            doc_data = {
                'local_id': record['id'],
                'timestamp': record['timestamp'],
                'temperature': record['temperature'],
                'humidity': record['humidity'],
                'backup_time': datetime.now().isoformat(),
                'source': 'weather_dashboard'
            }
            
            if record.get('pressure'):
                doc_data['pressure'] = record['pressure']
            
            # Store in Firestore
            self.db.collection('sensor_data').document(doc_id).set(doc_data, merge=True)
            self.logger.info(f"Backed up record: {record['timestamp']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error backing up record {record['id']}: {e}")
            return False
    
    def backup_batch(self, records: List[Dict]) -> int:
        """Backup multiple records in a batch"""
        if not self.backup_enabled or not self.db:
            return 0
        
        success_count = 0
        batch = self.db.batch()
        
        try:
            for record in records:
                doc_id = f"{record['timestamp'].replace(' ', '_').replace(':', '-')}"
                doc_ref = self.db.collection('sensor_data').document(doc_id)
                
                doc_data = {
                    'local_id': record['id'],
                    'timestamp': record['timestamp'],
                    'temperature': record['temperature'],
                    'humidity': record['humidity'],
                    'backup_time': datetime.now().isoformat(),
                    'source': 'weather_dashboard'
                }
                
                if record.get('pressure'):
                    doc_data['pressure'] = record['pressure']
                
                batch.set(doc_ref, doc_data, merge=True)
                success_count += 1
            
            # Commit the batch
            batch.commit()
            self.logger.info(f"Successfully backed up {success_count} records in batch")
            return success_count
            
        except Exception as e:
            self.logger.error(f"Error in batch backup: {e}")
            return 0
    
    def full_backup(self) -> bool:
        """Perform a full backup of all local data"""
        if not self.backup_enabled:
            self.logger.warning("Firebase backup not enabled")
            return False
        
        try:
            self.logger.info("Starting full backup...")
            data = self.get_local_data()
            
            if not data:
                self.logger.warning("No data to backup")
                return True
            
            # Backup in batches of 500 (Firestore limit)
            batch_size = 500
            total_backed_up = 0
            
            for i in range(0, len(data), batch_size):
                batch_data = data[i:i + batch_size]
                backed_up = self.backup_batch(batch_data)
                total_backed_up += backed_up
                
                # Small delay between batches
                time.sleep(0.5)
            
            self.logger.info(f"Full backup completed: {total_backed_up}/{len(data)} records")
            return total_backed_up == len(data)
            
        except Exception as e:
            self.logger.error(f"Error in full backup: {e}")
            return False
    
    def incremental_backup(self, hours_back: int = 24) -> bool:
        """Backup only recent data"""
        if not self.backup_enabled:
            return False
        
        try:
            # Get data from last N hours
            start_time = (datetime.now() - timedelta(hours=hours_back)).strftime('%Y-%m-%d %H:%M:%S')
            data = self.get_local_data(start_date=start_time)
            
            if not data:
                self.logger.info("No recent data to backup")
                return True
            
            success = self.backup_batch(data)
            self.logger.info(f"Incremental backup: {success}/{len(data)} records")
            return success == len(data)
            
        except Exception as e:
            self.logger.error(f"Error in incremental backup: {e}")
            return False
    
    def start_automatic_backup(self, interval_minutes: int = 60):
        """Start automatic backup service"""
        if not self.backup_enabled:
            self.logger.warning("Cannot start automatic backup - Firebase not initialized")
            return False
        
        if self.backup_thread and self.backup_thread.is_alive():
            self.logger.warning("Automatic backup already running")
            return False
        
        self.stop_backup.clear()
        self.backup_thread = threading.Thread(
            target=self._backup_worker,
            args=(interval_minutes,),
            daemon=True
        )
        self.backup_thread.start()
        self.logger.info(f"Started automatic backup every {interval_minutes} minutes")
        return True
    
    def stop_automatic_backup(self):
        """Stop automatic backup service"""
        self.stop_backup.set()
        if self.backup_thread:
            self.backup_thread.join(timeout=5)
        self.logger.info("Stopped automatic backup service")
    
    def _backup_worker(self, interval_minutes: int):
        """Worker thread for automatic backup"""
        while not self.stop_backup.is_set():
            try:
                # Perform incremental backup every interval
                self.incremental_backup(hours_back=interval_minutes * 60 // 60 + 1)
                
                # Wait for next interval or stop signal
                self.stop_backup.wait(timeout=interval_minutes * 60)
                
            except Exception as e:
                self.logger.error(f"Error in backup worker: {e}")
                # Wait a bit before retrying
                self.stop_backup.wait(timeout=300)  # 5 minutes
    
    def get_backup_status(self) -> Dict:
        """Get current backup status and statistics"""
        status = {
            'enabled': self.backup_enabled,
            'automatic_running': self.backup_thread and self.backup_thread.is_alive(),
            'last_check': datetime.now().isoformat()
        }
        
        if self.backup_enabled:
            try:
                # Get local data count
                local_data = self.get_local_data()
                status['local_records'] = len(local_data)
                
                # Get Firebase data count
                firebase_count = len(self.db.collection('sensor_data').get())
                status['firebase_records'] = firebase_count
                status['sync_status'] = 'synced' if len(local_data) == firebase_count else 'out_of_sync'
                
            except Exception as e:
                status['error'] = str(e)
        
        return status
    
    def restore_from_firebase(self, start_date: str = None, end_date: str = None) -> int:
        """Restore data from Firebase to local database (emergency recovery)"""
        if not self.backup_enabled:
            return 0
        
        try:
            # Query Firebase
            query = self.db.collection('sensor_data')
            
            if start_date:
                query = query.where('timestamp', '>=', start_date)
            if end_date:
                query = query.where('timestamp', '<=', end_date)
            
            docs = query.get()
            
            # Restore to local database
            conn = sqlite3.connect(self.db_path)
            restored_count = 0
            
            for doc in docs:
                data = doc.to_dict()
                try:
                    conn.execute('''
                        INSERT OR REPLACE INTO sensor_data 
                        (timestamp, temperature, humidity, pressure)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        data['timestamp'],
                        data['temperature'],
                        data['humidity'],
                        data.get('pressure')
                    ))
                    restored_count += 1
                except Exception as e:
                    self.logger.error(f"Error restoring record: {e}")
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Restored {restored_count} records from Firebase")
            return restored_count
            
        except Exception as e:
            self.logger.error(f"Error restoring from Firebase: {e}")
            return 0


# Convenience functions for integration
def create_firebase_config_template(output_path: str = "firebase_config_template.json"):
    """Create a template for Firebase configuration"""
    template = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project-id.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
    }
    
    with open(output_path, 'w') as f:
        json.dump(template, f, indent=2)
    
    print(f"Firebase config template created at: {output_path}")
    print("Please replace the placeholder values with your actual Firebase service account credentials")


if __name__ == "__main__":
    # Example usage
    backup_service = FirebaseBackupService()
    
    # Create config template if it doesn't exist
    if not os.path.exists("firebase_config.json"):
        create_firebase_config_template("firebase_config.json")
        print("Please configure firebase_config.json with your credentials and run again")
    else:
        # Initialize with config
        backup_service.initialize_firebase("firebase_config.json")
        
        # Perform a full backup
        backup_service.full_backup()
        
        # Start automatic backup
        backup_service.start_automatic_backup(interval_minutes=60)
