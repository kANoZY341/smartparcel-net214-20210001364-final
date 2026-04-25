import json, os, uuid
import boto3
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")

TABLE_NAME = os.environ["TABLE_NAME"]
QUEUE_URL = os.environ["QUEUE_URL"]
table = dynamodb.Table(TABLE_NAME)

VALID_STATUSES = ["registered", "picked_up", "in_transit", "delivered"]

def response(code, body):
    return {
        "statusCode": code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }

def parse_body(event):
    body = event.get("body") or "{}"
    if len(body.encode("utf-8")) > 10240:
        raise ValueError("Payload too large. Maximum allowed size is 10 KB.")
    try:
        return json.loads(body)
    except Exception:
        raise ValueError("Invalid JSON body")

def role(event):
    headers = event.get("headers") or {}
    return headers.get("X-User-Role") or headers.get("x-user-role") or ""

def require_role(event, allowed):
    user_role = role(event)
    return user_role in allowed

def require_fields(body, fields):
    for field in fields:
        if field not in body or body[field] in ["", None]:
            raise ValueError(f"Missing field: {field}")

def lambda_handler(event, context):
    try:
        method = event.get("httpMethod")
        path = event.get("resource")
        params = event.get("pathParameters") or {}

        if method == "POST" and path == "/parcels":
            if not require_role(event, ["driver", "admin"]):
                return response(403, {"error": "Forbidden"})
            return create_parcel(event)

        if method == "GET" and path == "/parcels/{id}":
            if not require_role(event, ["driver", "customer", "admin"]):
                return response(403, {"error": "Forbidden"})
            return get_parcel(params.get("id"))

        if method == "GET" and path == "/parcels":
            if not require_role(event, ["admin"]):
                return response(403, {"error": "Forbidden"})
            return list_parcels(event)

        if method == "PUT" and path == "/parcels/{id}/status":
            if not require_role(event, ["driver"]):
                return response(403, {"error": "Forbidden"})
            return update_status(event, params.get("id"))

        if method == "DELETE" and path == "/parcels/{id}":
            if not require_role(event, ["admin"]):
                return response(403, {"error": "Forbidden"})
            return delete_parcel(params.get("id"))

        return response(404, {"error": "Not found"})

    except ValueError as e:
        return response(400, {"error": str(e)})
    except Exception as e:
        print("ERROR:", str(e))
        return response(500, {"error": "Internal server error"})

def create_parcel(event):
    body = parse_body(event)
    require_fields(body, ["sender", "receiver", "address", "email"])

    parcel_id = "PKG-" + datetime.now().strftime("%Y") + "-" + uuid.uuid4().hex[:8].upper()
    now = datetime.now(timezone.utc).isoformat()

    item = {
        "parcel_id": parcel_id,
        "sender": body["sender"],
        "receiver": body["receiver"],
        "address": body["address"],
        "customer_email": body["email"],
        "status": "registered",
        "created_at": now,
        "updated_at": now
    }

    table.put_item(Item=item)
    return response(201, item)

def get_parcel(parcel_id):
    result = table.get_item(Key={"parcel_id": parcel_id})
    item = result.get("Item")
    if not item:
        return response(404, {"error": "Parcel not found"})
    return response(200, item)

def list_parcels(event):
    query = event.get("queryStringParameters") or {}
    status = query.get("status")

    if status:
        if status not in VALID_STATUSES:
            return response(400, {"error": "Invalid status"})
        result = table.query(
            IndexName="status-index",
            KeyConditionExpression=Key("status").eq(status)
        )
    else:
        result = table.scan()

    return response(200, {"items": result.get("Items", [])})

def update_status(event, parcel_id):
    body = parse_body(event)
    require_fields(body, ["status"])

    new_status = body["status"]
    if new_status not in VALID_STATUSES:
        return response(400, {"error": "Invalid status"})

    result = table.get_item(Key={"parcel_id": parcel_id})
    item = result.get("Item")
    if not item:
        return response(404, {"error": "Parcel not found"})

    old_status = item["status"]
    if VALID_STATUSES.index(new_status) <= VALID_STATUSES.index(old_status):
        return response(409, {"error": "Status can only move forward"})

    now = datetime.now(timezone.utc).isoformat()

    table.update_item(
        Key={"parcel_id": parcel_id},
        UpdateExpression="SET #s = :s, updated_at = :u",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": new_status, ":u": now}
    )

    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps({
            "parcel_id": parcel_id,
            "new_status": new_status,
            "customer_email": item["customer_email"],
            "timestamp": now
        })
    )

    item["status"] = new_status
    item["updated_at"] = now
    return response(200, item)

def delete_parcel(parcel_id):
    result = table.get_item(Key={"parcel_id": parcel_id})
    item = result.get("Item")
    if not item:
        return response(404, {"error": "Parcel not found"})

    if item["status"] != "registered":
        return response(409, {"error": "Only registered parcels can be cancelled"})

    table.delete_item(Key={"parcel_id": parcel_id})
    return response(200, {"message": "Parcel cancelled", "parcel_id": parcel_id})

