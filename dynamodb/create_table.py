import boto3
import os
from dotenv import load_dotenv
load_dotenv()

# Connect to DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=os.getenv("DYNAMODB_ENDPOINT_URL"),
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

# Define table name and schema
table_name = "BenchmarkMetrics"

try:
    # Create the table
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'run_id',  # Unique identifier for each benchmark run
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'timestamp',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'run_id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
    print(f"Table '{table_name}' created successfully.")

except dynamodb.meta.client.exceptions.ResourceInUseException:
    print(f"Table '{table_name}")
