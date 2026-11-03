"""
Engine #19: LunqFX Order Flow — Volume Delta, CVD, Absorption & Divergence (Pine Script Exact Port)
Implements:
- Buy Volume vs Sell Volume intra-bar split
- CVD (Cumulative Volume Delta)
- Absorption: volume > 1.8x SMA(20) and body < 0.35 * ATR(14)
- Delta Divergences: Price makes higher high while CVD makes lower high (Bearish) or vice versa (Bullish)
"""

class LuxAlgoOrderFlow:
    def __init__(self, div_len=8, abs_mult=1.8, abs_body=0.35):
        self.div_len = div_len
        self.abs_mult = abs_mult
        self.abs_body = abs_body

    def analyze(self, candles):
        if len(candles) < 25:
            return {
                "latest_delta": 0.0,
                "buy_share_pct": 50.0,
                "delta_sentiment": "NEUTRAL",
                "cvd_value": 0.0,
                "absorption_detected": False,
                "divergence_signal": "NONE"
            }

        # Calculate ATR(14) and SMA(20) Volume
        trs = [max(candles[i]['h'] - candles[i]['l'], abs(candles[i]['h'] - candles[i-1]['c']), abs(candles[i]['l'] - candles[i-1]['c'])) for i in range(1, len(candles))]
        atr14 = sum(trs[-14:]) / 14.0 if len(trs) >= 14 else 1.0

        vols = [float(c.get('v', 0)) for c in candles[-21:-1]]
        vol_avg = sum(vols) / len(vols) if vols else 1.0

        cvd = 0.0
        cvd_series = []
        deltas = []

        for c in candles[-40:]:
            rng = max(c['h'] - c['l'], 0.0001)
            v = float(c.get('v', 0))
            buy_vol = v * (c['c'] - c['l']) / rng
            sell_vol = v * (c['h'] - c['c']) / rng
            d = buy_vol - sell_vol
            cvd += d
            cvd_series.append(cvd)
            deltas.append(d)

        last_c = candles[-1]
        last_v = float(last_c.get('v', 0))
        last_d = deltas[-1]
        last_rng = max(last_c['h'] - last_c['l'], 0.0001)
        buy_vol = last_v * (last_c['c'] - last_c['l']) / last_rng
        buy_share = round(buy_vol / last_v * 100, 1) if last_v > 0 else 50.0

        # Absorption check
        last_body = abs(last_c['c'] - last_c['o'])
        absorption = (last_v > vol_avg * self.abs_mult) and (last_body < atr14 * self.abs_body)
        abs_type = "ABSORPTION DETECTED (Heavy Volume, Tight Range - Institutional Wall)" if absorption else "NONE"

        # Delta Divergence over div_len
        p_highs = [c['h'] for c in candles[-self.div_len*2:]]
        p_lows = [c['l'] for c in candles[-self.div_len*2:]]
        
        bull_div = False
        bear_div = False
        if len(cvd_series) >= self.div_len + 2:
            if candles[-1]['h'] > candles[-self.div_len]['h'] and cvd_series[-1] < cvd_series[-self.div_len]:
                bear_div = True
            elif candles[-1]['l'] < candles[-self.div_len]['l'] and cvd_series[-1] > cvd_series[-self.div_len]:
                bull_div = True

        div_sig = "NONE"
        if bear_div:
            div_sig = "▼ BEARISH DELTA DIVERGENCE (Price Higher High but CVD Falling)"
        elif bull_div:
            div_sig = "▲ BULLISH DELTA DIVERGENCE (Price Lower Low but CVD Rising)"

        sentiment = "▲ BUYERS IN CONTROL" if last_d >= 0 else "▼ SELLERS IN CONTROL"

        return {
            "latest_delta": round(last_d, 1),
            "buy_share_pct": buy_share,
            "delta_sentiment": f"{sentiment} ({buy_share}% Buy Pressure)",
            "cvd_value": round(cvd, 1),
            "absorption_detected": absorption,
            "absorption_status": abs_type,
            "divergence_signal": div_sig
        }
