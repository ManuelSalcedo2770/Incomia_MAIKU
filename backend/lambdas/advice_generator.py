import json
import os
import boto3
from decimal import Decimal

def lambda_handler(event, context):
    """
    Handler para generar consejos financieros (Advice).
    """
    query_params = event.get('queryStringParameters') or {}
    user_id = query_params.get('userId') or query_params.get('user_id') or "USR-FD8F0536"

    # En el futuro esto consultaría a AWS Bedrock (Claude)
    # Por ahora usamos lógica basada en el estado del usuario
    
    db = boto3.resource("dynamodb")
    table = db.Table(os.environ.get("DYNAMODB_TABLE_USERS", "incomia-users-dev"))
    
    advice = "Tu flujo de ingresos es estable. Considera mover un 5% adicional a tu fondo de resiliencia este mes para alcanzar tu meta más rápido."
    
    try:
        response = table.get_item(Key={"userId": user_id})
        item = response.get("Item")
        if item:
            salary = float(item.get("artificial_salary") or item.get("current_artificial_salary") or 0)
            fund = float(item.get("stabilization_fund_balance") or 0)
            
            if fund < (salary * 0.5):
                advice = "Prioridad: Construir tu fondo. Tus ingresos de este mes muestran una volatilidad baja, es el momento ideal para ahorrar un 10% adicional."
            elif fund > (salary * 2):
                advice = "¡Fondo sólido! Tienes cobertura para 2 meses. ¿Sabías que podrías invertir el excedente en un CETES para ganarle a la inflación?"
    except Exception as e:
        print(f"Error consultando perfil: {e}")

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
            "advice": advice,
            "engine": "Incomia-Rule-based-v1"
        })
    }
