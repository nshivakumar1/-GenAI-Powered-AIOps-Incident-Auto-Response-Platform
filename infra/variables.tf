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

variable "slack_webhook_url" {
  description = "Slack Incoming Webhook URL for alerts"
  sensitive   = true
}

variable "jira_email" {
  description = "Email address for Jira authentication"
  type        = string
}

variable "jira_domain" {
  description = "Jira domain (e.g., your-company.atlassian.net)"
  type        = string
}
