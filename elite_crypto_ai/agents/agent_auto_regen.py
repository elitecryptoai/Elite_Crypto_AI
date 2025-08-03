 ULTRA ELITE SELF-HEALING AI CORE (V3.0+ FULL REPAIR SYSTEM)

import os
import json
import traceback
import importlib.util
from datetime import datetime
from collections import defaultdict
from agents.utils.llm import query_llm_with_fallback
from utils.repair_utils import detect_common_error, adjust_prompt

AGENT_DIR = "agents"
BACKUP_DIR = "logs/regen_backups"
LOG_FILE = "logs/regen_log.json"
FAILURE_LOG = "logs/regen_failures.json"
METRICS_FILE = "logs/repair_metrics.json"
MANIFEST_FILE = "agents/manifest.json"

REPAIR_MODELS = [
    {"model": "gpt-4", "style": "strict"},
    {"model": "claude", "style": "soft"},
    {"model": "gemini", "style": "adaptive"}
]

# ✅ Smoke tests: basic module-level execution

def run_smoke_test(agent_path):
    try:
        name = os.path.basename(agent_path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(name, agent_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, name.title().replace("_", "")) or hasattr(mod, "run"):
            return True
    except:
        return False
    return False

# 📓 Logging

def log_regen(agent_name, model, reason, success):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            log = json.load(f)
    log.append({
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent_name,
        "model": model,
        "reason": reason,
        "success": success
    })
    with open(LOG_FILE, "w") as f:
        json.dump(log[-200:], f, indent=2)

# ⚠️ Failed pattern logging

def log_failure(agent_name, traceback_msg, model):
    entry = {
        "agent": agent_name,
        "error": traceback_msg,
        "model": model,
        "timestamp": datetime.utcnow().isoformat()
    }
    if os.path.exists(FAILURE_LOG):
        with open(FAILURE_LOG, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(FAILURE_LOG, "w") as f:
        json.dump(data[-300:], f, indent=2)

# 📊 Track model repair performance

def update_metrics(model, success):
    scores = defaultdict(lambda: {"attempts": 0, "successes": 0})
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "r") as f:
            raw = json.load(f)
            for m, d in raw.items():
                scores[m] = d
    scores[model]["attempts"] += 1
    if success:
        scores[model]["successes"] += 1
    with open(METRICS_FILE, "w") as f:
        json.dump(scores, f, indent=2)

# 🧠 Main repair logic

def regenerate_agent(agent_name):
    path = os.path.join(AGENT_DIR, agent_name)
    if not os.path.exists(path):
        reason = "Missing file"
    else:
        try:
            with open(path, "r") as f:
                code = f.read()
            compile(code, agent_name, 'exec')
            return
        except Exception as e:
            reason = str(e)

    print(f"🔧 Repairing {agent_name} due to: {reason}")

    if os.path.exists(path):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        backup_path = os.path.join(BACKUP_DIR, f"{agent_name}.{datetime.utcnow().timestamp()}.bak")
        with open(path, "r") as f:
            open(backup_path, "w").write(f.read())

    error_type = detect_common_error(reason)

    for tier in REPAIR_MODELS:
        try:
            prompt = f"""
You are a self-healing AI agent repairer.
The agent `{agent_name}` failed due to: {reason}
"""
            if os.path.exists(path):
                with open(path, "r") as f:
                    original_code = f.read()
                prompt += f"\nBroken Code:\n```python\n{original_code}\n```\n"
            else:
                prompt += "Missing file. Please regenerate it.\n"

            prompt = adjust_prompt(prompt, error_type)
            prompt += "\nRespond with ONLY FIXED Python code."

            repaired = query_llm_with_fallback(prompt, model_name=tier["model"])
            with open(path, "w") as f:
                f.write(repaired)

            if run_smoke_test(path):
                print(f"✅ {agent_name} repaired with {tier['model']}")
                log_regen(agent_name, tier["model"], reason, True)
                update_metrics(tier["model"], True)
                return
            else:
                print(f"❌ Repair failed test with {tier['model']}")
                log_regen(agent_name, tier["model"], reason, False)
                update_metrics(tier["model"], False)
                log_failure(agent_name, reason, tier["model"])
        except Exception as e:
            log_regen(agent_name, tier["model"], str(e), False)
            log_failure(agent_name, str(e), tier["model"])
            update_metrics(tier["model"], False)

    print(f"🛑 All repair attempts failed for {agent_name}")

# 🚦 Priority-aware regen order

def get_ordered_agent_list():
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE, "r") as f:
            manifest = json.load(f)
        return sorted(manifest["agents"].keys(), key=lambda k: -manifest["agents"][k])
    return sorted([f for f in os.listdir(AGENT_DIR) if f.endswith(".py")])

# 🔁 Main runner

def run():
    print("🛠️ Running Agent Auto-Regenerator...")
    os.makedirs(AGENT_DIR, exist_ok=True)
    for file in get_ordered_agent_list():
        if file.endswith(".py") and not file.startswith("__"):
            regenerate_agent(file)
    print("✅ Auto-regeneration complete.")

if __name__ == "__main__":
    run()
