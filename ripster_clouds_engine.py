"""
Ripster EMA Clouds Engine (Official Pine Script Exact Port)
Implements:
- Multi-EMA Clouds on HL2:
  * Cloud 1: 8/9 EMA
  * Cloud 2: 5/12 EMA (Short Momentum Cloud)
  * Cloud 3: 34/50 EMA (Core Institutional Trend Cloud)
  * Cloud 4: 72/89 EMA
  * Cloud 5: 180/200 EMA (Macro Baseline)
- Cloud Bull/Bear Status & Pullback Cushion Validation
"""

class RipsterCloudsEngine:
    def __init__(self):
        self.clouds = [
            (8, 9, "Cloud 1 (8/9)"),
            (5, 12, "Cloud 2 (5/12)"),
            (34, 50, "Cloud 3 (34/50 Core)"),
            (72, 89, "Cloud 4 (72/89)"),
            (180, 200, "Cloud 5 (180/200 Macro)")
        ]

    def _calc_ema(self, series, period):
        if len(series) < period:
            return series[-1] if series else 0.0
        k = 2.0 / (period + 1.0)
        res = sum(series[:period]) / period
        for val in series[period:]:
            res = (val * k) + (res * (1.0 - k))
        return res

    def analyze(self, candles):
        if len(candles) < 210:
            # Fallback with smaller subset if count is smaller
            pass

        hl2_series = [(c['h'] + c['l']) / 2.0 for c in candles]
        curr_price = candles[-1]['c']

        cloud_results = {}
        for s_len, l_len, name in self.clouds:
            s_ema = self._calc_ema(hl2_series, s_len)
            l_ema = self._calc_ema(hl2_series, l_len)
            is_bull = s_ema >= l_ema
            cloud_results[name] = {
                "short_ema": round(s_ema, 1),
                "long_ema": round(l_ema, 1),
                "color": "GREEN" if is_bull else "RED"
            }

        # Focus on Core 34/50 Cloud & Short 5/12 Cloud
        c3_short = cloud_results["Cloud 3 (34/50 Core)"]["short_ema"]
        c3_long = cloud_results["Cloud 3 (34/50 Core)"]["long_ema"]
        c3_top = max(c3_short, c3_long)
        c3_bot = min(c3_short, c3_long)

        c2_short = cloud_results["Cloud 2 (5/12)"]["short_ema"]
        c2_long = cloud_results["Cloud 2 (5/12)"]["long_ema"]

        if curr_price > c3_top:
            trend_state = f"🟢 BULLISH ABOVE 34-50 CLOUD (${c3_bot:,.1f} - ${c3_top:,.1f})"
        elif curr_price < c3_bot:
            trend_state = f"🔴 BEARISH BELOW 34-50 CLOUD (${c3_bot:,.1f} - ${c3_top:,.1f})"
        else:
            trend_state = f"🟡 INSIDE 34-50 CLOUD CONSOLIDATION (${c3_bot:,.1f} - ${c3_top:,.1f})"

        cushion_bounce = False
        if abs(curr_price - c3_top) / curr_price < 0.003 and curr_price >= c3_top:
            cushion_bounce = True

        return {
            "trend_state": trend_state,
            "core_34_50_top": c3_top,
            "core_34_50_bot": c3_bot,
            "cloud_2_state": "BULLISH" if c2_short >= c2_long else "BEARISH",
            "cloud_3_state": "BULLISH" if c3_short >= c3_long else "BEARISH",
            "cushion_bounce": cushion_bounce
        }
