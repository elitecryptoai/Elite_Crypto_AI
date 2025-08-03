# regen_controller.py — ULTRA INTELLIGENT SELF-HEALING SYSTEM (FULL EVOLUTION PATCH)

import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

REGEN_QUEUE = "logs/regen_queue.json"
FAILURE_LOG = "logs/regen_failures.json"
METRICS_FILE = "logs/repair_metrics.json"
HEALTH_SCORES = "logs/agent_health_scores.json"
EVOLUTION_LOG = "logs/agent_evolution_log.json"
MANIFEST_FILE = "agents/manifest.json"
FORECAST_LOG = "logs/forecast_history.json"
PERFORMANCE_LOG = "intel/performance_metrics.json"

MAX_AGENTS_PER_RUN = 10
CRITICAL_AGENTS = ["execution_agent.py", "forecast_agent.py"]
STALE_THRESHOLD_DAYS = 7
REGEN_INTERVAL_HOURS = 6

# ✅ Load logs safely
def safe_load(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

# 🕰️ Get last modified time of agent
def get_last_modified(path):
    try:
        return datetime.utcfromtimestamp(Path(path).stat().st_mtime)
    except:
        return datetime.utcnow() - timedelta(days=365)

# 📊 Score each agent's health based on multiple signals
def score_agents():
    failures = safe_load(FAILURE_LOG)
    metrics = safe_load(METRICS_FILE)
    performance = safe_load(PERFORMANCE_LOG)
    forecast = safe_load(FORECAST_LOG)

    fail_counts = defaultdict(int)
    for entry in failures:
        name = entry["agent"]
        ts = datetime.fromisoformat(entry["timestamp"])
        if datetime.utcnow() - ts < timedelta(days=7):
            fail_counts[name] += 1

    health = {}
    now = datetime.utcnow()
    for file in os.listdir("agents"):
        if not file.endswith(".py") or file.startswith("__"):
            continue
        penalty = fail_counts[file] * 0.2
        staleness = (now - get_last_modified(os.path.join("agents", file))).days
        stale_penalty = 0.2 if staleness > STALE_THRESHOLD_DAYS else 0
        base_score = 1.0 - penalty - stale_penalty
        if file in CRITICAL_AGENTS:
            base_score -= 0.2
        health[file] = round(max(0, base_score), 4)

    with open(HEALTH_SCORES, "w") as f:
        json.dump(health, f, indent=2)

    return health

# 🧠 Detect degradation trends
def find_degraded_agents():
    forecast_data = safe_load(FORECAST_LOG)
    degraded = set()
    for row in forecast_data[-100:]:
        try:
            model = row["forecast"]["model_used"].lower()
            score = row["forecast"].get("confidence_score", 0)
            if score < 0.4:
                degraded.add(row["token"])
        except:
            continue
    return list(degraded)

# 🧬 Smart regen queue builder with scheduling
def build_regen_queue():
    health = score_agents()
    degraded = find_degraded_agents()
    queue = sorted(health.items(), key=lambda x: x[1])
    regen_targets = [agent for agent, score in queue if score < 0.6][:MAX_AGENTS_PER_RUN]

    for file in CRITICAL_AGENTS:
        if file not in regen_targets:
            regen_targets.insert(0, file)

    for token in degraded:
        guess = f"{token}_strategy.py"
        if guess in health and guess not in regen_targets:
            regen_targets.append(guess)

    regen_targets = regen_targets[:MAX_AGENTS_PER_RUN]

    next_regen = (datetime.utcnow() + timedelta(hours=REGEN_INTERVAL_HOURS)).isoformat()
    queue_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "next_regen_time": next_regen,
        "agents": regen_targets
    }

    os.makedirs("logs", exist_ok=True)
    with open(REGEN_QUEUE, "w") as f:
        json.dump(queue_data, f, indent=2)

    print("🧠 Regen queue created:", regen_targets)
    return regen_targets

# 🧬 Evolution report generator (skeleton)
def log_agent_evolution(agent, old_score, new_score, model_used):
    log = safe_load(EVOLUTION_LOG)
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent,
        "before": old_score,
        "after": new_score,
        "model": model_used
    }
    log.append(entry)
    with open(EVOLUTION_LOG, "w") as f:
        json.dump(log[-200:], f, indent=2)

if __name__ == "__main__":
    build_regen_queue()
