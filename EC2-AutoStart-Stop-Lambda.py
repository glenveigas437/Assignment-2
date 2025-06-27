import boto3

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    # Find instances to stop
    stop_instances = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Action', 'Values': ['Auto-Stop']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    stop_ids = [
        inst['InstanceId']
        for res in stop_instances['Reservations']
        for inst in res['Instances']
    ]
    
    if stop_ids:
        print(f"Stopping instances: {stop_ids}")
        ec2.stop_instances(InstanceIds=stop_ids)
    else:
        print("No instances found to stop.")

    # Find instances to start
    start_instances = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Action', 'Values': ['Auto-Start']},
            {'Name': 'instance-state-name', 'Values': ['stopped']}
        ]
    )

    start_ids = [
        inst['InstanceId']
        for res in start_instances['Reservations']
        for inst in res['Instances']
    ]
    
    if start_ids:
        print(f"Starting instances: {start_ids}")
        ec2.start_instances(InstanceIds=start_ids)
    else:
        print("No instances found to start.")
