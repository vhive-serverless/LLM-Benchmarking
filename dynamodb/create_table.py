import boto3
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to DynamoDB
dynamodb = boto3.resource(
    "dynamodb",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

# Define table name and schema
table_name = "BenchmarkMetrics"

try:
    # Create the table
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                "AttributeName": "id",  # Partition key
                "KeyType": "HASH",  # Partition key type
            },
            {
                "AttributeName": "timestamp",  # Composite sort key
                "KeyType": "RANGE",  # Sort key type
            },
        ],
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "timestamp", "AttributeType": "S"},  # Define sort_key
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    # Wait until the table exists
    table.meta.client.get_waiter("table_exists").wait(TableName=table_name)
    print(f"Table '{table_name}' created successfully.")

except dynamodb.meta.client.exceptions.ResourceInUseException:
    print(f"Table '{table_name}' already exists.")
