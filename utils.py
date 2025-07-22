def format_prompt(metrics, forecast):
    cpu_max = max([d['Maximum'] for d in metrics['CPUUtilization']]) if metrics['CPUUtilization'] else 0
    mem_avg = sum([d['Average'] for d in metrics['MemoryUtilization']]) / len(metrics['MemoryUtilization']) if metrics['MemoryUtilization'] else 0
    prompt = f"""
EC2 CPU and memory usage in last 6 hours:
- CPU peak: {cpu_max:.2f}%
- Memory average: {mem_avg:.2f}%

Forecast next 6 hours:
{forecast.to_string(index=False)}

Summarize this and suggest optimizations.
"""
    return prompt
