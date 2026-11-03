"""
Liquidity Sweeps & Hunter Pure Python Engine
Directly translated from official Pine Scripts:
- 'Liquidity Sweeps [LuxAlgo]' (© LuxAlgo)
- 'Liquidity Sweep Hunter Algo [AlgoAlpha]' (© AlgoAlpha)
Detects Buy-Side Liquidity (BSL), Sell-Side Liquidity (SSL), and Wick Sweeps (Stop Hunts).
"""

class LiquiditySweepsEngine:
    def __init__(self, swing_len=5, fast_bars=14, mid_bars=42, slow_bars=120):
        self.swing_len = swing_len
        self.fast_bars = fast_bars
        self.mid_bars = mid_bars
        self.slow_bars = slow_bars

    def analyze(self, candles):
        """
        candles: list of dicts with 'o', 'h', 'l', 'c', 'v', 't'
        """
        n = len(candles)
        if n < 40:
            return {"error": "Not enough candles for Liquidity Sweeps"}

        highs = [c['h'] for c in candles]
        lows = [c['l'] for c in candles]
        closes = [c['c'] for c in candles]
        opens = [c['o'] for c in candles]
        curr_price = closes[-1]

        # 1. LuxAlgo Wick Sweeps Detection
        # ph/pl with swing_len
        piv_highs = []
        piv_lows = []
        L = self.swing_len
        for i in range(L, n - L):
            if highs[i] == max(highs[i - L : i + L + 1]):
                piv_highs.append({"idx": i, "price": highs[i], "swept": False, "mitigated": False})
            if lows[i] == min(lows[i - L : i + L + 1]):
                piv_lows.append({"idx": i, "price": lows[i], "swept": False, "mitigated": False})

        bearish_sweeps = [] # High swept by wick, closed below
        bullish_sweeps = [] # Low swept by wick, closed above

        # Check for wick sweeps on recent bars
        for ph in piv_highs[-10:]:
            lvl = ph["price"]
            for j in range(ph["idx"] + 1, n):
                if closes[j] > lvl:
                    ph["mitigated"] = True
                    break
                elif highs[j] > lvl and closes[j] < lvl and not ph["swept"]:
                    ph["swept"] = True
                    bearish_sweeps.append({
                        "bar_idx": j,
                        "swept_level": lvl,
                        "wick_high": highs[j],
                        "type": "BEARISH_LIQUIDITY_SWEEP (Stop Hunt Above High)"
                    })

        for pl in piv_lows[-10:]:
            lvl = pl["price"]
            for j in range(pl["idx"] + 1, n):
                if closes[j] < lvl:
                    pl["mitigated"] = True
                    break
                elif lows[j] < lvl and closes[j] > lvl and not pl["swept"]:
                    pl["swept"] = True
                    bullish_sweeps.append({
                        "bar_idx": j,
                        "swept_level": lvl,
                        "wick_low": lows[j],
                        "type": "BULLISH_LIQUIDITY_SWEEP (Stop Hunt Below Low)"
                    })

        # 2. AlgoAlpha Multi-tier Liquidity Pools (Fast, Mid, Slow)
        h_fast = max(highs[-self.fast_bars:])
        h_mid = max(highs[-min(self.mid_bars, n):])
        h_slow = max(highs[-min(self.slow_bars, n):])

        l_fast = min(lows[-self.fast_bars:])
        l_mid = min(lows[-min(self.mid_bars, n):])
        l_slow = min(lows[-min(self.slow_bars, n):])

        # Active resting liquidity
        unmitigated_bsl = [ph["price"] for ph in piv_highs if not ph["mitigated"] and ph["price"] > curr_price]
        unmitigated_ssl = [pl["price"] for pl in piv_lows if not pl["mitigated"] and pl["price"] < curr_price]

        nearest_bsl = min(unmitigated_bsl) if unmitigated_bsl else h_fast
        nearest_ssl = max(unmitigated_ssl) if unmitigated_ssl else l_fast

        latest_sweep = None
        if bearish_sweeps and bullish_sweeps:
            latest_sweep = max(bearish_sweeps + bullish_sweeps, key=lambda x: x["bar_idx"])
        elif bearish_sweeps:
            latest_sweep = bearish_sweeps[-1]
        elif bullish_sweeps:
            latest_sweep = bullish_sweeps[-1]

        sweep_status = latest_sweep["type"] if latest_sweep and (n - 1 - latest_sweep["bar_idx"] < 5) else "No Recent Sweep (Resting Pools Active)"

        return {
            "current_price": curr_price,
            "sweep_status": sweep_status,
            "nearest_bsl_pool": round(nearest_bsl, 2), # Buy-side liquidity
            "nearest_ssl_pool": round(nearest_ssl, 2), # Sell-side liquidity
            "distance_to_bsl": round(nearest_bsl - curr_price, 2),
            "distance_to_ssl": round(curr_price - nearest_ssl, 2),
            "major_high_liquidity": round(h_slow, 2),
            "major_low_liquidity": round(l_slow, 2),
            "recent_bullish_sweeps": len(bullish_sweeps),
            "recent_bearish_sweeps": len(bearish_sweeps)
        }
