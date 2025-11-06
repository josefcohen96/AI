import os, json, boto3
from decimal import Decimal

s3 = boto3.client('s3')
dynamo = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])
BUCKET = os.environ['BUCKET_NAME']

def load_food_db():
    # טוען nutrition/foods.json שנפרוס יחד עם הקוד
    import importlib.resources as r
    with r.files("nutrition").joinpath("foods.json").open() as f:
        return json.load(f)

FOOD_DB = load_food_db()
PORTION_TO_GRAMS = {"small":60, "medium":120, "large":200}

def guess_items_from_key(key:str):
    # MVP: ניחוש גס לפי שם הקובץ/דמו. בהמשך תחליף ל-AI אמיתי.
    name = key.lower()
    items = []
    if "chicken" in name: items.append({"name":"chicken breast","portion":"medium"})
    if "rice" in name:    items.append({"name":"rice cooked","portion":"medium"})
    if "broccoli" in name:items.append({"name":"broccoli","portion":"small"})
    if not items:
        items = [{"name":"rice cooked","portion":"medium"}]
    return items

def macro_for_item(name:str, portion:str):
    grams = PORTION_TO_GRAMS.get(portion, 120)
    info = FOOD_DB.get(name.lower())
    factor = grams/100.0
    if not info:
        return {"name":name, "grams":grams, "kcal":None,"protein":None,"carbs":None,"fat":None}
    return {
        "name": name, "grams": grams,
        "kcal": round(info["kcal"]*factor),
        "protein": round(info["protein"]*factor,1),
        "carbs": round(info["carbs"]*factor,1),
        "fat": round(info["fat"]*factor,1)
    }

def lambda_handler(event, context):
    for rec in event["Records"]:
        key = rec["s3"]["object"]["key"]
        image_id = key.split("/")[-1].split(".")[0]

        # כאן בהמשך: הורד את ה-binary, שלח ל-Bedrock/‏Rekognition
        # obj = s3.get_object(Bucket=BUCKET, Key=key)
        # image_bytes = obj["Body"].read()
        items = guess_items_from_key(key)

        macros = [macro_for_item(i["name"], i.get("portion","medium")) for i in items]
        total = {"kcal":0,"protein":0,"carbs":0,"fat":0}
        for m in macros:
            for k in total:
                if m[k] is not None: total[k]+=m[k]

        result = {"imageId": image_id, "items": macros, "total": total}
        dynamo.put_item(Item=json.loads(json.dumps(result), parse_float=Decimal))

    return {"statusCode":200}
