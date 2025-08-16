from prophet import Prophet
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
import os

def forecast_metric(datapoints, metric_label='CPUUtilization', output_html="forecast_report.html"):
    if not datapoints:
        print(f"No data for {metric_label}")
        return None

    df = pd.DataFrame(datapoints)
    if len(df) < 10:
        print(f"Not enough data for {metric_label} forecast")
        return None

    # Prepare data for Prophet (remove timezone, keep only last 30 days)
    df['ds'] = pd.to_datetime(df['Timestamp']).dt.tz_localize(None)
    df['y'] = df['Average']
    df = df[['ds', 'y']]

    # Filter last 30 days for better training
    max_date = df['ds'].max()
    min_date = max_date - pd.Timedelta(days=30)
    df = df[df['ds'] >= min_date]

    # Train model
    model = Prophet(interval_width=0.95, daily_seasonality=True)
    model.fit(df)

    # Predict next 24 hours
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)

    # Cap predictions at 100% for CPU utilization
    forecast['yhat'] = forecast['yhat'].clip(upper=100)
    forecast['yhat_upper'] = forecast['yhat_upper'].clip(upper=100)
    forecast['yhat_lower'] = forecast['yhat_lower'].clip(upper=100)

    forecast_filtered = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

    # Save CSV and Excel files
    csv_filename = output_html.replace(".html", ".csv")
    xlsx_filename = output_html.replace(".html", ".xlsx")
    forecast_filtered.to_csv(csv_filename, index=False)
    forecast_filtered.to_excel(xlsx_filename, index=False)

    # Create Plotly chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['ds'], y=df['y'],
                             mode='lines+markers', name=f"Actual {metric_label}"))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'],
                             mode='lines', name='Forecast'))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'],
                             mode='lines', line=dict(color="red", dash="dot"),
                             name='Upper Bound'))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'],
                             mode='lines', line=dict(color="green", dash="dot"),
                             name='Lower Bound'))
    fig.add_trace(go.Scatter(
        x=list(forecast['ds']) + list(forecast['ds'][::-1]),
        y=list(forecast['yhat_upper']) + list(forecast['yhat_lower'][::-1]),
        fill='toself',
        fillcolor='rgba(255, 215, 0, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=False
    ))

    fig.update_layout(
        title=f"{metric_label} Forecast (Next 24 Hours)",
        xaxis_title='Time',
        yaxis_title=metric_label,
        yaxis=dict(range=[0, 100]),  # 🔹 Lock y-axis between 0 and 100
        hovermode='x unified'
    )

    forecast_chart_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

    # HTML report with download links
    html_content = f"""
    <html>
    <head>
        <title>{metric_label} Forecast Report</title>
    </head>
    <body>
        <h1>{metric_label} Forecast Report</h1>
        {forecast_chart_html}
        <h2>Download Forecast Data</h2>
        <a href="{os.path.basename(csv_filename)}" download>Download as CSV</a> |
        <a href="{os.path.basename(xlsx_filename)}" download>Download as Excel</a>
    </body>
    </html>
    """

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Forecast HTML report saved to {output_html}")
    print(f"CSV file: {csv_filename}")
    print(f"Excel file: {xlsx_filename}")
    return output_html
