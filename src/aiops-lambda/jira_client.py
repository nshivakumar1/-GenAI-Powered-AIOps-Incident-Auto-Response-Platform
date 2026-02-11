import os
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
        Create a Jira issue in the configured project and return its issue key.
        
        Parameters:
            summary (str): Short summary/title for the Jira issue.
            description (str): Detailed description used as the Jira issue description.
            priority (str): Priority identifier (e.g., "P1", "P2"). Currently not included in the payload by default; mapping to Jira priority is present but commented out.
            labels (list): List of label strings to attach to the issue.
        
        Returns:
            str: The created issue key (e.g., "OPS-123"). Returns "MOCK-101" if Jira credentials are missing and ticket creation is skipped, or "ERROR-000" if an error occurs while calling the Jira API.
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
        # priority_map = {
        #     "P1": "Highest",
        #     "P2": "High",
        #     "P3": "Medium"
        # }
        # "priority": {"name": jira_priority} # Uncomment if priority scheme matches

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
                "issuetype": {"id": "10020"}, # "Report an incident" for JSM project
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
            if 'response' in locals():
                logger.error(f"Jira API Response: {response.text}")
            return "ERROR-000"