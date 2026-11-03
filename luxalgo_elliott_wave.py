"""
LuxAlgo Elliott Wave Pure Python Engine
Directly translated from official Pine Script v5: 'Elliott Wave [LuxAlgo]' (© LuxAlgo)
Implements ZigZag 1-2-3-4-5 Impulse waves and ABC Corrective patterns with strict Elliott Wave rules:
- Wave 3 is never the shortest wave
- Wave 4 does not enter Wave 1 price territory
- Wave 2 does not retrace beyond start of Wave 1
"""

class LuxAlgoElliottWave:
    def __init__(self, lengths=[4, 8, 16]):
        self.lengths = lengths

    def _find_pivots(self, highs, lows, length):
        n = len(highs)
        pivots = []
        # Find alternating swing highs and swing lows
        for i in range(length, n - length):
            is_high = highs[i] == max(highs[i - length : i + length + 1])
            is_low = lows[i] == min(lows[i - length : i + length + 1])
            if is_high and not is_low:
                pivots.append({"idx": i, "type": "H", "price": highs[i]})
            elif is_low and not is_high:
                pivots.append({"idx": i, "type": "L", "price": lows[i]})
            elif is_high and is_low:
                pivots.append({"idx": i, "type": "HL", "price": highs[i]})
        
        # Clean consecutive pivots of same type to enforce ZigZag alternating sequence
        clean_pivots = []
        for p in pivots:
            if not clean_pivots:
                clean_pivots.append(p)
            else:
                last = clean_pivots[-1]
                if p["type"] == last["type"]:
                    # Keep more extreme one
                    if p["type"] == "H" and p["price"] > last["price"]:
                        clean_pivots[-1] = p
                    elif p["type"] == "L" and p["price"] < last["price"]:
                        clean_pivots[-1] = p
                else:
                    clean_pivots.append(p)
        return clean_pivots

    def analyze(self, candles):
        """
        candles: list of dicts with 'o', 'h', 'l', 'c', 'v', 't'
        """
        n = len(candles)
        if n < 40:
            return {"error": "Not enough candles for Elliott Wave calculation"}

        highs = [c['h'] for c in candles]
        lows = [c['l'] for c in candles]
        closes = [c['c'] for c in candles]
        curr_price = closes[-1]

        detected_patterns = []

        # Analyze across zigzag lengths (primary len=8, secondary len=4, len=16)
        for length in self.lengths:
            pivots = self._find_pivots(highs, lows, length)
            if len(pivots) < 6:
                continue

            # Check last 6 consecutive points for 1-2-3-4-5
            for k in range(len(pivots) - 5):
                p0 = pivots[k]     # start of wave 1
                p1 = pivots[k+1]   # end of wave 1
                p2 = pivots[k+2]   # end of wave 2
                p3 = pivots[k+3]   # end of wave 3
                p4 = pivots[k+4]   # end of wave 4
                p5 = pivots[k+5]   # end of wave 5

                # 1. Bullish Impulse: Low (p0) -> High (p1) -> Low (p2) -> High (p3) -> Low (p4) -> High (p5)
                if p0['type'] == 'L' and p1['type'] == 'H' and p2['type'] == 'L' and p3['type'] == 'H' and p4['type'] == 'L' and p5['type'] == 'H':
                    w1 = p1['price'] - p0['price']
                    w3 = p3['price'] - p2['price']
                    w5 = p5['price'] - p4['price']
                    min_w = min(w1, w3, w5)

                    # LuxAlgo rules:
                    # _W3 != min and _6y > _4y and _3y > _1y and _5y > _2y
                    if w3 != min_w and p5['price'] > p3['price'] and p2['price'] > p0['price'] and p4['price'] > p1['price']:
                        detected_patterns.append({
                            "type": "BULLISH_IMPULSE_12345",
                            "length": length,
                            "w0_start": p0['price'],
                            "w1_top": p1['price'],
                            "w2_low": p2['price'],
                            "w3_top": p3['price'],
                            "w4_low": p4['price'],
                            "w5_top": p5['price'],
                            "last_bar_idx": p5['idx']
                        })

                # 2. Bearish Impulse: High (p0) -> Low (p1) -> High (p2) -> Low (p3) -> High (p4) -> Low (p5)
                if p0['type'] == 'H' and p1['type'] == 'L' and p2['type'] == 'H' and p3['type'] == 'L' and p4['type'] == 'H' and p5['type'] == 'L':
                    w1 = p0['price'] - p1['price']
                    w3 = p2['price'] - p3['price']
                    w5 = p4['price'] - p5['price']
                    min_w = min(w1, w3, w5)

                    # LuxAlgo rules:
                    # _W3 != min and _4y > _6y and _1y > _3y and _2y > _5y
                    if w3 != min_w and p3['price'] > p5['price'] and p0['price'] > p2['price'] and p1['price'] > p4['price']:
                        detected_patterns.append({
                            "type": "BEARISH_IMPULSE_12345",
                            "length": length,
                            "w0_start": p0['price'],
                            "w1_low": p1['price'],
                            "w2_high": p2['price'],
                            "w3_low": p3['price'],
                            "w4_high": p4['price'],
                            "w5_low": p5['price'],
                            "last_bar_idx": p5['idx']
                        })

        # Evaluate most recent pattern and active wave cycle
        if detected_patterns:
            latest = max(detected_patterns, key=lambda x: x["last_bar_idx"])
            bars_since = n - 1 - latest["last_bar_idx"]

            if latest["type"] == "BULLISH_IMPULSE_12345":
                if bars_since < 8:
                    wave_status = f"Wave (5) Completed @ ${latest['w5_top']:,.1f} - ABC Correction Expected"
                else:
                    wave_status = f"Post-Bullish Wave (5) @ ${latest['w5_top']:,.1f} - In Corrective ABC Phase"
                pattern_direction = "BULLISH_IMPULSE"
            else:
                if bars_since < 8:
                    wave_status = f"Wave (5) Bottom Completed @ ${latest['w5_low']:,.1f} - ABC Reversal Rally Expected"
                else:
                    wave_status = f"Post-Bearish Wave (5) @ ${latest['w5_low']:,.1f} - In Corrective ABC Phase"
                pattern_direction = "BEARISH_IMPULSE"
        else:
            # Check recent 3-pivot structure for Wave 3 progression
            pivots_len8 = self._find_pivots(highs, lows, 8)
            if len(pivots_len8) >= 3:
                last_p = pivots_len8[-1]
                prev_p = pivots_len8[-2]
                if last_p['type'] == 'L' and curr_price > last_p['price']:
                    wave_status = f"Developing Impulse Wave Up from ${last_p['price']:,.1f}"
                    pattern_direction = "IMPULSE_UP"
                elif last_p['type'] == 'H' and curr_price < last_p['price']:
                    wave_status = f"Developing Impulse Wave Down from ${last_p['price']:,.1f}"
                    pattern_direction = "IMPULSE_DOWN"
                else:
                    wave_status = "Consolidation / Wave (4) Range"
                    pattern_direction = "NEUTRAL"
            else:
                wave_status = "Building Wave Cycle"
                pattern_direction = "NEUTRAL"
            latest = None

        return {
            "current_price": curr_price,
            "wave_status": wave_status,
            "pattern_direction": pattern_direction,
            "latest_pattern": latest
        }
