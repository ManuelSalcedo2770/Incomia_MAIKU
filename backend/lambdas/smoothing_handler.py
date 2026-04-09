import json
import os
import sys
import boto3
from datetime import datetime
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
        # 1. Obtener estado actual
        response = table.get_item(Key={"userId": user_id})
        item = response.get("Item")
        
        # 2. Obtener historial de transacciones para las gráficas
        tx_table = db.Table(os.environ.get("DYNAMODB_TABLE_TRANSACTIONS", "incomia-transactions-dev"))
        # En una app real usaríamos Query con KeyConditionExpression. Para demo usamos Scan limitado.
        tx_resp = tx_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr("userId").eq(user_id),
            Limit=50 # Suficiente para mostrar tendencia reciente
        )
        transactions = tx_resp.get('Items', [])
        
        # Agrupar por mes para la gráfica (últimos 6 meses)
        # Por simplicidad para la demo, mapeamos los últimos registros a puntos de gráfica
        history = []
        months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        
        # Tomamos una muestra de transacciones y las proyectamos
        sorted_txs = sorted(transactions, key=lambda x: x.get('timestamp', ''), reverse=True)
        for i, tx in enumerate(sorted_txs[:6]):
            month_idx = (datetime.now().month - 1 - i) % 12
            history.append({
                "month": months[month_idx],
                "realIncome": float(tx.get('amount', 0)),
                "payout": float(tx.get('target_salary_at_time') or item.get('current_artificial_salary') if item else 3000)
            })
        
        history.reverse() # Orden cronológico

        if not item:
            # Fallback seguro
            return _response(200, {
                "userId": user_id,
                "artificial_salary": 0,
                "stabilization_fund": 0,
                "resilience_indicator": 0,
                "history": history
            })

        return _response(200, {
            "userId": user_id,
            "artificial_salary": float(item.get("current_artificial_salary") or item.get("artificial_salary") or 0),
            "stabilization_fund": float(item.get("stabilization_fund_balance") or 0),
            "resilience_indicator": float(item.get("stabilization_fund_balance", 0)) / float(item.get("current_artificial_salary", 1)) if float(item.get("current_artificial_salary", 0)) > 0 else 0,
            "history": history
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
