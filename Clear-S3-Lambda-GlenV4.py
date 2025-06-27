import boto3
import os
from datetime import datetime, timezone, timedelta

# Define how many days old the file must be to delete
BUCKET_NAME = os.environ['S3_BUCKET_NAME']

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    deleted_files = []

    # Calculate threshold date
    threshold_date = datetime.now(timezone.utc)

    # List all objects in the bucket
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)


    if 'Contents' in response:
        for obj in response['Contents']:
            key = obj['Key']
            last_modified = obj['LastModified']

            if last_modified < threshold_date:
                # Delete the object
                s3.delete_object(Bucket=BUCKET_NAME, Key=key)
                deleted_files.append(key)

        print(f"Deleted {len(deleted_files)} file(s): {deleted_files}")
    else:
        print("Bucket is empty or no objects found.")

    return {
        'statusCode': 200,
        'body': f"Deleted {len(deleted_files)} file(s)."
    }
