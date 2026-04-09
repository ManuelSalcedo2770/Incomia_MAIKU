import json
import os
import sys
import boto3
from decimal import Decimal

# Añadir el path raíz para importar servicios
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

DYNAMODB_TABLE_TRANSACTIONS = os.environ.get("DYNAMODB_TABLE_TRANSACTIONS", "incomia-transactions-dev")

def lambda_handler(event, context):
    """
    Handler para procesamiento y listado de ingresos/transacciones.
    Soporta POST para registro manual y GET para listar historial.
    """
    method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
    query_params = event.get('queryStringParameters') or {}
    user_id = query_params.get('userId') or query_params.get('user_id') or \
              event.get('requestContext', {}).get('authorizer', {}).get('jwt', {}).get('claims', {}).get('sub') or \
              "USR-FD8F0536"

    db = boto3.resource("dynamodb")
    table = db.Table(DYNAMODB_TABLE_TRANSACTIONS)

    if method == 'POST':
        from services.smoothing_algorithm import process_income_event
        try:
            body = json.loads(event.get('body', '{}'))
            amount = float(body.get('amount', 0))
            result = process_income_event(user_id, amount)
            return _response(200, result)
        except Exception as e:
            return _response(400, {"error": str(e)})

    elif method == 'GET':
        try:
            # Consultamos las transacciones reales del usuario en DynamoDB
            response = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('userId').eq(user_id),
                Limit=50,
                ScanIndexForward=False # Recientes primero
            )
            items = response.get('Items', [])
            
            # Si no hay datos en DB, podemos intentar simulacion con Nessie (Opcional)
            if not items and query_params.get('simulate') == 'true':
                from services.nessie_service import NessieService
                nessie = NessieService()
                account_id = query_params.get('account_id', '64cfbe9096831d0339d67962')
                items = nessie.simulate_income_stream(account_id)
            
            return _response(200, _decimal_to_float(items))
        except Exception as e:
            return _response(500, {"error": str(e)})

    return _response(405, {"error": "Method not allowed"})

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
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Authorization"
        },
        "body": json.dumps(body, default=str)
    }
