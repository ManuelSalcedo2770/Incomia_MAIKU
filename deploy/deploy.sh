#!/bin/sh
set -e

deploy_func() {
  FUNC=$1
  NAME="incomia-$FUNC-v2"
  HANDLER="$FUNC\_handler.lambda_handler"
  if [ "$FUNC" = "advice" ]; then HANDLER="advice_generator.lambda_handler"; fi
  if [ "$FUNC" = "prediction" ]; then HANDLER="prediction_handler.lambda_handler"; fi
  
  echo "Processing $NAME..."
  
  aws lambda create-function \
    --function-name "$NAME" \
    --runtime python3.11 \
    --role arn:aws:iam::834088498700:role/incomia-lambda-exec \
    --handler "$HANDLER" \
    --zip-file "fileb://deploy/$FUNC.zip" \
    --region us-east-1 \
    --environment "fileb://deploy/env.json" || \
  aws lambda update-function-code \
    --function-name "$NAME" \
    --zip-file "fileb://deploy/$FUNC.zip" \
    --region us-east-1
}

deploy_func smoothing
deploy_func advice
deploy_func prediction
deploy_func income
deploy_func expense
