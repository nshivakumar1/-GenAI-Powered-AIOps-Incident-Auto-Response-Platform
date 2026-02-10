import json
import logging
import time
import boto3
import os
import requests
from datetime import datetime
from gemini_client import GeminiClient
from jira_client import JiraClient
from slack_client import SlackClient

# Configure Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Clients
cw_logs = boto3.client('logs')
gemini = GeminiClient()
jira = JiraClient()
slack = SlackClient()

LOG_GROUP_NAME = "/ecs/aiops-victim-service"
ES_HOST = os.environ.get("ES_HOST", "http://elasticsearch:9200") # For local dev via Docker network or tunnel

def get_recent_logs(log_group_name, limit=50):
    try:
        streams = cw_logs.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        if not streams['logStreams']:
            return "No log streams found."
        
        stream_name = streams['logStreams'][0]['logStreamName']
        events = cw_logs.get_log_events(
            logGroupName=log_group_name,
            logStreamName=stream_name,
            limit=limit,
            startFromHead=False
        )
        return "\n".join([e['message'] for e in events['events']])
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        return f"Error fetching logs: {str(e)}"

def index_incident_to_es(incident_data):
    """
    Sends the incident data to Elasticsearch for dashboarding.
    """
    url = f"{ES_HOST}/aiops-incidents/_doc"
    headers = {"Content-Type": "application/json"}
    
    # Add timestamp
    incident_data["@timestamp"] = datetime.utcnow().isoformat()
    
    try:
        # TIMEOUT is short to not block execution
        resp = requests.post(url, json=incident_data, headers=headers, timeout=2)
        logger.info(f"Indexed to ES: {resp.status_code}")
    except Exception as e:
        logger.warning(f"Failed to index to ES (Dashboard might miss this): {e}")

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    
    detail = event.get('detail', {})
    alarm_name = detail.get('alarmName', 'Unknown Alarm')
    state_value = detail.get('state', {}).get('value', 'UNKNOWN')
    
    if state_value != 'ALARM':
        return {"status": "ignored"}

    logs = get_recent_logs(LOG_GROUP_NAME)
    
    # Analyze
    ai_context = {"alarm_name": alarm_name, "timestamp": time.time()}
    analysis = gemini.analyze_incident(logs, context=ai_context)
    
    # Jira
    ticket_key = jira.create_ticket(
        summary=f"[{analysis.get('severity')}] {analysis.get('category')} Incident: {alarm_name}",
        description=f"Root Cause: {analysis.get('root_cause')}\n\nSuggested Fix: {analysis.get('suggested_fix')}",
        priority=analysis.get('severity'),
        labels=["aiops", analysis.get('category')]
    )
    
    # Slack
    slack.send_alert(analysis, ticket_key)
    
    # Dashboard (ES)
    dashboard_data = {
        "incident_id": context.aws_request_id,
        "alarm_name": alarm_name,
        "severity": analysis.get('severity'),
        "category": analysis.get('category'),
        "root_cause": analysis.get('root_cause'),
        "auto_remediate": analysis.get('auto_remediate'),
        "jira_ticket": ticket_key,
        "logs_snippet": logs[:200]
    }
    index_incident_to_es(dashboard_data)
    
    return {
        "statusCode": 200,
        "body": json.dumps({"status": "processed", "ticket": ticket_key})
    }
