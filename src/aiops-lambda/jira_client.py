import os
import json
import logging
import requests

logger = logging.getLogger()

class JiraClient:
    def __init__(self):
        self.domain = os.environ.get("JIRA_DOMAIN")  # e.g., "your-company.atlassian.net"
        self.email = os.environ.get("JIRA_EMAIL")
        self.token = os.environ.get("JIRA_API_TOKEN")
        self.project_key = os.environ.get("JIRA_PROJECT_KEY", "OPS")

    def create_ticket(self, summary: str, description: str, priority: str, labels: list) -> str:
        """
        Creates a Jira ticket and returns the issue key (e.g., OPS-123).
        """
        if not (self.domain and self.email and self.token):
            logger.warning("Jira credentials missing. Skipping ticket creation.")
            return "MOCK-101"

        url = f"https://{self.domain}/rest/api/3/issue"
        auth = (self.email, self.token)
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Map 'P1'/'P2' to Jira Priority IDs (This varies by Jira instance, assuming standard names)
        priority_map = {
            "P1": "Highest",
            "P2": "High",
            "P3": "Medium"
        }
        jira_priority = priority_map.get(priority, "Medium")

        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}]
                    }]
                },
                "issuetype": {"name": "Incident"}, # Or "Bug" or "Task"
                "labels": labels,
                # "priority": {"name": jira_priority} # Uncomment if priority scheme matches
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers, auth=auth)
            response.raise_for_status()
            issue_key = response.json().get("key")
            logger.info(f"Created Jira Ticket: {issue_key}")
            return issue_key
        except Exception as e:
            logger.error(f"Failed to create Jira ticket: {e}")
            return "ERROR-000"
