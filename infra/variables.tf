variable "aws_region" {
  description = "AWS Region to deploy resources"
  default     = "us-east-1"
}

variable "gemini_api_key_placeholder" {
  description = "Placeholder for sensitive API key, injected via env vars or secrets manager in prod"
  default     = "change_me"
}

variable "jira_api_token" {
  description = "Jira API Token for creating tickets"
  sensitive   = true
}
