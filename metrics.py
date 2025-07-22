import boto3
from datetime import datetime, timedelta

def get_metrics(instance_id, region):
    cloudwatch = boto3.client("cloudwatch", region_name=region)
    ec2 = boto3.client("ec2", region_name=region)

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=6)

    def fetch_metric(metric_name, unit="Percent"):
        response = cloudwatch.get_metric_statistics(
            Namespace="CWAgent" if metric_name == "MemoryUtilization" else "AWS/EC2",
            MetricName=metric_name,
            Dimensions=[
                {"Name": "InstanceId", "Value": instance_id}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=["Average", "Maximum"],
            Unit=unit
        )
        # Sort by timestamp
        return sorted(response["Datapoints"], key=lambda x: x["Timestamp"])

    # Get instance metadata
    instance_desc = ec2.describe_instances(InstanceIds=[instance_id])
    instance_info = instance_desc["Reservations"][0]["Instances"][0]
    
    # Extract Name tag and private IP
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
