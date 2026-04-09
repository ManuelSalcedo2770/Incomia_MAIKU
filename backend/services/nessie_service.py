import os
import requests
import logging

logger = logging.getLogger("incomia.nessie")

class NessieService:
    """
    Servicio para interactuar con la API Nessie de Capital One.
    Permite simular cuentas bancarias y transacciones para Incomia.
    """
    BASE_URL = "http://api.reimaginefinancial.com"

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("NESSIE_API_KEY", "MOCK_KEY")
        if self.api_key == "MOCK_KEY":
            logger.warning("Usando MOCK_KEY para Nessie. Las llamadas reales fallarán.")

    def _get_params(self):
        return {"key": self.api_key}

    def get_accounts(self):
        """Obtiene todas las cuentas (usado para simulación)."""
        url = f"{self.BASE_URL}/accounts"
        response = requests.get(url, params=self._get_params())
        response.raise_for_status()
        return response.json()

    def get_customer_accounts(self, customer_id):
        """Obtiene cuentas de un cliente específico."""
        url = f"{self.BASE_URL}/customers/{customer_id}/accounts"
        response = requests.get(url, params=self._get_params())
        response.raise_for_status()
        return response.json()

    def get_account_purchases(self, account_id):
        """Obtiene compras (gastos) de una cuenta."""
        url = f"{self.BASE_URL}/accounts/{account_id}/purchases"
        response = requests.get(url, params=self._get_params())
        response.raise_for_status()
        return response.json()

    def get_account_deposits(self, account_id):
        """Obtiene depósitos (ingresos) de una cuenta."""
        url = f"{self.BASE_URL}/accounts/{account_id}/deposits"
        response = requests.get(url, params=self._get_params())
        response.raise_for_status()
        return response.json()

    def map_to_incomia_income(self, deposit):
        """
        Mapea un depósito de Nessie al modelo interno de Incomia.
        Nessie deposit example:
        {
            "_id": "...", "type": "Deposit", "transaction_date": "2023-10-01",
            "status": "completed", "payee_id": "...", "medium": "balance",
            "amount": 1200, "description": "Payment"
        }
        """
        return {
            "amount": deposit.get("amount", 0),
            "timestamp": f"{deposit.get('transaction_date')}T12:00:00",
            "type": "ingreso",
            "income_source": deposit.get("description", "Nessie External Transfer"),
            "status": "processed"
        }

    def simulate_income_stream(self, account_id):
        """
        Simula un flujo de ingresos basado en los depósitos reales de Nessie.
        """
        deposits = self.get_account_deposits(account_id)
        return [self.map_to_incomia_income(d) for d in deposits]
