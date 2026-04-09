import json
import os
import sys
import boto3
from decimal import Decimal

# Añadir el path raíz para importar servicios
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

DYNAMODB_TABLE_USERS = os.environ.get("DYNAMODB_TABLE_USERS", "incomia-users-dev")

def lambda_handler(event, context):
    """
    Retorna el estado actual del smoothing para el usuario.
    """
    user_id = event.get('requestContext', {}).get('authorizer', {}).get('jwt', {}).get('claims', {}).get('sub') or "test_user"
    
    db = boto3.resource("dynamodb")
    table = db.Table(DYNAMODB_TABLE_USERS)
    
    try:
        response = table.get_item(Key={"userId": user_id})
        item = response.get("Item")
        
        if not item:
            return _response(404, {"error": "User financial state not found"})
            
        # Convertir Decimal a float para JSON
        result = _decimal_to_float(item)
        
        return _response(200, {
            "userId": result["userId"],
            "artificial_salary": result.get("current_artificial_salary", 0),
            "stabilization_fund": result.get("stabilization_fund_balance", 0),
            "resilience_indicator": (result.get("stabilization_fund_balance", 0) / result.get("current_artificial_salary", 1)) if result.get("current_artificial_salary", 0) > 0 else 0
        })
    except Exception as e:
        return _response(500, {"error": str(e)})

def _decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _decimal_to_float(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_decimal_to_float(i) for i in obj]
    return obj

def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body, default=str)
    }
