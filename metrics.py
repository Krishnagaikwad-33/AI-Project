import boto3
from datetime import datetime, timedelta

def get_metrics(instance_id, region):
    cloudwatch = boto3.client("cloudwatch", region_name=region)
    ec2 = boto3.client("ec2", region_name=region)

    # Last 30 days
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=30)

    def fetch_metric(metric_name, unit="Percent"):
        if metric_name == "MemoryUtilization":
            # For memory, use CWAgent namespace and proper metric name
            actual_metric = "mem_used_percent"
            namespace = "CWAgent"
            dimensions = [
                {"Name": "InstanceId", "Value": instance_id},
                {"Name": "ImageId", "Value": get_image_id(instance_id, region)},
                {"Name": "InstanceType", "Value": get_instance_type(instance_id, region)}
            ]
        else:
            # For CPU
            actual_metric = metric_name
            namespace = "AWS/EC2"
            dimensions = [{"Name": "InstanceId", "Value": instance_id}]
        
        response = cloudwatch.get_metric_statistics(
            Namespace=namespace,
            MetricName=actual_metric,
            Dimensions=dimensions,
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=["Average", "Maximum"],
            Unit=unit
        )
        return sorted(response["Datapoints"], key=lambda x: x["Timestamp"])

    def get_image_id(instance_id, region):
        # Required for CWAgent dimensions
        ec2 = boto3.client('ec2', region_name=region)
        instance = ec2.describe_instances(InstanceIds=[instance_id])
        return instance['Reservations'][0]['Instances'][0]['ImageId']

    def get_instance_type(instance_id, region):
        # Required for CWAgent dimensions
        ec2 = boto3.client('ec2', region_name=region)
        instance = ec2.describe_instances(InstanceIds=[instance_id])
        return instance['Reservations'][0]['Instances'][0]['InstanceType']

    # Get instance details
    instance_desc = ec2.describe_instances(InstanceIds=[instance_id])
    instance_info = instance_desc["Reservations"][0]["Instances"][0]

    name_tag = next(
        (tag["Value"] for tag in instance_info.get("Tags", []) if tag["Key"] == "Name"),
        "Unnamed"
    )
    private_ip = instance_info.get("PrivateIpAddress", "N/A")

    return {
        "CPUUtilization": fetch_metric("CPUUtilization"),
        "MemoryUtilization": fetch_metric("MemoryUtilization"),
        "InstanceName": name_tag,
        "PrivateIp": private_ip
    }
