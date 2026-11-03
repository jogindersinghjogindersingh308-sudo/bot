"""
AlgoAlpha Smart Money Breakout Channels Pure Python Engine
Directly translated from official Pine Script v6 'Smart Money Breakout Channels [AlgoAlpha]'
"""
import math
import numpy as np

class AlgoAlphaBreakoutChannels:
    def __init__(self, norm_length=100, box_length=14, strong=True):
        self.norm_length = norm_length
        self.box_length = box_length
        self.strong = strong

    def analyze(self, candles):
        """
        candles: list of dicts with 'o', 'h', 'l', 'c', 'v', 't'
        """
        n = len(candles)
        if n < self.norm_length + self.box_length + 10:
            return {"error": "Not enough candle data"}

        opens = [c['o'] for c in candles]
        highs = [c['h'] for c in candles]
        lows = [c['l'] for c in candles]
        closes = [c['c'] for c in candles]
        volumes = [c.get('v', 0.0) for c in candles]

        # 1. Price Normalization
        # lowestLow = ta.lowest(low, length_)
        # highestHigh = ta.highest(high, length_)
        # normalizedPrice = (close - lowestLow) / (highestHigh - lowestLow)
        norm_price = []
        for i in range(n):
            start_idx = max(0, i - self.norm_length + 1)
            ll = min(lows[start_idx : i + 1])
            hh = max(highs[start_idx : i + 1])
            denom = hh - ll if hh != ll else 1.0
            norm_price.append((closes[i] - ll) / denom)

        # 2. Volatility = ta.stdev(normalizedPrice, 14)
        vol = []
        for i in range(n):
            if i < 14:
                vol.append(0.0)
            else:
                window = norm_price[i - 13 : i + 1]
                vol.append(float(np.std(window)))

        # 3. upper = (highestbars(vol, length + 1) + length)/length
        # lowestbars/highestbars in Pine returns 0 for current, -k for k bars back.
        upper = []
        lower = []
        L = self.box_length
        for i in range(n):
            if i < L + 1:
                upper.append(0.5)
                lower.append(0.5)
            else:
                window = vol[i - L : i + 1]
                max_val = max(window)
                min_val = min(window)
                # offset from current bar (0 is current, -k is past)
                # window[-1] is index i (offset 0), window[0] is offset -L
                # Pine highestbars: - (L - idx_in_window)
                max_offset = -(len(window) - 1 - window.index(max_val))
                min_offset = -(len(window) - 1 - window.index(min_val))
                
                up_val = (max_offset + L) / float(L)
                low_val = (min_offset + L) / float(L)
                upper.append(up_val)
                lower.append(low_val)

        # 4. ATR for inner zones
        # ATR(14)
        tr = [highs[0] - lows[0]]
        for i in range(1, n):
            tr.append(max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])))
        
        atr = []
        atr_window = 14
        curr_atr = sum(tr[:atr_window]) / atr_window
        for i in range(n):
            if i < atr_window:
                atr.append(curr_atr)
            else:
                curr_atr = (curr_atr * (atr_window - 1) + tr[i]) / atr_window
                atr.append(curr_atr)

        # 5. Track Channels & Breakouts
        # crossover(lower, upper) starts a duration count
        # crossover(upper, lower) triggers channel formation if duration > 10
        active_boxes = []
        last_crossover_lu = 0
        
        bullish_breakouts = []
        bearish_breakouts = []

        for i in range(1, n):
            # ta.crossover(lower, upper): lower[i-1] <= upper[i-1] and lower[i] > upper[i]
            if lower[i-1] <= upper[i-1] and lower[i] > upper[i]:
                last_crossover_lu = i

            duration = max(i - last_crossover_lu, 1)

            # ta.crossover(upper, lower) and duration > 10
            if upper[i-1] <= lower[i-1] and upper[i] > lower[i] and duration > 10:
                h_chan = max(highs[i - duration : i + 1])
                l_chan = min(lows[i - duration : i + 1])
                vola = atr[i] / 2.0
                active_boxes.append({
                    "start_idx": i - duration,
                    "top": h_chan,
                    "bottom": l_chan,
                    "midline": (h_chan + l_chan) / 2.0,
                    "upper_zone": h_chan - vola,
                    "lower_zone": l_chan + vola,
                    "formed_idx": i
                })

            # Check Breakouts on active boxes
            check_price = (closes[i] + opens[i]) / 2.0 if self.strong else closes[i]
            
            # Iterate backwards to allow removal
            retained = []
            for box in active_boxes:
                if check_price > box["top"]:
                    bullish_breakouts.append({
                        "bar_idx": i,
                        "price": closes[i],
                        "channel_top": box["top"],
                        "channel_bottom": box["bottom"],
                        "type": "BULLISH_BREAKOUT"
                    })
                elif check_price < box["bottom"]:
                    bearish_breakouts.append({
                        "bar_idx": i,
                        "price": closes[i],
                        "channel_top": box["top"],
                        "channel_bottom": box["bottom"],
                        "type": "BEARISH_BREAKOUT"
                    })
                else:
                    retained.append(box)
            active_boxes = retained

        # Current state
        latest_box = active_boxes[-1] if active_boxes else None
        curr_price = closes[-1]
        
        status = "IN_CHANNEL" if latest_box else "NO_ACTIVE_CHANNEL"
        channel_info = None
        if latest_box:
            channel_info = {
                "top": round(latest_box["top"], 2),
                "bottom": round(latest_box["bottom"], 2),
                "midline": round(latest_box["midline"], 2),
                "distance_to_top": round(latest_box["top"] - curr_price, 2),
                "distance_to_bottom": round(curr_price - latest_box["bottom"], 2)
            }

        return {
            "current_price": curr_price,
            "status": status,
            "active_channel": channel_info,
            "total_active_channels": len(active_boxes),
            "recent_bullish_breakouts": bullish_breakouts[-3:],
            "recent_bearish_breakouts": bearish_breakouts[-3:]
        }
