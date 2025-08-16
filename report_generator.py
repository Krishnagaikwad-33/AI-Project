import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime

def generate_html_report(instance_name, private_ip, cpu_data, mem_data, forecast_df, ai_summary, output_path='ec2_report.html'):
    plots = generate_plot_html(cpu_data, mem_data, forecast_df)

    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>EC2 Monitoring Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f9f9f9; }}
        .card {{ background: #fff; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1, h2 {{ color: #333; }}
        .summary {{ white-space: pre-wrap; font-size: 16px; background: #f3f3f3; padding: 10px; border-radius: 5px; }}
        footer {{ text-align: center; font-size: 12px; color: #888; margin-top: 40px; }}
    </style>
</head>
<body>
    <h1>EC2 Usage Report</h1>
    <p><strong>Instance:</strong> {instance_name} &nbsp;|&nbsp; <strong>Private IP:</strong> {private_ip} &nbsp;|&nbsp; <strong>Generated:</strong> {timestamp}</p>

    <div class="card">
        <h2>CPU Usage</h2>
        {plots['cpu_chart']}
    </div>

    <div class="card">
        <h2>Memory Usage</h2>
        {plots['mem_chart']}
    </div>

    <div class="card">
        <h2>CPU Forecast (Prophet)</h2>
        {plots['forecast_chart']}
    </div>

    <div class="card">
        <h2>AI Summary & Recommendations</h2>
        <div class="summary">{ai_summary}</div>
    </div>

    <footer>© {datetime.utcnow().year} EC2 Analyzer • Powered by AWS, Prophet & LLaMA</footer>
</body>
</html>
"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Report saved to: {output_path}")
