# --- CloudWatch Alarms ---

resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "victim-service-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "60"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ec2 cpu utilization"
  treat_missing_data  = "breaching"

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = "aiops-victim-service" # Assumption: Service will be named this
  }
}

resource "aws_cloudwatch_metric_alarm" "high_memory" {
  alarm_name          = "victim-service-high-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = "60"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors available memory"
  treat_missing_data  = "breaching"

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = "aiops-victim-service"
  }
}

# --- EventBridge Rule for Alarm State Change ---

resource "aws_cloudwatch_event_rule" "capture_alarm" {
  name           = "capture-cloudwatch-alarms"
  description    = "Capture CloudWatch Alarm State Changes"
  event_bus_name = aws_cloudwatch_event_bus.aiops_bus.name

  event_pattern = jsonencode({
    source      = ["aws.cloudwatch"]
    detail-type = ["CloudWatch Alarm State Change"]
    detail = {
      state = {
        value = ["ALARM"]
      }
      alarmName = [
        aws_cloudwatch_metric_alarm.high_cpu.alarm_name,
        aws_cloudwatch_metric_alarm.high_memory.alarm_name
      ]
    }
  })
}

# --- EventBridge Target (Trigger Lambda) ---

resource "aws_cloudwatch_event_target" "sns" {
  rule           = aws_cloudwatch_event_rule.capture_alarm.name
  target_id      = "SendToAIOpsLambda"
  arn            = aws_lambda_function.aiops_brain.arn
  event_bus_name = aws_cloudwatch_event_bus.aiops_bus.name
}
