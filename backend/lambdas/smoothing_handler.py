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
        
        # 2. Generar historial para gráficas
        salary = 0
        fund = 0
        if item:
            salary = float(item.get("current_artificial_salary") or item.get("artificial_salary") or 0)
            fund = float(item.get("stabilization_fund_balance") or 0)

        # Intentar obtener transacciones reales
        history = []
        months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        
        try:
            from boto3.dynamodb.conditions import Attr
            tx_table = db.Table(os.environ.get("DYNAMODB_TABLE_TRANSACTIONS", "incomia-transactions-dev"))
            tx_resp = tx_table.scan(
                FilterExpression=Attr("userId").eq(user_id),
                Limit=50
            )
            transactions = tx_resp.get('Items', [])
            
            if transactions:
                sorted_txs = sorted(transactions, key=lambda x: x.get('timestamp', ''), reverse=True)
                for i, tx in enumerate(sorted_txs[:6]):
                    month_idx = (datetime.now().month - 1 - i) % 12
                    real_amount = float(tx.get('amount', 0))
                    payout_amount = float(tx.get('target_salary_at_time', salary)) if tx.get('target_salary_at_time') else salary
                    history.append({
                        "month": months[month_idx],
                        "realIncome": abs(real_amount),
                        "payout": payout_amount
                    })
                history.reverse()
        except Exception as tx_err:
            print(f"Error fetching transactions: {tx_err}")

        # Si no hay historial real, generar datos de demostración basados en el salario
        if not history and salary > 0:
            import random
            random.seed(42)  # Semilla fija para que se vean consistentes
            for i in range(6):
                month_idx = (datetime.now().month - 1 - (5 - i)) % 12
                # Simular volatilidad freelance: variación de ±40% alrededor del salario
                volatility = random.uniform(0.6, 1.4)
                history.append({
                    "month": months[month_idx],
                    "realIncome": round(salary * volatility, 2),
                    "payout": round(salary, 2)
                })

        if not item:
            return _response(200, {
                "userId": user_id,
                "artificial_salary": 0,
                "stabilization_fund": 0,
                "resilience_indicator": 0,
                "history": history
            })

        resilience = (fund / salary) if salary > 0 else 0
        return _response(200, {
            "userId": user_id,
            "artificial_salary": salary,
            "stabilization_fund": fund,
            "resilience_indicator": resilience,
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
