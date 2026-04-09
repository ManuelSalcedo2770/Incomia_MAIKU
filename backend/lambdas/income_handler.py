import json
import os
import sys

# Añadir el path raíz para importar servicios
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.smoothing_algorithm import process_income_event
from services.nessie_service import NessieService

def lambda_handler(event, context):
    """
    Handler para procesamiento de ingresos.
    Soporta POST para registro manual y GET para integración con Nessie.
    """
    method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
    query_params = event.get('queryStringParameters') or {}
    user_id = query_params.get('userId') or query_params.get('user_id') or \
              event.get('requestContext', {}).get('authorizer', {}).get('jwt', {}).get('claims', {}).get('sub') or \
              "test_user"

    if method == 'POST':
        try:
            body = json.loads(event.get('body', '{}'))
            amount = float(body.get('amount', 0))
            result = process_income_event(user_id, amount)
            return _response(200, result)
        except Exception as e:
            return _response(400, {"error": str(e)})

    elif method == 'GET':
        # Simulación con Nessie
        try:
            nessie = NessieService()
            # En un caso real, buscaríamos la account_id asociada al user_id
            # Para la demo, usamos una account_id fija si no viene en query
            account_id = event.get('queryStringParameters', {}).get('account_id', '64cfbe9096831d0339d67962')
            
            incomes = nessie.simulate_income_stream(account_id)
            for inc in incomes:
                 process_income_event(user_id, inc['amount'])
            
            return _response(200, {"message": f"Processed {len(incomes)} incomes from Nessie.", "incomes": incomes})
        except Exception as e:
            return _response(500, {"error": str(e)})

    return _response(405, {"error": "Method not allowed"})

def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body, default=str)
    }
