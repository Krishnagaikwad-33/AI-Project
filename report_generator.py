import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime

def generate_plot_html(cpu_data, mem_data, forecast_df):
    # Time format fix
    cpu_times = [point['Timestamp'].strftime('%Y-%m-%d %H:%M') for point in cpu_data]
    mem_times = [point['Timestamp'].strftime('%Y-%m-%d %H:%M') for point in mem_data]
    forecast_times = forecast_df['ds'].dt.strftime('%Y-%m-%d %H:%M')

    # CPU Usage Chart
    fig_cpu = go.Figure()
    fig_cpu.add_trace(go.Scatter(x=cpu_times, y=[pt['Average'] for pt in cpu_data],
                                 mode='lines+markers', name='CPU Avg', line=dict(color='royalblue')))
    fig_cpu.add_trace(go.Scatter(x=cpu_times, y=[pt['Maximum'] for pt in cpu_data],
                                 mode='lines', name='CPU Max', line=dict(dash='dot', color='red')))
    fig_cpu.update_layout(title='CPU Utilization Trend', xaxis_title='Time', yaxis_title='Usage %', height=400)

    # Memory Usage Chart
    fig_mem = go.Figure()
    fig_mem.add_trace(go.Scatter(x=mem_times, y=[pt['Average'] for pt in mem_data],
                                 mode='lines+markers', name='Memory Avg', line=dict(color='green')))
    fig_mem.add_trace(go.Scatter(x=mem_times, y=[pt['Maximum'] for pt in mem_data],
                                 mode='lines', name='Memory Max', line=dict(dash='dot', color='orange')))
    fig_mem.update_layout(title='Memory Utilization Trend', xaxis_title='Time', yaxis_title='Usage %', height=400)

    # Forecast Chart
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(x=forecast_times, y=forecast_df['yhat'], mode='lines', name='Forecast (CPU)', line=dict(color='purple')))
    fig_forecast.update_layout(title='CPU Forecast (Prophet)', xaxis_title='Future Time', yaxis_title='Predicted Usage %', height=400)

    # Export HTML divs
    return {
        'cpu_chart': pio.to_html(fig_cpu, full_html=False, include_plotlyjs='cdn'),
        'mem_chart': pio.to_html(fig_mem, full_html=False, include_plotlyjs=False),
        'forecast_chart': pio.to_html(fig_forecast, full_html=False, include_plotlyjs=False)
    }

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
