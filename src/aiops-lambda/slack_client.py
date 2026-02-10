import os
import json
import logging
import requests

logger = logging.getLogger()

class SlackClient:
    def __init__(self):
        self.webhook_url = os.environ.get("SLACK_WEBHOOK_URL")

    def send_alert(self, incident_data: dict, jira_key: str):
        """
        Sends a Block Kit alert to Slack.
        """
        if not self.webhook_url:
            logger.warning("SLACK_WEBHOOK_URL missing. Skipping alert.")
            return

        severity = incident_data.get("severity", "UNKNOWN")
        color = "#FF0000" if severity == "P1" else "#FFA500" if severity == "P2" else "#FFFF00"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 {severity} Incident Detected",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Service:*\n{incident_data.get('category', 'App')}"},
                    {"type": "mrkdwn", "text": f"*Root Cause:*\n{incident_data.get('root_cause')}"}
                ]
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Jira Ticket:*\n<{jira_key}|View Ticket>"},
                    {"type": "mrkdwn", "text": f"*Suggested Fix:*\n{incident_data.get('suggested_fix')}"}
                ]
            }
        ]

        # Add Actions if auto-remediation is possible
        if incident_data.get("auto_remediate"):
            action = incident_data.get("remediation_action")
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🟢 Auto-Fix Now",
                            "emoji": True
                        },
                        "style": "primary",
                        "value": action, 
                        "action_id": "auto_fix_action" # This would need an interactive endpoint to handle
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🔴 Escalate",
                            "emoji": True
                        },
                        "style": "danger",
                        "value": "escalate",
                        "action_id": "escalate_action"
                    }
                ]
            })

        payload = {"blocks": blocks}
        
        try:
            requests.post(self.webhook_url, json=payload)
            logger.info("Slack alert sent.")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
