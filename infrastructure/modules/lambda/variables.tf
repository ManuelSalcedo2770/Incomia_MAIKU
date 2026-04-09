variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
}

variable "env" {
  description = "Ambiente (dev/prod)"
  type        = string
}

variable "lambda_role_arn" {
  description = "ARN del rol de ejecución de Lambda"
  type        = string
}

variable "nessie_api_key" {
  description = "API Key para Nessie"
  type        = string
  default     = "MOCK_KEY"
}

variable "bedrock_model_id" {
  description = "Modelo de Bedrock a usar"
  type        = string
  default     = "anthropic.claude-3-sonnet-20260229-v1:0"
}
