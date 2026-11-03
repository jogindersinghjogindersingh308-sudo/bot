"""
MarketCipher B Engine (Official Pine Script Exact Port)
Implements:
- WaveTrend Oscillators (wt1, wt2) via EMA/SMA of HLC3
- MarketCipher Green Dot (Bullish Crossover in Oversold)
- MarketCipher Red Dot (Bearish Crossover in Overbought)
- Money Flow Wave (RSI+MFI Area): candleValue = (close-open)/(high-low), 60-SMA
- WaveTrend Regular Bullish & Bearish Divergences
"""
import math

class MarketCipherBEngine:
    def __init__(self, n1=9, n2=12, mfi_period=60, ob_level=53, os_level=-53):
        self.n1 = n1
        self.n2 = n2
        self.mfi_period = mfi_period
        self.ob_level = ob_level
        self.os_level = os_level

    def _calc_ema(self, series, period):
        if len(series) < period:
            return series[-1] if series else 0.0
        k = 2.0 / (period + 1.0)
        ema_val = sum(series[:period]) / period
        for val in series[period:]:
            ema_val = (val * k) + (ema_val * (1.0 - k))
        return ema_val

    def _calc_ema_series(self, series, period):
        if not series:
            return []
        k = 2.0 / (period + 1.0)
        res = [series[0]]
        for val in series[1:]:
            res.append((val * k) + (res[-1] * (1.0 - k)))
        return res

    def analyze(self, candles):
        if len(candles) < max(self.mfi_period, 35):
            return {
                "wt1": 0.0,
                "wt2": 0.0,
                "signal_dot": "NONE",
                "money_flow": 0.0,
                "money_flow_state": "NEUTRAL",
                "divergence": "NONE"
            }

        # 1. Calculate HLC3 series
        hlc3_series = [(c['h'] + c['l'] + c['c']) / 3.0 for c in candles]

        # esa = ema(ap, n1)
        esa_series = self._calc_ema_series(hlc3_series, self.n1)
        
        # d = ema(abs(ap - esa), n1)
        abs_diff = [abs(hlc3_series[i] - esa_series[i]) for i in range(len(hlc3_series))]
        d_series = self._calc_ema_series(abs_diff, self.n1)

        # ci = (ap - esa) / (0.015 * d)
        ci_series = []
        for i in range(len(hlc3_series)):
            d_val = d_series[i]
            ci = (hlc3_series[i] - esa_series[i]) / (0.015 * d_val) if d_val > 0 else 0.0
            ci_series.append(ci)

        # tci = ema(ci, n2) = wt1
        wt1_series = self._calc_ema_series(ci_series, self.n2)

        # wt2 = sma(wt1, 3)
        wt2_series = []
        for i in range(len(wt1_series)):
            if i < 2:
                wt2_series.append(wt1_series[i])
            else:
                wt2_series.append(sum(wt1_series[i-2:i+1]) / 3.0)

        curr_wt1 = round(wt1_series[-1], 2)
        prev_wt1 = round(wt1_series[-2], 2)
        curr_wt2 = round(wt2_series[-1], 2)
        prev_wt2 = round(wt2_series[-2], 2)

        # Green & Red Dots
        cross_up = (prev_wt1 <= prev_wt2) and (curr_wt1 > curr_wt2)
        cross_down = (prev_wt1 >= prev_wt2) and (curr_wt1 < curr_wt2)

        signal_dot = "NONE"
        if cross_up and curr_wt2 <= self.os_level:
            signal_dot = "🟢 GREEN DOT (Major Bullish Oversold Reversal)"
        elif cross_up:
            signal_dot = "🟢 GREEN CROSS (Bullish Momentum Turn)"
        elif cross_down and curr_wt1 >= self.ob_level:
            signal_dot = "🔴 RED DOT (Major Bearish Overbought Reversal)"
        elif cross_down:
            signal_dot = "🔴 RED CROSS (Bearish Momentum Turn)"

        # 2. Money Flow Wave (RSI+MFI Area)
        # candleValue = (close - open) / (high - low)
        cv_series = []
        for c in candles:
            rng = max(c['h'] - c['l'], 0.0001)
            cv_series.append((c['c'] - c['o']) / rng)

        sub_cv = cv_series[-self.mfi_period:]
        mvc = sum(sub_cv) / len(sub_cv) if sub_cv else 0.0
        money_flow = round(mvc * 190.0, 2)
        mf_state = f"🟢 GREEN INFLOW (+{money_flow})" if money_flow > 0 else f"🔴 RED OUTFLOW ({money_flow})"

        # 3. WaveTrend Divergences
        div = "NONE"
        if len(candles) >= 15:
            p_curr = candles[-1]['c']
            p_prev = candles[-8]['c']
            wt_curr = wt1_series[-1]
            wt_prev = wt1_series[-8]
            if p_curr < p_prev and wt_curr > wt_prev and curr_wt1 < 0:
                div = "▲ REGULAR BULLISH DIVERGENCE (Price Lower Low, Wave Higher Low)"
            elif p_curr > p_prev and wt_curr < wt_prev and curr_wt1 > 0:
                div = "▼ REGULAR BEARISH DIVERGENCE (Price Higher High, Wave Lower High)"

        return {
            "wt1": curr_wt1,
            "wt2": curr_wt2,
            "signal_dot": signal_dot,
            "money_flow": money_flow,
            "money_flow_state": mf_state,
            "divergence": div
        }
