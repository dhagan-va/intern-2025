import boto3

def get_s3_batch(count, bucket_name, prefix=""):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix, MaxKeys=count)
    return [obj['Key'] for obj in response.get('Contents', [])]

print(get_s3_batch(5, "edi-test-client"))