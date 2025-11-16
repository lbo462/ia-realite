# metrics_collector.py
import time
import csv
import os
import subprocess
from typing import Optional, Callable, Tuple, Any, Dict
import psutil

OUT_CSV = os.path.join(os.path.dirname(__file__), "metrics_log.csv")
# grid intensity default gCO2/kWh (override via ENV)
GRID_GCO2_PER_KWH = float(os.getenv("GRID_GCO2_PER_KWH", "22.0"))
SYSTEM_TDP_W = float(os.getenv("SYSTEM_TDP_W", "30.0"))  # crude default, override if known

def _nvidia_smi_power_once() -> Optional[float]:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=power.draw", "--format=csv,noheader,nounits"],
            stderr=subprocess.DEVNULL,
            timeout=1,
        )
        val = out.decode().strip().splitlines()[0]
        return float(val)
    except Exception:
        return None

def _estimate_cpu_power_w() -> float:
    # Very rough estimate: fraction of TDP
    cpu_pct = psutil.cpu_percent(interval=0.01)
    return SYSTEM_TDP_W * (cpu_pct / 100.0)

def _avg_power_w(pre_w: Optional[float], post_w: Optional[float]) -> float:
    if pre_w is not None and post_w is not None:
        return (pre_w + post_w) / 2.0
    if pre_w is not None:
        return pre_w
    if post_w is not None:
        return post_w
    return _estimate_cpu_power_w()

def _append_csv(metrics: Dict[str, Any]):
    exists = os.path.exists(OUT_CSV)
    with open(OUT_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(metrics.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(metrics)

def measure_inference(callable_fn: Callable[..., Any], *args, **kwargs) -> Tuple[Any, Dict]:
    """
    Wrap a model-callable to measure duration, power estimate, energy, CO2, tokens.
    Returns (result, metrics_dict).
    """
    # Pre-sample power (try GPU)
    pre_gpu = _nvidia_smi_power_once()
    start = time.perf_counter()
    result = callable_fn(*args, **kwargs)
    end = time.perf_counter()
    post_gpu = _nvidia_smi_power_once()

    duration_s = end - start
    power_w = _avg_power_w(pre_gpu, post_gpu)
    energy_Wh = power_w * duration_s / 3600.0
    energy_kWh = energy_Wh / 1000.0
    co2_g = energy_kWh * GRID_GCO2_PER_KWH
    co2_mg = co2_g * 1000.0

    # Try to detect token count in common places (dict usage or attributes)
    tokens = None
    try:
        if isinstance(result, dict):
            usage = result.get("usage") or result.get("metrics") or {}
            if isinstance(usage, dict):
                tokens = usage.get("total_tokens") or usage.get("completion_tokens") or usage.get("prompt_tokens")
        else:
            # object with .usage or .content
            tokens_attr = getattr(result, "usage", None)
            if isinstance(tokens_attr, dict):
                tokens = tokens_attr.get("total_tokens")
    except Exception:
        tokens = None

    tokens = tokens or 0
    tokens_per_joule = tokens / (energy_Wh + 1e-12)  # tokens per Wh (avoid /0)
    tokens_per_joule = tokens / (energy_Wh * 3600.0 + 1e-12) if False else tokens / max(energy_Wh, 1e-12)  # keep tokens/Wh

    metrics = {
        "timestamp": time.time(),
        "duration_s": duration_s,
        "power_w": power_w,
        "energy_Wh": energy_Wh,
        "energy_kWh": energy_kWh,
        "co2_g": co2_g,
        "co2_mg": co2_mg,
        "tokens": tokens,
        "tokens_per_Wh": tokens_per_joule,
    }

    try:
        _append_csv(metrics)
    except Exception:
        pass

    return result, metrics
