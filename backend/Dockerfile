FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para algunas librerías de Python
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponer el puerto de FastAPI
EXPOSE 8000

# Comando para ejecutar la aplicación (MVP Local)
# En AWS Lambda, esta imagen no se usa directamente a menos que sea una Lambda Container Image.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
