import boto3
from moto import mock_aws

@mock_aws
def test_create_dynamodb_table():
    # Set up the mock DynamoDB environment
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    
    # Run the table creation code
    table = dynamodb.create_table(
        TableName="Testtable",
        KeySchema=[
            {"AttributeName": "run_id", "KeyType": "HASH"},
            {"AttributeName": "timestamp", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "run_id", "AttributeType": "S"},
            {"AttributeName": "timestamp", "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    # Wait until the table exists
    table.meta.client.get_waiter("table_exists").wait(TableName="Testtable")

    # Assertions
    assert table.table_status == "ACTIVE"
    assert table.table_name == "Testtable"

    # Check the table's key schema
    assert table.key_schema == [
        {"AttributeName": "run_id", "KeyType": "HASH"},
        {"AttributeName": "timestamp", "KeyType": "RANGE"},
    ]
