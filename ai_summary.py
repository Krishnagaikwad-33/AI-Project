import requests

def generate_prompt(cpu_data, mem_data, forecast_df):
    # Compute simple stats
    cpu_avg = sum([point['Average'] for point in cpu_data]) / len(cpu_data) if cpu_data else 0
    cpu_max = max([point['Maximum'] for point in cpu_data]) if cpu_data else 0
    mem_avg = sum([point['Average'] for point in mem_data]) / len(mem_data) if mem_data else 0
    mem_max = max([point['Maximum'] for point in mem_data]) if mem_data else 0

    future_max = forecast_df['yhat'].max() if not forecast_df.empty else 0
    future_min = forecast_df['yhat'].min() if not forecast_df.empty else 0

    prompt = f"""
You are a cloud cost and infrastructure optimization assistant.

Based on this EC2 instance's recent behavior, analyze and recommend actions:

🔹 Recent CPU Usage:
- Avg: {cpu_avg:.2f}% | Max: {cpu_max:.2f}%

🔹 Recent Memory Usage:
- Avg: {mem_avg:.2f}% | Max: {mem_max:.2f}%

🔹 Forecast (Next 6–12 hours):
- CPU Max Forecast: {future_max:.2f}% | Min: {future_min:.2f}%

Answer:
- Analyze if this instance is under or over-utilized.
- Predict future usage pattern (stable, spiky, underused).
- Recommend actions (e.g., resize instance, add auto-scaling, keep as-is).
Keep the tone professional, 5–6 lines max.
"""
    return prompt.strip()

def query_ollama_llama3(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",  # Change this if Ollama runs elsewhere
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        result = response.json()
        return result.get("response", "⚠️ No response from model.")
    except Exception as e:
        return f"⚠️ AI summary generation failed: {e}"

def generate_ai_summary(cpu_data, mem_data, forecast_df):
    prompt = generate_prompt(cpu_data, mem_data, forecast_df)
    return query_ollama_llama3(prompt)
