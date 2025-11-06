import os, json, boto3
dynamo = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])

def lambda_handler(event, context):
    image_id = event["pathParameters"]["imageId"]
    resp = dynamo.get_item(Key={"imageId": image_id})
    item = resp.get("Item")
    return {
        "statusCode": 200 if item else 404,
        "headers": {"content-type":"application/json"},
        "body": json.dumps(item or {"error":"not found"})
    }
