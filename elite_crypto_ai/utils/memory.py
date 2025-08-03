# utils/memory.py

import json
import os

MEMORY_FILE = "logs/rebalancer_memory.json"


def load_allocation_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_allocation_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)