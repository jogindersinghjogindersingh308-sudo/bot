"""
LuxAlgo Volume Profile Pure Python Engine
Directly translated from official Pine Script: 'Volume Profile [LUX]' (© LuxAlgo)
Calculates exact Point of Control (POC), Value Area High (VAH), and Value Area Low (VAL).
"""
import numpy as np

class LuxAlgoVolumeProfile:
    def __init__(self, lookback=200, row_size=100, va_percent=0.70):
        self.lookback = lookback
        self.row_size = row_size
        self.va_percent = va_percent

    def analyze(self, candles):
        """
        candles: list of dicts with 'o', 'h', 'l', 'c', 'v', 't'
        """
        n = len(candles)
        if n < 20:
            return {"error": "Not enough candle data for Volume Profile"}

        use_len = min(self.lookback, n)
        subset = candles[-use_len:]

        highs = [c['h'] for c in subset]
        lows = [c['l'] for c in subset]
        volumes = [c.get('v', 1.0) for c in subset]
        closes = [c['c'] for c in subset]

        highest = max(highs)
        lowest = min(lows)
        curr_price = closes[-1]

        if highest == lowest:
            return {
                "current_price": curr_price,
                "poc": curr_price,
                "vah": curr_price,
                "val": curr_price
            }

        # Divide into price rows
        row = self.row_size
        price_step = (highest - lowest) / float(row)
        levels = [lowest + i * price_step for i in range(row + 1)]
        sumv = [0.0] * row

        # Distribute volume across price levels
        for k in range(use_len):
            h_k = highs[k]
            l_k = lows[k]
            v_k = volumes[k]
            if h_k <= l_k:
                continue

            for j in range(row):
                lvl_bot = levels[j]
                lvl_top = levels[j+1]
                # Check overlap between candle [l_k, h_k] and row [lvl_bot, lvl_top]
                if h_k > lvl_bot and l_k < lvl_top:
                    # Weight by intersection proportion
                    overlap = min(h_k, lvl_top) - max(l_k, lvl_bot)
                    proportion = overlap / (h_k - l_k)
                    sumv[j] += v_k * proportion

        # Point of Control (POC)
        max_idx = int(np.argmax(sumv))
        poc = (levels[max_idx] + levels[max_idx + 1]) / 2.0
        max_volume = sumv[max_idx]

        # Value Area (70% Volume around POC)
        total_vol = sum(sumv)
        target_vol = total_vol * self.va_percent

        accum_vol = sumv[max_idx]
        up_idx = max_idx
        dn_idx = max_idx

        while accum_vol < target_vol and (up_idx < row - 1 or dn_idx > 0):
            next_up = sumv[up_idx + 1] if up_idx < row - 1 else 0.0
            next_dn = sumv[dn_idx - 1] if dn_idx > 0 else 0.0

            if next_up >= next_dn and up_idx < row - 1:
                up_idx += 1
                accum_vol += sumv[up_idx]
            elif dn_idx > 0:
                dn_idx -= 1
                accum_vol += sumv[dn_idx]
            elif up_idx < row - 1:
                up_idx += 1
                accum_vol += sumv[up_idx]
            else:
                break

        vah = levels[up_idx + 1]
        val = levels[dn_idx]

        # Determine price location relative to Volume Profile
        if curr_price > vah:
            location = "ABOVE VALUE AREA (Bullish Imbalance)"
        elif curr_price < val:
            location = "BELOW VALUE AREA (Bearish Imbalance)"
        elif curr_price > poc:
            location = "INSIDE VALUE AREA (Upper Half, Testing POC)"
        else:
            location = "INSIDE VALUE AREA (Lower Half, Testing POC)"

        return {
            "current_price": curr_price,
            "poc": round(poc, 2),
            "vah": round(vah, 2),
            "val": round(val, 2),
            "profile_highest": round(highest, 2),
            "profile_lowest": round(lowest, 2),
            "distance_to_poc": round(curr_price - poc, 2),
            "location": location,
            "total_profile_volume": round(total_vol, 2)
        }
