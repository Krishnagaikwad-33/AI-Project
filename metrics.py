import boto3
from datetime import datetime, timedelta

def get_metrics(instance_id, region, days=30):
    cloudwatch = boto3.client("cloudwatch", region_name=region)
    ec2 = boto3.client("ec2", region_name=region)

    # Time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)

    # Choose period based on range
    if days <= 3:
        period = 300   # 5 minutes for short-term
    else:
        period = 3600  # 1 hour for long-term

    def fetch_metric(metric_name):
        if metric_name == "Memory Available MBytes":
            namespace = "CWAgent"
            unit = "None"
        else:
            namespace = "AWS/EC2"
            unit = "Percent"

        dimensions = [{"Name": "InstanceId", "Value": instance_id}]

        response = cloudwatch.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=dimensions,
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=["Average", "Maximum"],
            Unit=unit
        )

        # Sort by timestamp
        data = sorted(response["Datapoints"], key=lambda x: x["Timestamp"])

        # Clip CPU utilization values to 0–100
        if metric_name == "CPUUtilization":
            for dp in data:
                dp["Average"] = max(0, min(100, dp["Average"]))
                dp["Maximum"] = max(0, min(100, dp["Maximum"]))

        return data

    # Get EC2 instance details
    instance_desc = ec2.describe_instances(InstanceIds=[instance_id])
    instance_info = instance_desc["Reservations"][0]["Instances"][0]

    name_tag = next(
        (tag["Value"] for tag in instance_info.get("Tags", []) if tag["Key"] == "Name"),
        "Unnamed"
    )
    private_ip = instance_info.get("PrivateIpAddress", "N/A")

    return {
        "Memory Available MBytes": fetch_metric("Memory Available MBytes"),
        "CPUUtilization": fetch_metric("CPUUtilization"),
        "InstanceName": name_tag,
        "PrivateIp": private_ip
    }
