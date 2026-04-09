variable "project_name" {
  description = "Nombre del proyecto usado como prefijo en la API"
  type        = string
}

variable "cognito_client_id" {
  description = "ID del cliente Cognito para el authorizer JWT"
  type        = string
}

variable "cognito_pool_id" {
  description = "ID del User Pool de Cognito para el authorizer JWT"
  type        = string
}

variable "region" {
  description = "Región AWS"
  type        = string
}

variable "income_processor_arn" {
  description = "ARN de la lambda de procesamiento de ingresos"
  type        = string
}

variable "smoothing_engine_arn" {
  description = "ARN de la lambda de motor de smoothing"
  type        = string
}

variable "prediction_engine_arn" {
  description = "ARN de la lambda de predicción de liquidez"
  type        = string
}

variable "advice_generator_arn" {
  description = "ARN de la lambda de asesor IA"
  type        = string
}
