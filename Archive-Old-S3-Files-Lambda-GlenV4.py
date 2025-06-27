import boto3
import os
from datetime import datetime, timezone, timedelta

# Config
BUCKET_NAME = os.environ['S3_BUCKET_NAME']  
MONTHS_THRESHOLD = os.environ['MONTHS_THRESHOLD']
STORAGE_CLASS = os.environ['STORAGE_CLASS']

s3 = boto3.client('s3')

def lambda_handler(event, context):
    threshold_date = datetime.now(timezone.utc) - timedelta(days=MONTHS_THRESHOLD * 30)
    archived_files = []

    response = s3.list_objects_v2(Bucket=BUCKET_NAME)

    if 'Contents' not in response:
        print("Bucket is empty.")
        return

    for obj in response['Contents']:
        key = obj['Key']
        last_modified = obj['LastModified']
        storage_class = obj.get('StorageClass', 'STANDARD')

        if last_modified < threshold_date and storage_class == 'STANDARD':
            print(f"Archiving file: {key} (LastModified: {last_modified})")

            # Copy same object to same key with new storage class
            s3.copy_object(
                Bucket=BUCKET_NAME,
                Key=key,
                CopySource={'Bucket': BUCKET_NAME, 'Key': key},
                StorageClass=STORAGE_CLASS,
                MetadataDirective='COPY'
            )

            archived_files.append(key)

    print(f"Archived {len(archived_files)} file(s): {archived_files}")

    return {
        'statusCode': 200,
        'body': f"Archived {len(archived_files)} files to Glacier."
    }
