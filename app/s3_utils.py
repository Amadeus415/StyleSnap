import boto3
from flask import current_app
from botocore.exceptions import ClientError
import uuid
import base64
import re

def get_s3_client():
    """Get S3 client with credentials"""
    return boto3.client(
        's3',
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['AWS_REGION']
    )

def upload_file_to_s3(file_data, user_id, is_base64=False):
    """Upload file to S3 and return the key and URL"""
    try:
        s3_client = get_s3_client()
        filename = f"{uuid.uuid4()}.jpg"
        s3_key = f"users/{user_id}/photos/{filename}"
        
        if is_base64:
            try:
                # Clean up the base64 string
                if isinstance(file_data, str):
                    # Remove data URL prefix if present
                    if 'data:image' in file_data and 'base64,' in file_data:
                        file_data = file_data.split('base64,')[1]
                    
                    # Remove any whitespace and newlines
                    file_data = file_data.strip().replace('\n', '').replace('\r', '')
                    
                    
                    # Validate that this looks like base64 image data
                    if not file_data.startswith('/9j/'):  # JPEG signature in base64
                        raise ValueError("Invalid base64 image data")
                    
                    # Add padding if needed
                    missing_padding = len(file_data) % 4
                    if missing_padding:
                        file_data += '=' * (4 - missing_padding)
                    
                    # Decode base64
                    file_bytes = base64.b64decode(file_data)
                else:
                    raise ValueError("Base64 data must be a string")
            except Exception as e:
                current_app.logger.error(f"Base64 processing error: {str(e)}")
                current_app.logger.error(f"Data type: {type(file_data)}")
                raise
        else:
            file_bytes = file_data.read()
        
        # Upload to S3
        s3_client.put_object(
            Bucket=current_app.config['AWS_BUCKET_NAME'],
            Key=s3_key,
            Body=file_bytes,
            ContentType='image/jpeg'
        )
        
        # Generate URL
        s3_url = f"https://{current_app.config['AWS_BUCKET_NAME']}.s3.{current_app.config['AWS_REGION']}.amazonaws.com/{s3_key}"
        return s3_key, s3_url
        
    except Exception as e:
        current_app.logger.error(f"Error uploading to S3: {str(e)}")
        raise

def delete_file_from_s3(s3_key):
    """Delete file from S3"""
    try:
        s3_client = get_s3_client()
        s3_client.delete_object(
            Bucket=current_app.config['AWS_BUCKET_NAME'],
            Key=s3_key
        )
    except Exception as e:
        current_app.logger.error(f"Error deleting from S3: {str(e)}")
        raise