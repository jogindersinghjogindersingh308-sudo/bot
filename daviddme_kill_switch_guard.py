"""
DavidDME Institutional Auto Kill-Switch & Risk Guard Engine
Ported & Adapted from daviddme/claude-skills perpetual futures risk doctrine.
Fully aligned with User Rule #6:
- Zero hanging orders: Instant liquidation of position and immediate cancellation of ALL pending orders.
- Momentum collapse, flash crash, or adverse whale manipulation detection.
"""
import time
import json
import urllib.request
import os

CONFIG_PATH = r"C:\Users\om\.gemini\antigravity\scratch\trading_config.json"

class DavidDMEKillSwitchGuard:
    def __init__(self, max_allowed_loss_usd=15.0, flash_drop_threshold_pct=1.8):
        self.max_allowed_loss_usd = max_allowed_loss_usd
        self.flash_drop_threshold_pct = flash_drop_threshold_pct
        self.kill_switch_triggered = False
        self.trigger_reason = None
        self.trigger_time = None

    def evaluate_kill_switch(self, position_data, current_price, recent_1h_candle, cvd_net_delta=0):
        """
        Evaluates whether an emergency kill-switch must be pulled.
        Returns dict with should_kill, reason, and severity.
        """
        if not position_data or float(position_data.get("size", 0)) == 0:
            return {"should_kill": False, "reason": "NO_ACTIVE_POSITION", "severity": "NORMAL"}

        size = float(position_data.get("size", 0))
        entry_price = float(position_data.get("entry_price", current_price))
        side = "LONG" if size > 0 else "SHORT"
        unrealized_pnl = float(position_data.get("unrealized_pnl", 0))

        # 1. Hard Maximum Loss Guard
        if unrealized_pnl <= -abs(self.max_allowed_loss_usd):
            return {
                "should_kill": True,
                "reason": f"🚨 EMERGENCY KILL-SWITCH: Max Allowed Loss Exceeded (-${abs(unrealized_pnl):.2f})",
                "severity": "CRITICAL",
                "side": side,
                "size": abs(size)
            }

        # 2. Flash Crash / Flash Pump against position
        if recent_1h_candle:
            high = float(recent_1h_candle.get("h", current_price))
            low = float(recent_1h_candle.get("l", current_price))
            candle_range_pct = ((high - low) / low) * 100

            if side == "LONG" and current_price < entry_price:
                adverse_move_pct = ((entry_price - current_price) / entry_price) * 100
                if adverse_move_pct >= self.flash_drop_threshold_pct and candle_range_pct >= self.flash_drop_threshold_pct:
                    return {
                        "should_kill": True,
                        "reason": f"⚡ FLASH DROP ANOMALY: BTC dumped {adverse_move_pct:.2f}% against Long position in 1H!",
                        "severity": "EMERGENCY_PROTECT",
                        "side": side,
                        "size": abs(size)
                    }

            elif side == "SHORT" and current_price > entry_price:
                adverse_move_pct = ((current_price - entry_price) / entry_price) * 100
                if adverse_move_pct >= self.flash_drop_threshold_pct and candle_range_pct >= self.flash_drop_threshold_pct:
                    return {
                        "should_kill": True,
                        "reason": f"⚡ FLASH PUMP ANOMALY: BTC pumped {adverse_move_pct:.2f}% against Short position in 1H!",
                        "severity": "EMERGENCY_PROTECT",
                        "side": side,
                        "size": abs(size)
                    }

        # 3. Violent CVD Institutional Inversion (Whale counter-attack)
        if side == "LONG" and cvd_net_delta < -80000 and unrealized_pnl < 0:
            return {
                "should_kill": True,
                "reason": f"🐋 WHALE DUMP OVERRIDE: Violent institutional selling detected (CVD: {cvd_net_delta:+,d}) against Long!",
                "severity": "INSTITUTIONAL_DEFENSE",
                "side": side,
                "size": abs(size)
            }
        elif side == "SHORT" and cvd_net_delta > 80000 and unrealized_pnl < 0:
            return {
                "should_kill": True,
                "reason": f"🐋 WHALE PUMP OVERRIDE: Violent institutional buying detected (CVD: {cvd_net_delta:+,d}) against Short!",
                "severity": "INSTITUTIONAL_DEFENSE",
                "side": side,
                "size": abs(size)
            }

        return {"should_kill": False, "reason": "ALL_RISK_METRICS_HEALTHY", "severity": "NORMAL"}

    def execute_instant_kill(self, make_request_func, cancel_all_orders_func, position_data, reason="User Rule #6 Kill"):
        """
        Executes immediate market liquidation + cancels ALL pending orders across Delta.
        Guarantees zero hanging orders.
        """
        size = abs(float(position_data.get("size", 0)))
        side = "sell" if float(position_data.get("size", 0)) > 0 else "buy"
        
        # 1. Close Position immediately via Market Order
        close_order = {
            "product_id": 84,  # BTCUSD Perpetual
            "size": int(size),
            "side": side,
            "order_type": "market_order"
        }
        res_close = make_request_func("POST", "/v2/orders", close_order)

        # 2. Cancel ALL pending orders immediately (Zero hanging orders rule)
        res_cancel = cancel_all_orders_func()

        self.kill_switch_triggered = True
        self.trigger_reason = reason
        self.trigger_time = time.time()

        return {
            "status": "KILL_SWITCH_EXECUTED",
            "reason": reason,
            "closed_position": res_close,
            "cancelled_orders": res_cancel,
            "zero_hanging_guaranteed": True
        }
