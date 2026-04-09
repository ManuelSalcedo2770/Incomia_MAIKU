import json
import os
import uuid
import boto3
from datetime import datetime

# Inicialización de DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE_EXPENSES', 'incomia-expenses-dev')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """
    Handler para CRUD de gastos (Expenses).
    Soporta GET (listar), POST (crear) y DELETE (eliminar).
    """
    method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
    query_params = event.get('queryStringParameters') or {}
    
    # Identificar al usuario (fallback para test)
    user_id = query_params.get('userId') or query_params.get('user_id') or \
              event.get('requestContext', {}).get('authorizer', {}).get('jwt', {}).get('claims', {}).get('sub') or \
              "USR-FD8F0536"

    if method == 'GET':
        try:
            # En un entorno real usaríamos un Index (GSI) o Query por userId
            # Por simplicidad para la demo usamos Scan con filtro (No recomendado para prod)
            response = table.scan(
                FilterExpression="userId = :uid",
                ExpressionAttributeValues={":uid": user_id}
            )
            items = response.get('Items', [])
            return _response(200, items)
        except Exception as e:
            return _response(500, {"error": str(e)})

    elif method == 'POST':
        try:
            body = json.loads(event.get('body', '{}'))
            if not body.get('amount') or not body.get('concept'):
                return _response(400, {"error": "Missing amount or concept"})

            expense_id = str(uuid.uuid4())[:8]
            item = {
                "userId": user_id,
                "expenseId": expense_id,
                "concept": body.get('concept'),
                "amount": float(body.get('amount')),
                "category": body.get('category', 'Otros'),
                "type": body.get('type', 'fixed'),
                "timestamp": datetime.utcnow().isoformat()
            }
            table.put_item(Item=item)
            return _response(201, item)
        except Exception as e:
            return _response(400, {"error": str(e)})

    elif method == 'DELETE':
        try:
            # El ID viene en query params para el DELETE
            expense_id = query_params.get('id') or query_params.get('expenseId')
            if not expense_id:
                return _response(400, {"error": "Missing expenseId"})

            table.delete_item(
                Key={
                    "userId": user_id,
                    "expenseId": expense_id
                }
            )
            return _response(200, {"message": "Deleted successfully", "id": expense_id})
        except Exception as e:
            return _response(500, {"error": str(e)})

    return _response(405, {"error": "Method not allowed"})

def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,Authorization"
        },
        "body": json.dumps(body, default=str)
    }
