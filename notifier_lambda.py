import json, os
import boto3

sns = boto3.client("sns")
TOPIC_ARN = os.environ["TOPIC_ARN"]

def lambda_handler(event, context):
    for record in event.get("Records", []):
        try:
            body = json.loads(record["body"])
            parcel_id = body["parcel_id"]
            new_status = body["new_status"]
            customer_email = body.get("customer_email", "customer")

            message = f"SmartParcel update: Parcel {parcel_id} is now {new_status}. Customer: {customer_email}"

            sns.publish(
                TopicArn=TOPIC_ARN,
                Subject="SmartParcel Status Update",
                Message=message
            )

        except Exception as e:
            print("Malformed message skipped:", str(e))
            continue

    return {"statusCode": 200}

