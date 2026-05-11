"""
AWS Cloud Config — Chatbot
Handles S3 chat log storage and cloud status.
"""

import boto3
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class CloudConfig:
    """AWS S3 integration for storing chat logs."""

    def __init__(self):
        self.aws_key = os.getenv('AWS_ACCESS_KEY_ID', '')
        self.aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY', '')
        self.region = os.getenv('AWS_REGION', 'ap-south-1')
        self.bucket = os.getenv('S3_BUCKET_NAME', 'chatbot-system-bucket')
        self.s3 = None
        self._connected = False
        self._init()

    def _init(self):
        try:
            if self.aws_key and self.aws_key != 'your-access-key-id':
                self.s3 = boto3.client('s3',
                    aws_access_key_id=self.aws_key,
                    aws_secret_access_key=self.aws_secret,
                    region_name=self.region
                )
                self.s3.head_bucket(Bucket=self.bucket)
                self._connected = True
                print(f"[AWS] Connected to S3: {self.bucket}")
            else:
                print("[AWS] No credentials — LOCAL mode.")
        except Exception as e:
            print(f"[AWS] Connection failed: {e} — LOCAL mode.")

    def is_connected(self):
        return self._connected

    def save_chat_log(self, session_id, messages):
        """Save chat session to S3."""
        if not self._connected:
            return {'status': 'local_only', 'message': 'Chat saved locally only.'}
        try:
            key = f"chat_logs/{session_id}.json"
            data = {
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'message_count': len(messages),
                'messages': messages
            }
            self.s3.put_object(
                Bucket=self.bucket, Key=key,
                Body=json.dumps(data, indent=2),
                ContentType='application/json'
            )
            return {'status': 'uploaded', 'message': f'Chat log saved to S3: {key}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def get_status(self):
        return {
            'connected': self._connected,
            'region': self.region,
            'bucket': self.bucket,
            'mode': 'AWS S3' if self._connected else 'LOCAL'
        }
