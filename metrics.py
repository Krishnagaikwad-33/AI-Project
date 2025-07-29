import boto3
from datetime import datetime, timedelta

def get_metrics(instance_id, region):
    cloudwatch = boto3.client("cloudwatch", region_name=region)
    ec2 = boto3.client("ec2", region_name=region)

    # Time range: last 2 days
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=2)

    def fetch_metric(metric_name):
        if metric_name == "Memory Available MBytes":
            namespace = "CWAgent"
            unit = "None"  # Memory metrics typically use 'None'
        else:
            namespace = "AWS/EC2"
            unit = "Percent"  # CPU and other EC2 metrics use 'Percent'

        # Shared dimensions
        dimensions = [{"Name": "InstanceId", "Value": instance_id}]

        response = cloudwatch.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=dimensions,
            StartTime=start_time,
            EndTime=end_time,
            Period=300,  # 5 minutes
            Statistics=["Average", "Maximum"],
            Unit=unit
        )

        return sorted(response["Datapoints"], key=lambda x: x["Timestamp"])

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
