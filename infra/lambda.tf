# --- IAM Roles ---

resource "aws_iam_role" "lambda_role" {
  name = "aiops_lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_permissions" {
  name = "aiops_lambda_permissions"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "logs:FilterLogEvents",
          "logs:GetLogEvents",
          "logs:DescribeLogStreams" 
        ]
        Resource = "*" 
      }
    ]
  })
}

# --- Zipping Code ---

data "archive_file" "aiops_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src/aiops-lambda"
  output_path = "${path.module}/files/aiops-lambda.zip"
  excludes    = ["requirements.txt", "__pycache__"] 
}

data "archive_file" "remediation_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src/remediation-lambda"
  output_path = "${path.module}/files/remediation-lambda.zip"
}

# --- Lambda Functions ---

resource "aws_lambda_function" "aiops_brain" {
  filename         = data.archive_file.aiops_lambda_zip.output_path
  function_name    = "aiops-incident-analyzer"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  source_code_hash = data.archive_file.aiops_lambda_zip.output_base64sha256
  runtime          = "python3.9"
  timeout          = 60 # Increased for Gemini API

  environment {
    variables = {
      GEMINI_API_KEY = var.gemini_api_key_placeholder
      JIRA_DOMAIN    = "devopsvibecoding.atlassian.net"
      JIRA_EMAIL     = "nakul.cloudops@outlook.com"
      JIRA_PROJECT_KEY = "AIO"
      JIRA_API_TOKEN = var.jira_api_token
      SLACK_WEBHOOK_URL = var.gemini_api_key_placeholder # Temporary reuse or add new var
    }
  }
}

resource "aws_lambda_function" "remediation_bot" {
  filename         = data.archive_file.remediation_lambda_zip.output_path
  function_name    = "aiops-remediation-bot"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  source_code_hash = data.archive_file.remediation_lambda_zip.output_base64sha256
  runtime          = "python3.9"
  timeout          = 30

  environment {
    variables = {
      CLUSTER_NAME = aws_ecs_cluster.main.name
    }
  }
}

# --- Function URL for Remediation (Slack Button Target) ---
resource "aws_lambda_function_url" "remediation_url" {
  function_name      = aws_lambda_function.remediation_bot.function_name
  authorization_type = "NONE" # For demo purposes; use AWS_IAM or verify signature in prod
}

# --- EventBridge Permission ---
resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.aiops_brain.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_bus.aiops_bus.arn
}

# --- Outputs ---
output "remediation_function_url" {
  value = aws_lambda_function_url.remediation_url.function_url
}
