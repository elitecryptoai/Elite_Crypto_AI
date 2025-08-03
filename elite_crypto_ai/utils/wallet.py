# untils/wallet.py
import json
import os

WALLET_PATH = "wallets/wallet.json"


def get_wallet_holdings():
    if not os.path.exists(WALLET_PATH):
        return {}
    with open(WALLET_PATH, "r") as f:
        return json.load(f)


def update_wallet(wallet_type, symbol, qty, price, action):
    wallet = get_wallet_holdings()
    if action == "buy":
        wallet[symbol] = wallet.get(symbol, 0) + qty
    elif action == "sell":
        wallet[symbol] = max(wallet.get(symbol, 0) - qty, 0)
    with open(WALLET_PATH, "w") as f:
        json.dump(wallet, f, indent=2)


def get_wallet_value():
    return {"total": 10000}  # stub until pricing hooked in

def get_wallet_allocation():
    return {"safe": 0.5, "medium": 0.3, "risky": 0.2}
