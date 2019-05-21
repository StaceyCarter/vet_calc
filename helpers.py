import boto3, botocore
import os

S3_BUCKET = os.environ.get('S3_BUCKET')
S3_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
S3_SECRET = os.environ.get('AWS_SECRET_KEY')
S3_LOCATION = f'http://{S3_BUCKET}.s3.amazonaws.com/'

s3 = boto3.client(
    "s3",
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET
)

def upload_file_to_s3(file, acl="public-read"):
    print("file type: ", type(file))
    print("bucket type: ", type(S3_BUCKET))
    print("Key type: ", type(acl))
    try:
        s3.upload_fileobj(
            file,
            S3_BUCKET,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except Exception as e:
        print("oh no....", e)
        return e

    return f"{S3_LOCATION}{file.filname}"
