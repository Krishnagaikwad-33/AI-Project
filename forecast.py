from prophet import Prophet
import pandas as pd

def forecast_metric(datapoints, metric_label='CPUUtilization'):
    if not datapoints:
        return None

    df = pd.DataFrame(datapoints)

    # Convert to datetime and strip timezone info
    df['ds'] = pd.to_datetime(df['Timestamp']).dt.tz_localize(None)
    df['y'] = df['Average']
    df = df[['ds', 'y']]

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=6, freq='H')
    forecast = model.predict(future)
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(6)
