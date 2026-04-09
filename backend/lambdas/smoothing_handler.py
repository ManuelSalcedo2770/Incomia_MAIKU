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
    # Prioridad: Query parameter (para simulación) > Authorizer (para producción)
    query_params = event.get('queryStringParameters') or {}
    user_id = query_params.get('userId') or query_params.get('user_id') or \
              event.get('requestContext', {}).get('authorizer', {}).get('jwt', {}).get('claims', {}).get('sub') or \
              "test_user"
    
    db = boto3.resource("dynamodb")
    table = db.Table(DYNAMODB_TABLE_USERS)
    
    try:
        response = table.get_item(Key={"userId": user_id})
        item = response.get("Item")
        
        if not item:
            # En lugar de 404, devolvemos un estado inicial seguro para que el Dashboard no se cuelgue
            return _response(200, {
                "userId": user_id,
                "artificial_salary": 0,
                "stabilization_fund": 0,
                "resilience_indicator": 0,
                "message": "Bienvenido a Incomia. Comience cargando sus depósitos."
            })
            
        # Convertir Decimal a float para JSON
        result = _decimal_to_float(item)
        
        # Soportamos ambos nombres de campos (transición de schema)
        salary = result.get("current_artificial_salary") or result.get("artificial_salary") or 0
        fund = result.get("stabilization_fund_balance") or 0
        
        return _response(200, {
            "userId": result["userId"],
            "artificial_salary": salary,
            "stabilization_fund": fund,
            "resilience_indicator": (fund / salary) if salary > 0 else 0
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
