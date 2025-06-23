import boto3
import os

# Environment variables
TARGET_GROUP_ARN = os.environ['TARGET_GROUP_ARN']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

# Clients
elbv2_client = boto3.client('elbv2')
sns_client = boto3.client('sns')

def lambda_handler(event, context):
    try:
        response = elbv2_client.describe_target_health(TargetGroupArn=TARGET_GROUP_ARN)
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Failed to describe target health: {str(e)}"
        }

    unhealthy_targets = [
        target for target in response['TargetHealthDescriptions']
        if target['TargetHealth']['State'] != 'healthy'
    ]

    if unhealthy_targets:
        message = f"Unhealthy targets detected in Target Group:\n"
        for target in unhealthy_targets:
            message += (
                f"- Instance ID: {target['Target']['Id']}\n"
                f"  Port: {target['Target']['Port']}\n"
                f"  State: {target['TargetHealth']['State']}\n"
                f"  Reason: {target['TargetHealth'].get('Reason', 'N/A')}\n\n"
            )

        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="Unhealthy Targets Detected in ALB Target Group",
            Message=message
        )

        print(f"Target group ARN: {TARGET_GROUP_ARN}")
        print(f"Health check result: {unhealthy_targets}")

        return {
            'status': 'Unhealthy targets found',
            'unhealthy': unhealthy_targets
        }

    return {
        'status': 'All targets are healthy'
    }
