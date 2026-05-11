"""
AWS Cloud Storage Module — S3 Integration
Handles uploading verified data to AWS S3 as JSON backups
and syncing database records to the cloud.
"""

import boto3
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class CloudStorage:
    """Manages AWS S3 operations for data backup and cloud sync."""

    def __init__(self):
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID', '')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY', '')
        self.region = os.getenv('AWS_REGION', 'ap-south-1')
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'data-redundancy-system-bucket')
        self.s3_client = None
        self._connected = False
        self._init_client()

    def _init_client(self):
        """Initialize the AWS S3 client."""
        try:
            if self.aws_access_key and self.aws_access_key != 'your-access-key-id':
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    region_name=self.region
                )
                # Test connection
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                self._connected = True
                print(f"[AWS] Connected to S3 bucket: {self.bucket_name}")
            else:
                print("[AWS] No credentials configured — running in LOCAL mode.")
                print("[AWS] To enable cloud sync, add your AWS keys to .env file.")
        except Exception as e:
            print(f"[AWS] S3 connection failed: {e}")
            print("[AWS] Falling back to LOCAL mode.")
            self._connected = False

    def is_connected(self):
        """Check if AWS S3 is connected."""
        return self._connected

    def upload_record(self, record_data, record_id):
        """Upload a single verified record to S3 as a JSON file."""
        if not self._connected:
            return {
                'status': 'local_only',
                'message': 'Cloud sync disabled — record saved locally only.'
            }

        try:
            key = f"verified_records/{record_id}.json"
            record_data['uploaded_at'] = datetime.utcnow().isoformat()
            record_data['source'] = 'data-redundancy-system'

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(record_data, indent=2),
                ContentType='application/json'
            )

            return {
                'status': 'uploaded',
                'message': f'Record synced to S3: s3://{self.bucket_name}/{key}',
                's3_key': key
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Upload failed: {str(e)}'
            }

    def upload_backup(self, all_records):
        """Upload a full database backup to S3."""
        if not self._connected:
            return {
                'status': 'local_only',
                'message': 'Cloud backup disabled — no AWS credentials.'
            }

        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            key = f"backups/full_backup_{timestamp}.json"

            backup_data = {
                'backup_timestamp': datetime.utcnow().isoformat(),
                'total_records': len(all_records),
                'records': all_records
            }

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(backup_data, indent=2),
                ContentType='application/json'
            )

            return {
                'status': 'uploaded',
                'message': f'Full backup uploaded: s3://{self.bucket_name}/{key}',
                's3_key': key
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Backup failed: {str(e)}'
            }

    def list_cloud_records(self):
        """List all records stored in S3."""
        if not self._connected:
            return {'status': 'local_only', 'records': []}

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='verified_records/'
            )
            records = []
            for obj in response.get('Contents', []):
                records.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                })
            return {'status': 'success', 'records': records}
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'records': []}

    def get_cloud_status(self):
        """Get cloud connection status summary."""
        return {
            'connected': self._connected,
            'region': self.region,
            'bucket': self.bucket_name,
            'mode': 'CLOUD' if self._connected else 'LOCAL'
        }
