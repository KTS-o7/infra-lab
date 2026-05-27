from app.aws_client import get_dynamodb_client

def dynamodb_table_exists(table_name: str) -> dict:
    client = get_dynamodb_client()
    try:
        client.describe_table(TableName=table_name)
        return {"id": "table-exists", "type": "dynamodb_table_exists", "passed": True, "message": f"Table {table_name} exists."}
    except Exception:
        return {"id": "table-exists", "type": "dynamodb_table_exists", "passed": False, "message": f"Table {table_name} was not found."}

def dynamodb_key_schema_equals(table_name: str, partition_key: dict, sort_key: dict = None) -> dict:
    client = get_dynamodb_client()
    try:
        response = client.describe_table(TableName=table_name)
        schema = response["Table"]["KeySchema"]
        expected = [{"KeyType": "HASH", "AttributeName": partition_key["name"]}]
        if sort_key:
            expected.append({"KeyType": "RANGE", "AttributeName": sort_key["name"]})
        actual = {k["AttributeName"]: k["KeyType"] for k in schema}
        expected_dict = {k["AttributeName"]: k["KeyType"] for k in expected}
        if actual == expected_dict:
            return {"id": "key-schema", "type": "dynamodb_key_schema_equals", "passed": True, "message": f"Table {table_name} key schema matches."}
        else:
            return {"id": "key-schema", "type": "dynamodb_key_schema_equals", "passed": False, "message": f"Table {table_name} key schema does not match."}
    except Exception:
        return {"id": "key-schema", "type": "dynamodb_key_schema_equals", "passed": False, "message": f"Table {table_name} was not found."}

def dynamodb_item_exists(table_name: str, key: dict) -> dict:
    client = get_dynamodb_client()
    try:
        response = client.get_item(TableName=table_name, Key=key)
        if response.get("Item"):
            return {"id": "item-exists", "type": "dynamodb_item_exists", "passed": True, "message": f"Item exists in table {table_name}."}
        return {"id": "item-exists", "type": "dynamodb_item_exists", "passed": False, "message": f"Item was not found in table {table_name}."}
    except Exception:
        return {"id": "item-exists", "type": "dynamodb_item_exists", "passed": False, "message": f"Item was not found in table {table_name}."}

def dynamodb_item_attribute_equals(table_name: str, key: dict, attribute: str, expected: dict) -> dict:
    client = get_dynamodb_client()
    try:
        response = client.get_item(TableName=table_name, Key=key)
        item = response.get("Item", {})
        if attribute in item and item[attribute] == expected:
            return {"id": "item-name", "type": "dynamodb_item_attribute_equals", "passed": True, "message": f"Attribute {attribute} matches expected value."}
        else:
            return {"id": "item-name", "type": "dynamodb_item_attribute_equals", "passed": False, "message": f"Attribute {attribute} does not match expected value in table {table_name}."}
    except Exception:
        return {"id": "item-name", "type": "dynamodb_item_attribute_equals", "passed": False, "message": f"Item was not found in table {table_name}."}
