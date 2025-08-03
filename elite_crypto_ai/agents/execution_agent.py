# execution_agent.py

import json
import os
from datetime import datetime
from utils.wallet import update_wallet, get_wallet
from utils.source_manager import get_price

EXEC_LOG = "data/execution_log.json"
TRADE_MODE = "paper"  # or "live"


def execute_trade(symbol, amount_usdc, action, wallet_type="medium"):
    price = get_price(symbol)
    if price is None:
        return {"status": "error", "reason": "Price unavailable"}

    qty = round(amount_usdc / price, 6)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    if TRADE_MODE == "paper":
        update_wallet(wallet_type, symbol, qty, price, action)
    elif TRADE_MODE == "live":
        # Future real trade via MetaMask or Uniswap integration
        return {"status": "error", "reason": "Live trading not enabled"}

    log_trade({
        "timestamp": now,
        "symbol": symbol,
        "action": action,
        "price": price,
        "qty": qty,
        "wallet": wallet_type,
        "mode": TRADE_MODE,
    })

    return {"status": "ok", "price": price, "qty": qty, "mode": TRADE_MODE}


def log_trade(entry):
    if not os.path.exists(EXEC_LOG):
        trades = []
    else:
        with open(EXEC_LOG, "r") as f:
            trades = json.load(f)
    trades.append(entry)
    with open(EXEC_LOG, "w") as f:
        json.dump(trades, f, indent=2)


def get_execution_log():
    if not os.path.exists(EXEC_LOG):
        return []
    with open(EXEC_LOG, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    print(execute_trade("ETH", 500, "buy", "medium"))
