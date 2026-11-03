"""
AlgoAlpha Trend Targets Pure Python Engine
Directly translated from official Pine Script v6: 'Trend Targets [AlgoAlpha]' (© AlgoAlpha)
"""
import numpy as np

class AlgoAlphaTrendTargets:
    def __init__(self, st_factor=12.0, st_atr_period=90, wma_length=40, ema_length=14, 
                 cont_factor=3, atr_period=14, sl_mult=5.0, tp1_mult=0.5, tp2_mult=1.0, tp3_mult=1.5):
        self.st_factor = st_factor
        self.st_atr_period = st_atr_period
        self.wma_length = wma_length
        self.ema_length = ema_length
        self.cont_factor = cont_factor
        self.atr_period = atr_period
        self.sl_mult = sl_mult
        self.tp1_mult = tp1_mult
        self.tp2_mult = tp2_mult
        self.tp3_mult = tp3_mult

    def _calc_tr_series(self, highs, lows, closes):
        n = len(highs)
        tr = [highs[0] - lows[0]]
        for i in range(1, n):
            tr.append(max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])))
        return tr

    def _calc_atr_series(self, tr, period):
        n = len(tr)
        atr = [0.0] * n
        if n == 0:
            return atr
        curr_atr = sum(tr[:min(period, n)]) / max(min(period, n), 1)
        for i in range(n):
            if i < period:
                atr[i] = curr_atr
            else:
                curr_atr = (curr_atr * (period - 1) + tr[i]) / period
                atr[i] = curr_atr
        return atr

    def _calc_wma(self, series, length):
        n = len(series)
        wma = [0.0] * n
        weight_sum = length * (length + 1) / 2.0
        for i in range(n):
            if i < length - 1:
                wma[i] = series[i]
            else:
                sub = series[i - length + 1 : i + 1]
                weighted = sum((k + 1) * sub[k] for k in range(length))
                wma[i] = weighted / weight_sum
        return wma

    def _calc_ema(self, series, length):
        n = len(series)
        ema = [0.0] * n
        if n == 0:
            return ema
        alpha = 2.0 / (length + 1.0)
        curr = series[0]
        for i in range(n):
            curr = alpha * series[i] + (1.0 - alpha) * curr
            ema[i] = curr
        return ema

    def analyze(self, candles):
        """
        candles: list of dicts with 'o', 'h', 'l', 'c', 'v', 't'
        """
        n = len(candles)
        min_bars = self.st_atr_period + self.wma_length + self.ema_length
        if n < min_bars:
            return {"error": f"Need at least {min_bars} candles, got {n}"}

        opens = [c['o'] for c in candles]
        highs = [c['h'] for c in candles]
        lows = [c['l'] for c in candles]
        closes = [c['c'] for c in candles]

        hl2 = [(highs[i] + lows[i]) / 2.0 for i in range(n)]
        tr = self._calc_tr_series(highs, lows, closes)
        st_atr = self._calc_atr_series(tr, self.st_atr_period)
        vol_atr = self._calc_atr_series(tr, self.atr_period)

        # 1. Supertrend Bands
        lowerBand = [0.0] * n
        upperBand = [0.0] * n

        prev_l = hl2[0] - self.st_factor * st_atr[0]
        prev_u = hl2[0] + self.st_factor * st_atr[0]

        for i in range(n):
            src = hl2[i]
            cur_atr = st_atr[i]
            raw_upper = src + self.st_factor * cur_atr
            raw_lower = src - self.st_factor * cur_atr

            if i == 0:
                lowerBand[i] = raw_lower
                upperBand[i] = raw_upper
            else:
                c_prev = closes[i-1]
                l_prev = lowerBand[i-1]
                u_prev = upperBand[i-1]

                lowerBand[i] = raw_lower if (raw_lower > l_prev or c_prev < l_prev) else l_prev
                upperBand[i] = raw_upper if (raw_upper < u_prev or c_prev > u_prev) else u_prev

        # 2. Baseline tL = ta.ema(ta.wma(avg(lwr, upr), 40), 14)
        avg_bands = [(lowerBand[i] + upperBand[i]) / 2.0 for i in range(n)]
        wma_bands = self._calc_wma(avg_bands, self.wma_length)
        tL = self._calc_ema(wma_bands, self.ema_length)

        # 3. Trend tracking
        trend = [0] * n
        cur_trend = 0
        for i in range(1, n):
            if tL[i] > tL[i-1]:
                cur_trend = 1
            elif tL[i] < tL[i-1]:
                cur_trend = -1
            trend[i] = cur_trend

        # 4. Continuation & Rejections
        rejcount = 0
        rejections = []
        for i in range(1, n):
            tr_val = trend[i]
            line_val = tL[i]
            bullish_rej = (tr_val == 1) and (highs[i] > line_val) and (lows[i] < line_val)
            bearish_rej = (tr_val == -1) and (highs[i] > line_val) and (lows[i] < line_val)

            if bullish_rej or bearish_rej:
                rejcount += 1
            
            # Trend cross or no rejection breaks streak
            if (trend[i] != trend[i-1]) or (not (bullish_rej or bearish_rej) and rejcount > 0):
                rejcount = 0

            if rejcount > self.cont_factor:
                if tr_val == 1:
                    rejections.append({"idx": i, "type": "BULLISH_REJECTION", "baseline": line_val})
                elif tr_val == -1:
                    rejections.append({"idx": i, "type": "BEARISH_REJECTION", "baseline": line_val})

        # 5. Targets for Current Bar
        curr_price = closes[-1]
        curr_tL = tL[-1]
        curr_trend = trend[-1]
        curr_vol = vol_atr[-1]

        # Targets calculation based on current trend
        if curr_trend == 1:
            sl = lows[-1] - curr_vol * self.sl_mult
            risk = abs(curr_price - sl)
            tp1 = curr_price + risk * self.tp1_mult
            tp2 = curr_price + risk * self.tp2_mult
            tp3 = curr_price + risk * self.tp3_mult
            trend_str = "BULLISH (Uptrend Baseline)"
        else:
            sl = highs[-1] + curr_vol * self.sl_mult
            risk = abs(curr_price - sl)
            tp1 = curr_price - risk * self.tp1_mult
            tp2 = curr_price - risk * self.tp2_mult
            tp3 = curr_price - risk * self.tp3_mult
            trend_str = "BEARISH (Downtrend Baseline)"

        return {
            "current_price": curr_price,
            "trend_direction": trend_str,
            "trend_numeric": curr_trend,
            "baseline_tL": round(curr_tL, 2),
            "distance_to_baseline": round(curr_price - curr_tL, 2),
            "volatility_atr": round(curr_vol, 2),
            "calculated_sl": round(sl, 2),
            "calculated_tp1": round(tp1, 2),
            "calculated_tp2": round(tp2, 2),
            "calculated_tp3": round(tp3, 2),
            "latest_rejection": rejections[-1] if rejections else None
        }
