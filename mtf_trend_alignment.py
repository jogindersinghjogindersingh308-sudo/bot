"""
Engine #18: MTF Market Structure Protected-Level Trend Alignment (Pine Script Exact Port)
Calculates Protected Highs/Lows and Key Structure Breaks:
- Computes calcMSTrend() for each timeframe:
  * BullKey = protected low (raised on every new swing high in uptrend)
  * BearKey = protected high (lowered on every new swing low in downtrend)
- Calculates Alignment Score across Daily, 4H, 1H, 15m (Score range from -4 to +4 or -6 to +6)
- Identifies Full Bull Alignment (+4 / +6) or Full Bear Alignment (-4 / -6)
"""

class MTFTrendAlignmentEngine:
    def __init__(self, ms_length=5):
        self.ms_length = ms_length

    def _calc_ms_trend(self, candles):
        if len(candles) < (self.ms_length * 2 + 5):
            return 0, 0.0, 0.0

        n = len(candles)
        last_sh = None
        last_sl = None
        bull_key = None
        bear_key = None
        trend = 0

        for i in range(self.ms_length, n - self.ms_length):
            high_val = candles[i]['h']
            low_val = candles[i]['l']
            close_val = candles[i]['c']

            is_ph = all(high_val >= candles[j]['h'] for j in range(i - self.ms_length, i + self.ms_length + 1) if j != i)
            is_pl = all(low_val <= candles[j]['l'] for j in range(i - self.ms_length, i + self.ms_length + 1) if j != i)

            if is_ph:
                last_sh = high_val
                if trend == 1 and last_sl is not None:
                    bull_key = last_sl
            if is_pl:
                last_sl = low_val
                if trend == -1 and last_sh is not None:
                    bear_key = last_sh

            # Trend transition logic
            if trend == 0:
                if last_sh and close_val > last_sh:
                    trend = 1
                    bull_key = last_sl
                elif last_sl and close_val < last_sl:
                    trend = -1
                    bear_key = last_sh
            elif trend == 1:
                if bull_key and close_val < bull_key:
                    trend = -1
                    bear_key = last_sh
            elif trend == -1:
                if bear_key and close_val > bear_key:
                    trend = 1
                    bull_key = last_sl

        # Evaluate last close against final protected keys
        last_c = candles[-1]['c']
        if trend == 1 and bull_key and last_c < bull_key:
            trend = -1
        elif trend == -1 and bear_key and last_c > bear_key:
            trend = 1

        return trend, (bull_key or 0.0), (bear_key or 0.0)

    def analyze(self, candles_daily, candles_4h, candles_1h, candles_15m):
        t_d, _, _ = self._calc_ms_trend(candles_daily)
        t_4h, _, _ = self._calc_ms_trend(candles_4h)
        t_1h, bk_1h, sk_1h = self._calc_ms_trend(candles_1h)
        t_15m, _, _ = self._calc_ms_trend(candles_15m)

        score = t_d + t_4h + t_1h + t_15m
        max_score = 4

        t_text = {1: "🟢 BULL", -1: "🔴 BEAR", 0: "⚪ CHOP"}

        if score == max_score:
            status = "✅ FULL 4-TIMEFRAME BULLISH ALIGNMENT (+4/4)"
        elif score == -max_score:
            status = "✅ FULL 4-TIMEFRAME BEARISH ALIGNMENT (-4/4)"
        elif score >= 2:
            status = f"BULLISH CONFLUENCE (+{score}/4)"
        elif score <= -2:
            status = f"BEARISH CONFLUENCE ({score}/4)"
        else:
            status = f"⚠️ MIXED MARKET STRUCTURE ({score}/4)"

        return {
            "alignment_score": score,
            "max_score": max_score,
            "status_text": status,
            "daily": t_text.get(t_d, "⚪"),
            "h4": t_text.get(t_4h, "⚪"),
            "h1": t_text.get(t_1h, "⚪"),
            "m15": t_text.get(t_15m, "⚪"),
            "protected_bull_key": bk_1h,
            "protected_bear_key": sk_1h
        }
