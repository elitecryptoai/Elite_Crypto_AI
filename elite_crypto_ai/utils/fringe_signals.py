# utils/fringe_signals.py

import random

def detect_anomalies(token):
    # Fake alert: returns True ~10% of the time
    return random.random() < 0.1
