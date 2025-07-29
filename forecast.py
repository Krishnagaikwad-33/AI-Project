from prophet import Prophet
import pandas as pd

def forecast_metric(datapoints, metric_label='CPUUtilization'):
    if not datapoints:
        return None

    df = pd.DataFrame(datapoints)
    if len(df) < 10:
        print(f"Not enough data to forecast for {metric_label}")
        return None

    df['ds'] = pd.to_datetime(df['Timestamp']).dt.tz_localize(None)
    df['y'] = df['Average']
    df = df[['ds', 'y']]

    model = Prophet(daily_seasonality=True, weekly_seasonality=False, yearly_seasonality=False)
    model.add_seasonality(name='hourly', period=24, fourier_order=5)
    model.fit(df)

    interval = (df['ds'].iloc[-1] - df['ds'].iloc[-2]).seconds // 60
    freq = f"{interval}min"
    future = model.make_future_dataframe(periods=6, freq=freq)

    forecast = model.predict(future)
    forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    forecast['Metric'] = metric_label
    return forecast.tail(6)

