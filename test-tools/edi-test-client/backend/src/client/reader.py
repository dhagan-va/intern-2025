import boto3
from pathlib import Path

PAYLOADS_DIR = Path(__file__).parent / "payloads"

def get_s3_batch(count, bucket_name, prefix=""):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix, MaxKeys=count)
    
    return [obj['Key'] for obj in response.get('Contents', [])]

def store_s3_batch(count, bucket_name, prefix=""):
    PAYLOADS_DIR.mkdir(parents=True, exist_ok=True)
    
    object_keys = get_s3_batch(count, bucket_name, prefix)
    
    if not object_keys:
        return []
    
    s3 = boto3.client('s3')
    downloaded_files = []
    
    for key in object_keys:
        local_filename = PAYLOADS_DIR / key.replace('/', '_')
        
        s3.download_file(bucket_name, key, str(local_filename))
        downloaded_files.append(str(local_filename))
    
    return downloaded_files

print(store_s3_batch(5, "edi-test-client"))