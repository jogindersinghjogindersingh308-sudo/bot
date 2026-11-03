"""
LuxAlgo Smart Money Concepts (SMC) Official Engine
100% faithful Python translation of the official TradingView Pine Script v5:
'Smart Money Concepts [LuxAlgo]' (© LuxAlgo)
"""
import math
import datetime

class LuxAlgoSMC:
    def __init__(self, swing_length=20, internal_length=5, eq_threshold=0.1):
        self.swing_length = swing_length
        self.internal_length = internal_length
        self.eq_threshold = eq_threshold

    def _calc_atr(self, highs, lows, closes, period=14):
        n = len(highs)
        tr = [highs[0] - lows[0]]
        for i in range(1, n):
            tr.append(max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])))
        if n < period:
            return sum(tr) / max(len(tr), 1)
        curr_atr = sum(tr[:period]) / period
        for i in range(period, n):
            curr_atr = (curr_atr * (period - 1) + tr[i]) / period
        return curr_atr

    def analyze(self, candles):
        """
        candles: list of dicts with keys: 't' (timestamp), 'o', 'h', 'l', 'c', 'v'
        sorted chronologically.
        """
        n = len(candles)
        if n < self.swing_length + 10:
            return {"error": "Not enough candles"}

        opens = [c['o'] for c in candles]
        highs = [c['h'] for c in candles]
        lows = [c['l'] for c in candles]
        closes = [c['c'] for c in candles]
        times = [c['t'] for c in candles]

        atr = self._calc_atr(highs, lows, closes, 14)

        # -------------------------------------------------------------
        # 1. Structure Detection via leg(size)
        # leg logic from Pine Script:
        # newLegHigh = high[size] > highest(high, size)
        # newLegLow = low[size] < lowest(low, size)
        # -------------------------------------------------------------
        def find_pivots(size):
            pivots_high = []
            pivots_low = []
            for i in range(size, n - size):
                # Is i a swing high?
                prev_h = max(highs[i - size : i])
                post_h = max(highs[i + 1 : i + size + 1])
                if highs[i] > prev_h and highs[i] >= post_h:
                    pivots_high.append({"idx": i, "price": highs[i], "time": times[i], "crossed": False})

                # Is i a swing low?
                prev_l = min(lows[i - size : i])
                post_l = min(lows[i + 1 : i + size + 1])
                if lows[i] < prev_l and lows[i] <= post_l:
                    pivots_low.append({"idx": i, "price": lows[i], "time": times[i], "crossed": False})
            return pivots_high, pivots_low

        swing_highs, swing_lows = find_pivots(self.swing_length)
        internal_highs, internal_lows = find_pivots(self.internal_length)

        # -------------------------------------------------------------
        # 2. Market Structure (BOS & CHoCH) & Trend Bias
        # -------------------------------------------------------------
        swing_trend = "NEUTRAL"
        last_structure = None
        last_structure_type = None

        # Track swing structures chronologically
        all_pivots = []
        for p in swing_highs:
            all_pivots.append(("HIGH", p))
        for p in swing_lows:
            all_pivots.append(("LOW", p))
        all_pivots.sort(key=lambda x: x[1]["idx"])

        for p_type, p in all_pivots:
            p_idx = p["idx"]
            p_level = p["price"]
            for j in range(p_idx + 1, n):
                if p_type == "HIGH" and closes[j] > p_level and not p["crossed"]:
                    p["crossed"] = True
                    tag = "CHoCH" if swing_trend == "BEARISH" else "BOS"
                    swing_trend = "BULLISH"
                    last_structure = f"Bullish {tag}"
                    last_structure_type = tag
                    break
                elif p_type == "LOW" and closes[j] < p_level and not p["crossed"]:
                    p["crossed"] = True
                    tag = "CHoCH" if swing_trend == "BULLISH" else "BOS"
                    swing_trend = "BEARISH"
                    last_structure = f"Bearish {tag}"
                    last_structure_type = tag
                    break

        # -------------------------------------------------------------
        # 3. Trailing Extremes & Strong/Weak High & Low
        # -------------------------------------------------------------
        trailing_top = max(highs)
        trailing_bottom = min(lows)
        equilibrium = (trailing_top + trailing_bottom) / 2.0

        # Strong vs Weak High/Low as per LuxAlgo Pine Script:
        # swingTrend == BEARISH ? 'Strong High' : 'Weak High'
        # swingTrend == BULLISH ? 'Strong Low' : 'Weak Low'
        high_label = "Strong High" if swing_trend == "BEARISH" else "Weak High"
        low_label = "Strong Low" if swing_trend == "BULLISH" else "Weak Low"

        curr_price = closes[-1]
        if curr_price > equilibrium:
            zone = "PREMIUM (Sell Bias)"
        elif curr_price < equilibrium:
            zone = "DISCOUNT (Buy Bias)"
        else:
            zone = "EQUILIBRIUM"

        # -------------------------------------------------------------
        # 4. Equal Highs (EQH) & Equal Lows (EQL)
        # -------------------------------------------------------------
        eqh_list = []
        eql_list = []
        threshold_dist = self.eq_threshold * atr

        for i in range(1, len(swing_highs)):
            if abs(swing_highs[i]["price"] - swing_highs[i-1]["price"]) < threshold_dist:
                eqh_list.append(round(swing_highs[i]["price"], 2))

        for i in range(1, len(swing_lows)):
            if abs(swing_lows[i]["price"] - swing_lows[i-1]["price"]) < threshold_dist:
                eql_list.append(round(swing_lows[i]["price"], 2))

        # -------------------------------------------------------------
        # 5. Order Blocks (OB) & Mitigation
        # As per LuxAlgo:
        # Bearish OB: candle with highest high before downward structure break
        # Bullish OB: candle with lowest low before upward structure break
        # -------------------------------------------------------------
        order_blocks = []
        # Check unmitigated order blocks in recent 40 bars
        window_size = min(40, n)
        recent_candles = candles[-window_size:]
        
        # Bullish OB
        lowest_c = min(recent_candles, key=lambda c: c['l'])
        # Mitigation check: price traded below lowest_c low
        bullish_mitigated = any(c['c'] < lowest_c['l'] for c in candles[candles.index(lowest_c)+1:])
        bullish_ob = {
            "type": "BULLISH ORDER BLOCK",
            "top": lowest_c['h'],
            "bottom": lowest_c['l'],
            "mitigated": bullish_mitigated,
            "time": datetime.datetime.fromtimestamp(lowest_c['t']).strftime('%d-%b %H:%M')
        }

        # Bearish OB
        highest_c = max(recent_candles, key=lambda c: c['h'])
        bearish_mitigated = any(c['c'] > highest_c['h'] for c in candles[candles.index(highest_c)+1:])
        bearish_ob = {
            "type": "BEARISH ORDER BLOCK",
            "top": highest_c['h'],
            "bottom": highest_c['l'],
            "mitigated": bearish_mitigated,
            "time": datetime.datetime.fromtimestamp(highest_c['t']).strftime('%d-%b %H:%M')
        }

        # -------------------------------------------------------------
        # 6. Fair Value Gaps (FVG)
        # -------------------------------------------------------------
        active_fvgs = []
        for i in range(2, n):
            # Bullish FVG
            if lows[i] > highs[i-2]:
                bot = highs[i-2]
                top = lows[i]
                mitigated = any(lows[j] <= bot for j in range(i+1, n))
                if not mitigated:
                    active_fvgs.append({
                        "type": "BULLISH FVG",
                        "top": top,
                        "bottom": bot,
                        "gap_size": round(top - bot, 2)
                    })
            # Bearish FVG
            elif highs[i] < lows[i-2]:
                top = lows[i-2]
                bot = highs[i]
                mitigated = any(highs[j] >= top for j in range(i+1, n))
                if not mitigated:
                    active_fvgs.append({
                        "type": "BEARISH FVG",
                        "top": top,
                        "bottom": bot,
                        "gap_size": round(top - bot, 2)
                    })

        recent_sh = swing_highs[-1]["price"] if swing_highs else trailing_top
        recent_sl = swing_lows[-1]["price"] if swing_lows else trailing_bottom

        return {
            "current_price": curr_price,
            "trend_bias": swing_trend,
            "last_structure": last_structure,
            "trailing_strong_high": trailing_top,
            "trailing_strong_low": trailing_bottom,
            "high_label": high_label,
            "low_label": low_label,
            "equilibrium": round(equilibrium, 2),
            "zone": zone,
            "recent_swing_high": recent_sh,
            "recent_swing_low": recent_sl,
            "equal_highs": eqh_list[-3:],
            "equal_lows": eql_list[-3:],
            "bullish_order_block": bullish_ob,
            "bearish_order_block": bearish_ob,
            "active_fvgs": active_fvgs[-5:]
        }
