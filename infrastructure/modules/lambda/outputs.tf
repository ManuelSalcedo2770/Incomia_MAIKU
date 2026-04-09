output "income_processor_arn" {
  value = aws_lambda_function.income_processor.arn
}

output "smoothing_engine_arn" {
  value = aws_lambda_function.smoothing_engine.arn
}

output "prediction_engine_arn" {
  value = aws_lambda_function.prediction_engine.arn
}

output "advice_generator_arn" {
  value = aws_lambda_function.advice_generator.invoke_arn
}

output "expense_processor_arn" {
  value = aws_lambda_function.expense_processor.invoke_arn
}

output "income_processor_name" {
  value = aws_lambda_function.income_processor.function_name
}

output "smoothing_engine_name" {
  value = aws_lambda_function.smoothing_engine.function_name
}

output "prediction_engine_name" {
  value = aws_lambda_function.prediction_engine.function_name
}

output "advice_generator_name" {
  value = aws_lambda_function.advice_generator.function_name
}
