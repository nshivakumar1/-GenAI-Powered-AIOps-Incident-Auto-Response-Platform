import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ecs = boto3.client('ecs')

def lambda_handler(event, context):
    """
    Handles auto-remediation actions triggered by Slack interactive buttons.
    """
    logger.info(f"Received remediation request: {json.dumps(event)}")
    
    # Payload from Slack usually comes differently, we will need to parse the payload (base64 encoded often)
    # For now, assuming a direct JSON invocation for simplicity/testing
    
    action = event.get("action", "unknown")
    service_name = event.get("service", "aiops-victim-service")
    cluster_name = event.get("cluster", "aiops-cluster")
    
    try:
        if action == "restart_service":
            logger.info(f"Restarting service {service_name} in cluster {cluster_name}")
            # Force new deployment
            response = ecs.update_service(
                cluster=cluster_name,
                service=service_name,
                forceNewDeployment=True
            )
            return {"status": "success", "message": "Service restart initiated."}
            
        elif action == "scale_up":
            logger.info("Scaling up service...")
            # Logic to update desired count
            return {"status": "success", "message": "Service scaled up."}
            
        else:
            return {"status": "ignored", "message": f"Unknown action: {action}"}

    except Exception as e:
        logger.error(f"Remediation failed: {str(e)}")
        return {"status": "error", "message": str(e)}
