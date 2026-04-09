import os
import boto3
from datetime import datetime
from decimal import Decimal
import logging

logger = logging.getLogger("incomia.smoothing")

# Configuraciones del algoritmo de resiliencia
SAFETY_FACTOR = 0.8 # Para ser conservadores iniciales y no sobreestimar (80%)
RESILIENCE_MONTHS = 3 # M = Número de meses de colchón financiero
MIN_SALARY_THRESHOLD = 200.0 # Umbral mínimo de vida configurable

DYNAMODB_TABLE_USERS = os.environ.get("DYNAMODB_TABLE_USERS", "incomia-users-dev")
DYNAMODB_TABLE_TRANSACTIONS = os.environ.get("DYNAMODB_TABLE_TRANSACTIONS", "incomia-transactions-dev")

def _get_db():
    return boto3.resource("dynamodb")

def _decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: _decimal_to_float(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_decimal_to_float(i) for i in obj]
    return obj

def process_income_event(user_id: str, amount: float) -> dict:
    """
    Procesa un evento de ingreso y aplica el algoritmo de suavizado (Smoothing).
    Implementado para DynamoDB.
    """
    db = _get_db()
    users_table = db.Table(DYNAMODB_TABLE_USERS)
    txns_table = db.Table(DYNAMODB_TABLE_TRANSACTIONS)
    
    # 1. Obtener estado actual del usuario
    response = users_table.get_item(Key={"userId": user_id})
    user_state = response.get("Item")
    
    if not user_state:
        # 1.1 Usuario nuevo sin historial
        target_salary = max(amount * SAFETY_FACTOR, MIN_SALARY_THRESHOLD)
        available_fund = 0.0
        user_state = {
            "userId": user_id,
            "current_artificial_salary": Decimal(str(target_salary)),
            "stabilization_fund_balance": Decimal(str(available_fund)),
            "primary_sector": "General", # Default
            "created_at": datetime.utcnow().isoformat()
        }
        users_table.put_item(Item=user_state)
    else:
        target_salary = float(user_state.get("current_artificial_salary", MIN_SALARY_THRESHOLD))
        available_fund = float(user_state.get("stabilization_fund_balance", 0.0))

    artificial_salary_paid = 0.0
    surplus_to_fund = 0.0
    withdrawn_from_fund = 0.0
    
    # 3. Lógica principal de Buffer y Absorsión
    if amount >= target_salary:
        # Ingresos altos: Absorbemos excedentes
        artificial_salary_paid = target_salary
        surplus_to_fund = amount - target_salary
        available_fund += surplus_to_fund
    else:
        # Ingresos bajos: Retiramos del fondo
        deficit = target_salary - amount
        if available_fund >= deficit:
            withdrawn_from_fund = deficit
            available_fund -= deficit
            artificial_salary_paid = target_salary
        else:
            withdrawn_from_fund = available_fund
            available_fund = 0.0
            artificial_salary_paid = amount + withdrawn_from_fund
            
            # Ajuste de salario objetivo si el fondo se agota
            new_target = (target_salary + artificial_salary_paid) / 2.0
            target_salary = max(new_target, MIN_SALARY_THRESHOLD)

    # 4. Actualizar estado
    available_fund = max(0.0, available_fund)
    users_table.update_item(
        Key={"userId": user_id},
        UpdateExpression="SET stabilization_fund_balance = :f, current_artificial_salary = :s",
        ExpressionAttributeValues={
            ":f": Decimal(str(round(available_fund, 2))),
            ":s": Decimal(str(round(target_salary, 2)))
        }
    )
    
    # 5. Calcular indicadores
    resilience_indicator = available_fund / target_salary if target_salary > 0 else 0.0

    # 6. Guardar transacción
    import uuid
    txns_table.put_item(Item={
        "userId": user_id,
        "transactionId": f"TXN-{uuid.uuid4().hex[:8].upper()}", # Requerido por el esquema de DB
        "timestamp": datetime.utcnow().isoformat(),
        "amount": Decimal(str(amount)),
        "type": "ingreso",
        "description": "Depósito procesado por IA",
        "target_salary_at_time": Decimal(str(round(target_salary, 2))),
        "fund_after": Decimal(str(round(available_fund, 2)))
    })

    return {
        "amount_processed": amount,
        "artificial_salary_paid": round(artificial_salary_paid, 2),
        "surplus_to_fund": round(surplus_to_fund, 2),
        "withdrawn_from_fund": round(withdrawn_from_fund, 2),
        "current_target": round(target_salary, 2),
        "remaining_fund": round(available_fund, 2),
        "resilience_indicator": round(resilience_indicator, 2)
    }
