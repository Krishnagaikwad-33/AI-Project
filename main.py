from metrics import get_metrics
from forecast import forecast_metric
from ai_summary import generate_ai_summary
from report_generator import generate_html_report
from notify import upload_to_s3_and_notify

INSTANCE_ID = "i-0cbb6adb845b51f42"
REGION = "eu-west-1"
S3_BUCKET = "prod-ec2-cpu-utilization-reports"
SNS_TOPIC = "arn:aws:sns:eu-west-1:973597288417:ai-ec2-report"

def main():
    print("📡 Fetching metrics...")
    metrics = get_metrics(INSTANCE_ID, REGION)

    print("📈 Forecasting CPU usage...")
    forecast_df = forecast_metric(metrics['CPUUtilization'], "CPUUtilization")

    print("🤖 Generating AI summary via Ollama...")
    ai_summary = generate_ai_summary(
        cpu_data=metrics["CPUUtilization"],
        mem_data=metrics["Memory Available MBytes"],
        forecast_df=forecast_df
    )

    print("📄 Generating HTML report...")
    html_path = "ec2_ai_report.html"
    generate_html_report(
        instance_name=metrics["InstanceName"],
        private_ip=metrics["PrivateIp"],
        cpu_data=metrics["CPUUtilization"],
        mem_data=metrics["Memory Available MBytes"],
        forecast_df=forecast_df,
        ai_summary=ai_summary,
        output_path=html_path
    )

    print("☁️ Uploading to S3 and notifying SNS...")
    report_url = upload_to_s3_and_notify(html_path, S3_BUCKET, SNS_TOPIC)

    print(f"✅ Done. Report URL: {report_url}")

if __name__ == "__main__":
    main()
