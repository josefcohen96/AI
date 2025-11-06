import os, json, boto3, uuid
s3 = boto3.client('s3')
BUCKET = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    image_id = str(uuid.uuid4())
    key = f"uploads/{image_id}.jpg"
    url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={'Bucket': BUCKET, 'Key': key, 'ContentType': 'image/jpeg'},
        ExpiresIn=300
    )
    return {
        "statusCode": 200,
        "headers": {"content-type":"application/json"},
        "body": json.dumps({"uploadUrl": url, "imageId": image_id, "key": key})
    }
