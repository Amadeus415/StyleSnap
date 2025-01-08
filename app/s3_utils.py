import boto3
from flask import current_app
from botocore.exceptions import ClientError
import uuid
import base64
import re

# This file is used to interact with the S3 bucket.
# 
# S3 Uses a flat file structure.


def get_s3_client():
    """Get S3 client with credentials"""
    return boto3.client(
        's3',
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'], # Access limited by IAM user.
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['AWS_REGION']
    ) # Returns: <botocore.client.S3 object at 0x0000022222222222> an object that has methods like put_object, generate_presigned_url, etc. And other ways to interact with S3.


def upload_file_to_s3(file_data, user_id, is_base64=False):
    """
    Upload an image file to AWS S3 bucket.
    
    Args:
        file_data: Either a file object or base64 encoded string
        user_id: User identifier for file organization
        is_base64: Flag indicating if input is base64 encoded
    
    Returns:
        tuple: (s3_key, s3_url) where s3_key is the file path in S3 and 
               s3_url is the public access URL
    """
    try:
        # Initialize S3 client using AWS credentials
        s3_client = get_s3_client()
        
        # Generate unique filename using UUID to prevent collisions
        filename = f"{uuid.uuid4()}.jpg"
        
        # Create S3 key with organized folder structure: users/[user_id]/photos/[filename]
        s3_key = f"users/{user_id}/photos/{filename}"
        
        if is_base64:
            try:
                # Handle base64 encoded input
                if isinstance(file_data, str):
                    # Remove metadata prefix if present (e.g., "data:image/jpeg;base64,")
                    if 'data:image' in file_data and 'base64,' in file_data:
                        file_data = file_data.split('base64,')[1]
                    
                    # Clean the base64 string by removing whitespace and line breaks
                    file_data = file_data.strip().replace('\n', '').replace('\r', '')
                    
                    # Validate JPEG signature in base64 (/9j/ is the base64 encoding of JPEG SOI marker)
                    if not file_data.startswith('/9j/'):
                        raise ValueError("Invalid base64 image data")
                    
                    # Add padding ('=') if needed for valid base64 string length
                    missing_padding = len(file_data) % 4
                    if missing_padding:
                        file_data += '=' * (4 - missing_padding)
                    
                    # Convert base64 string to bytes
                    file_bytes = base64.b64decode(file_data)
                else:
                    raise ValueError("Base64 data must be a string")
            except Exception as e:
                # Log detailed error information for debugging
                current_app.logger.error(f"Base64 processing error: {str(e)}")
                current_app.logger.error(f"Data type: {type(file_data)}")
                raise
        else:
            # Handle regular file upload by reading file content
            file_bytes = file_data.read()
        
        # Upload file bytes to S3 bucket
        s3_client.put_object(
            Bucket=current_app.config['AWS_BUCKET_NAME'],
            Key=s3_key,
            Body=file_bytes,
            ContentType='image/jpeg'  # Set content type for proper browser handling
        )
        
        # Generate public URL for the uploaded file
        s3_url = f"https://{current_app.config['AWS_BUCKET_NAME']}.s3.{current_app.config['AWS_REGION']}.amazonaws.com/{s3_key}"
        return s3_key, s3_url
        
    except Exception as e:
        # Log any errors during the upload process
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