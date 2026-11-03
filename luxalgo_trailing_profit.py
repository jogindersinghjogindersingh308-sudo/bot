"""
Engine #20: High-Watermark Peak Profit & Dynamic Trailing Lock Engine
Implements Master Rule #6:
- Tracks Peak Unrealized Profit (High-Water Mark)
- Lets winners run uncapped ("ਜਿੰਨਾ ਪ੍ਰਾਫਿਟ ਬਣਦਾ ਹੈ, ਬਣਨ ਦੇਣਾ")
- Detects the exact moment money starts slipping away ("ਕਮ ਪੈਸੇ ਤੁਰੇ ਜਾਂਦੇ ਆ" / "ਗੇਮ ਘੁੰਮ ਗਈ")
- Calculates Auto-Compounding position sizing for the $20K Goal
"""
import json
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(_DIR, "profit_trail_state.json")

class HighWatermarkProfitEngine:
    def __init__(self, state_file=STATE_FILE):
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"peak_pnl": 0.0, "position_active": False, "side": None}

    def _save_state(self):
        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception:
            pass

    def reset(self):
        self.state = {"peak_pnl": 0.0, "position_active": False, "side": None}
        self._save_state()

    def update_position(self, current_pnl, side):
        self.state["position_active"] = True
        self.state["side"] = side
        if current_pnl > self.state["peak_pnl"]:
            self.state["peak_pnl"] = current_pnl
        self._save_state()

        peak = self.state["peak_pnl"]
        should_exit = False
        reason = ""

        # Trailing rules
        if peak >= 10.0:
            # If we reached +$10 or higher, lock in at least 75% of profits (allow 25% retracement)
            threshold = peak * 0.75
            if current_pnl < threshold:
                should_exit = True
                reason = f"PEAK PROFIT LOCK: Reached +${peak:.2f}, slipped to +${current_pnl:.2f} ('ਕਮ ਪੈਸੇ ਤੁਰੇ ਜਾਂਦੇ ਆ')!"
        elif peak >= 5.0:
            # If reached +$5, don't let it drop below +$3.5
            threshold = peak * 0.70
            if current_pnl < threshold:
                should_exit = True
                reason = f"PROFIT RETRACEMENT: Reached +${peak:.2f}, slipped to +${current_pnl:.2f} ('ਕਮ ਪੈਸੇ ਤੁਰੇ ਜਾਂਦੇ ਆ')!"
        elif peak >= 2.5:
            # If reached +$2.5, lock in at +$1.5
            if current_pnl < 1.5:
                should_exit = True
                reason = f"EARLY PROFIT SECURED: Peak was +${peak:.2f}, securing +${current_pnl:.2f}!"

        return {
            "peak_pnl": round(peak, 2),
            "current_pnl": round(current_pnl, 2),
            "should_exit": should_exit,
            "exit_reason": reason
        }

    def calculate_compounding_size(self, net_equity, btc_price, leverage=3.0):
        """
        Calculates position size dynamically based on equity to compound towards 20K goal.
        Uses 70% of available equity at safe 3x leverage.
        """
        try:
            usable_margin = net_equity * 0.70
            notional = usable_margin * leverage
            # 1 contract of BTCUSD is 0.001 BTC (~$80 at $80,000 BTC)
            contract_value = btc_price * 0.001
            contracts = int(notional / contract_value) if contract_value > 0 else 10
            return max(10, contracts)
        except Exception:
            return 10
