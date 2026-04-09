# =====================================================================
# MOTOR DE PROCESAMIENTO SERVERLESS (LAMBDAS)
# Aquí definimos el "cerebro" distribuido de Incomia.
# Cada función es independiente, escalable y de bajo costo.
# =====================================================================

# 1. FUNCIÓN: PROCESADOR DE INGRESOS (POST /income, GET /income)
resource "aws_lambda_function" "income_processor" {
  filename      = "income_processor.zip"
  function_name = "${var.project_name}-income-processor-${var.env}"
  role          = var.lambda_role_arn
  handler       = "income_handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30

  environment {
    variables = {
      DYNAMODB_TABLE_USERS        = "${var.project_name}-users-${var.env}"
      DYNAMODB_TABLE_TRANSACTIONS = "${var.project_name}-transactions-${var.env}"
      NESSIE_API_KEY              = var.nessie_api_key
      ENV                         = var.env
    }
  }
}

# 2. FUNCIÓN: MOTOR DE SMOOTHING (GET /smoothing)
resource "aws_lambda_function" "smoothing_engine" {
  filename      = "smoothing_engine.zip"
  function_name = "${var.project_name}-smoothing-engine-${var.env}"
  role          = var.lambda_role_arn
  handler       = "smoothing_handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = 30

  environment {
    variables = {
      DYNAMODB_TABLE_USERS = "${var.project_name}-users-${var.env}"
      ENV                  = var.env
    }
  }
}

# 3. FUNCIÓN: PRONÓSTICO DE LIQUIDEZ (GET /predictions)
resource "aws_lambda_function" "prediction_engine" {
  filename      = "prediction_engine.zip"
  function_name = "${var.project_name}-prediction-engine-${var.env}"
  role          = var.lambda_role_arn
  handler       = "liquidity_forecast.lambda_handler"
  runtime       = "python3.11"
  timeout       = 60 # Prophet puede ser pesado

  environment {
    variables = {
      DYNAMODB_TABLE_USERS        = "${var.project_name}-users-${var.env}"
      DYNAMODB_TABLE_TRANSACTIONS = "${var.project_name}-transactions-${var.env}"
      DYNAMODB_TABLE_EXPENSES     = "${var.project_name}-expenses-${var.env}"
    }
  }
}

# 4. FUNCIÓN: ASESOR IA (GET /advice)
resource "aws_lambda_function" "advice_generator" {
  filename      = "advice_generator.zip"
  function_name = "${var.project_name}-advice-generator-${var.env}"
  role          = var.lambda_role_arn
  handler       = "advice_generator.lambda_handler"
  runtime       = "python3.11"
  timeout       = 60 # Bedrock puede tardar

  environment {
    variables = {
      DYNAMODB_TABLE_USERS        = "${var.project_name}-users-${var.env}"
      DYNAMODB_TABLE_TRANSACTIONS = "${var.project_name}-transactions-${var.env}"
      DYNAMODB_TABLE_EXPENSES     = "${var.project_name}-expenses-${var.env}"
      BEDROCK_MODEL_ID           = var.bedrock_model_id
    }
  }
}

# PERMISOS PARA API GATEWAY INVOCAR LAMBDAS
resource "aws_lambda_permission" "apigw_income" {
  statement_id  = "AllowAPIGatewayInvokeIncome"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.income_processor.function_name
  principal     = "apigateway.amazonaws.com"
}

resource "aws_lambda_permission" "apigw_smoothing" {
  statement_id  = "AllowAPIGatewayInvokeSmoothing"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.smoothing_engine.function_name
  principal     = "apigateway.amazonaws.com"
}

resource "aws_lambda_permission" "apigw_prediction" {
  statement_id  = "AllowAPIGatewayInvokePrediction"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.prediction_engine.function_name
  principal     = "apigateway.amazonaws.com"
}

resource "aws_lambda_permission" "apigw_advice" {
  statement_id  = "AllowAPIGatewayInvokeAdvice"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.advice_generator.function_name
  principal     = "apigateway.amazonaws.com"
}
