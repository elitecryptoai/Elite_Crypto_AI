import subprocess
import time
import os
from datetime import datetime

AGENTS = [
    ("search_agent.py", True),
    ("strategy_agent.py", True),
    ("forecast_agent.py", True),
    ("manager_agent.py", True),
    ("rebalancer_agent.py", True),
    ("execution_agent.py", True),
    ("token_monitor.py", True),
    ("self_trainer.py", True),
    ("strategy_generator.py", True),
    ("report_builder.py", True),
    ("email_reporter.py", True)
]

LOG_FILE = "logs/sequence_log.txt"

class SequenceAgent:
    def __init__(self):
        self.log_path = LOG_FILE
        self.memory = []

    def run_agent(self, agent_name):
        print(f"[Sequence] 🔄 Running {agent_name}...")
        try:
            result = subprocess.run(["python", f"agents/{agent_name}"], capture_output=True, text=True, timeout=300)
            self.memory.append((agent_name, "✅ Success"))
            return result.stdout
        except subprocess.TimeoutExpired:
            self.memory.append((agent_name, "❌ Timeout"))
            self.run_regen(agent_name)
            return f"{agent_name} timed out"
        except Exception as e:
            self.memory.append((agent_name, f"❌ Failed: {e}"))
            self.run_regen(agent_name)
            return str(e)

    def run_regen(self, agent_name):
        print(f"[Sequence] 🛠️ Attempting to auto-repair {agent_name} via regen_controller...")
        try:
            subprocess.run(["python", "agents/regen_controller.py", agent_name], timeout=120)
        except Exception as e:
            print(f"[Sequence] ❌ Regen failed for {agent_name}: {e}")

    def run(self):
        log_lines = [f"[{datetime.utcnow().isoformat()}] Starting full system sequence..."]

        for agent, enabled in AGENTS:
            if not enabled:
                continue
            output = self.run_agent(agent)
            log_lines.append(f"--- {agent} ---\n{output}\n")

        log_lines.append("[Sequence] ✅ Sequence complete.")
        self.save_log(log_lines)
        print("[Sequence] ✅ All enabled agents executed.")

    def save_log(self, lines):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write("\n".join(lines) + "\n")

if __name__ == "__main__":
    SequenceAgent().run()
