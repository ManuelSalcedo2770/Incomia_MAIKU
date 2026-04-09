import json
import os
import boto3
from decimal import Decimal

def lambda_handler(event, context):
    """
    Handler para generar predicciones de liquidez y riesgo.
    """
    query_params = event.get('queryStringParameters') or {}
    user_id = query_params.get('userId') or query_params.get('user_id') or "USR-FD8F0536"

    # En el futuro esto consultaría a un modelo de Prophet o XGBoost
    # Por ahora simulamos la respuesta esperada por el UI con lógica de seguridad
    
    db = boto3.resource("dynamodb")
    table = db.Table(os.environ.get("DYNAMODB_TABLE_USERS", "incomia-users-dev"))
    
    # Valores por defecto "Seguros"
    bankruptcy_prob = 0.05
    new_risk_score = 30
    projected_balance = 5000.0
    
    try:
        response = table.get_item(Key={"userId": user_id})
        item = response.get("Item")
        if item:
            salary = float(item.get("artificial_salary") or item.get("current_artificial_salary") or 0)
            fund = float(item.get("stabilization_fund_balance") or 0)
            
            # Simple heurística de riesgo
            if salary > 0:
                score = (fund / salary)
                if score < 0.2:
                    bankruptcy_prob = 0.45
                    new_risk_score = 85
                    projected_balance = fund - (salary * 0.1)
                elif score > 1.5:
                    bankruptcy_prob = 0.01
                    new_risk_score = 15
                    projected_balance = fund + (salary * 0.2)
    except Exception as e:
        print(f"Error en predicción: {e}")

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps({
            "userId": user_id,
            "prediction": {
                "bankruptcy_probability": bankruptcy_prob,
                "final_projected_balance": projected_balance,
                "new_risk_score": new_risk_score,
                "confidence_interval": [0.85, 0.98]
            }
        })
    }
