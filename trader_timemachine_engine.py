"""
TimeMachine Historical Replay & Strategy Backtester Engine
Ported & Adapted from Jakeschincariol/day-trader-skill /trader-timemachine.
Simulates 1-Hour (1H) trend trading on historical BTC data based on User Master Rules:
- 1-Hour Timeframe focus (Rule #4)
- 2x-3x Leverage Trend Following (Diwali Rule #1)
- Strict Momentum / Trailing Exits with Zero Hanging Orders (Rule #6)
"""
import urllib.request
import json
import datetime
import time

class TraderTimeMachineEngine:
    def __init__(self, initial_capital=1000.0, leverage=2.5):
        self.initial_capital = initial_capital
        self.leverage = leverage

    def fetch_historical_1h_candles(self, limit=120):
        """
        Fetches authentic historical 1-Hour candles for BTCUSD from public feeds.
        """
        # Try Delta Exchange first
        try:
            now = int(time.time())
            start = now - (limit * 3600)
            url = f"https://cdn-ind.testnet.deltaex.org/v2/chart/history?symbol=BTCUSD&resolution=60&from={start}&to={now}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=6) as response:
                data = json.loads(response.read().decode())
                if data.get("result") and data["result"].get("c"):
                    res = data["result"]
                    candles = []
                    for i in range(len(res["c"])):
                        candles.append({
                            "t": res["t"][i],
                            "o": float(res["o"][i]),
                            "h": float(res["h"][i]),
                            "l": float(res["l"][i]),
                            "c": float(res["c"][i]),
                            "v": float(res["v"][i])
                        })
                    if len(candles) >= 20:
                        return candles
        except Exception as e:
            pass

        # Public Binance fallback for robust historical replay
        try:
            url = f"https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit={limit}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=6) as response:
                raw = json.loads(response.read().decode())
                candles = []
                for k in raw:
                    candles.append({
                        "t": int(k[0]) // 1000,
                        "o": float(k[1]),
                        "h": float(k[2]),
                        "l": float(k[3]),
                        "c": float(k[4]),
                        "v": float(k[5])
                    })
                return candles
        except Exception as e:
            pass

        return []

    def run_replay_simulation(self, candles):
        """
        Runs candle-by-candle step simulation over historical data.
        """
        if len(candles) < 30:
            return {"error": "Not enough historical candle data for simulation."}

        balance = self.initial_capital
        peak_balance = balance
        max_drawdown_pct = 0.0

        position = None  # {"side": "LONG"|"SHORT", "entry": price, "size": contracts, "peak_pnl": 0}
        trades = []

        # Technical indicators tracking (20-period Donchian Channels + EMA)
        for i in range(25, len(candles)):
            curr = candles[i]
            prev = candles[i-1]
            past_window = candles[i-20:i]

            upper_band = max(c["h"] for c in past_window)
            lower_band = min(c["l"] for c in past_window)
            avg_vol = sum(c["v"] for c in past_window) / len(past_window)

            curr_price = curr["c"]

            # Manage open position
            if position:
                side = position["side"]
                entry = position["entry"]
                
                if side == "LONG":
                    pnl_pct = ((curr_price - entry) / entry) * 100 * self.leverage
                    pnl_usd = (balance * (pnl_pct / 100.0))
                else:
                    pnl_pct = ((entry - curr_price) / entry) * 100 * self.leverage
                    pnl_usd = (balance * (pnl_pct / 100.0))

                # Update peak PnL
                if pnl_usd > position["peak_pnl"]:
                    position["peak_pnl"] = pnl_usd

                # Exit Strategy (Rule #6 - Ride profit, exit when momentum exhausts)
                exit_signal = False
                exit_reason = ""

                # Stop loss protect (-2.0% on capital)
                if pnl_pct <= -2.5:
                    exit_signal = True
                    exit_reason = "Hard Discipline Stop (-2.5%)"

                # High Watermark trailing lock (Locking profit when game turns)
                elif position["peak_pnl"] > 35.0 and pnl_usd < position["peak_pnl"] * 0.70:
                    exit_signal = True
                    exit_reason = "Momentum Fade / Trailing Profit Lock ('ਕਮ ਪੈਸੇ ਤੁਰੇ ਜਾਂਦੇ ਆ')"

                # Breakdown / Reversal
                elif side == "LONG" and curr_price < lower_band:
                    exit_signal = True
                    exit_reason = "Market Structure Bearish Reversal"
                elif side == "SHORT" and curr_price > upper_band:
                    exit_signal = True
                    exit_reason = "Market Structure Bullish Reversal"

                # Target reached (+6% to +10% High R:R trend move)
                elif pnl_pct >= 8.0:
                    exit_signal = True
                    exit_reason = "Big Trend Target Reached (1:3+ R:R)"

                if exit_signal:
                    balance += pnl_usd
                    if balance > peak_balance:
                        peak_balance = balance
                    dd = ((peak_balance - balance) / peak_balance) * 100
                    if dd > max_drawdown_pct:
                        max_drawdown_pct = dd

                    trades.append({
                        "trade_no": len(trades) + 1,
                        "side": side,
                        "entry_price": entry,
                        "exit_price": curr_price,
                        "pnl_usd": round(pnl_usd, 2),
                        "pnl_pct": round(pnl_pct, 2),
                        "exit_reason": exit_reason,
                        "exit_time": datetime.datetime.fromtimestamp(curr["t"]).strftime("%Y-%m-%d %H:%M")
                    })
                    position = None

            # Look for New High-Confluence Entry (When no position)
            else:
                # Bullish Breakout with Volume Confirmation (300+ contracts / high relative vol)
                if curr_price > upper_band and curr["v"] > avg_vol * 1.1:
                    position = {
                        "side": "LONG",
                        "entry": curr_price,
                        "peak_pnl": 0.0,
                        "entry_time": datetime.datetime.fromtimestamp(curr["t"]).strftime("%Y-%m-%d %H:%M")
                    }
                # Bearish Breakdown with Volume Confirmation
                elif curr_price < lower_band and curr["v"] > avg_vol * 1.1:
                    position = {
                        "side": "SHORT",
                        "entry": curr_price,
                        "peak_pnl": 0.0,
                        "entry_time": datetime.datetime.fromtimestamp(curr["t"]).strftime("%Y-%m-%d %H:%M")
                    }

        # Calculate performance statistics
        total_trades = len(trades)
        wins = [t for t in trades if t["pnl_usd"] > 0]
        losses = [t for t in trades if t["pnl_usd"] <= 0]
        win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0
        total_profit = sum(t["pnl_usd"] for t in wins)
        total_loss = abs(sum(t["pnl_usd"] for t in losses))
        profit_factor = round(total_profit / total_loss, 2) if total_loss > 0 else 999.0
        total_return_pct = round(((balance - self.initial_capital) / self.initial_capital) * 100, 2)

        return {
            "initial_capital": self.initial_capital,
            "final_balance": round(balance, 2),
            "total_return_pct": total_return_pct,
            "total_trades": total_trades,
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate_pct": round(win_rate, 1),
            "profit_factor": profit_factor,
            "max_drawdown_pct": round(max_drawdown_pct, 2),
            "leverage_used": f"{self.leverage}x",
            "recent_trades": trades[-5:] if trades else []
        }

if __name__ == "__main__":
    tm = TraderTimeMachineEngine(initial_capital=1000.0, leverage=2.5)
    candles = tm.fetch_historical_1h_candles(limit=150)
    print(f"Fetched {len(candles)} historical 1H candles.")
    res = tm.run_replay_simulation(candles)
    print("\n--- TIME MACHINE REPLAY RESULTS ---")
    print(json.dumps(res, indent=2))
