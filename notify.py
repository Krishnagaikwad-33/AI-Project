import boto3
import uuid

def upload_to_s3_and_notify(html_file_path, bucket_name, topic_arn):
    s3 = boto3.client('s3')
    sns = boto3.client('sns')

    filename = f"ec2-report-{uuid.uuid4().hex}.html"

    # ✅ Read actual contents of the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # ✅ Upload the real HTML content
    s3.put_object(Body=html_content, Bucket=bucket_name, Key=filename, ContentType='text/html')

    url = f"https://{bucket_name}.s3.amazonaws.com/{filename}"
    message = f"EC2 Monitoring Report is ready:\n{url}"
    sns.publish(TopicArn=topic_arn, Message=message, Subject="EC2 Usage Report")

    return url
