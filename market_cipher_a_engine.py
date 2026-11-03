"""
MarketCipher A Engine (Official Pine Script Exact Port)
Implements:
- 8-EMA Ribbon (5, 11, 15, 18, 21, 25, 29, 33)
- WaveTrend (ohlc4, n1=7, n2=12)
- RSI(14)
- Signals:
  * Blood Diamond: Red Diamond + Red Cross (WTCrossDown + crossunder(ema5, ema11)) -> Major Short Dump
  * Yellow Cross: Red Diamond + RSI <= 30 + WT2 <= -53 -> Capitulation Bullish Reversal
  * Blue Triangle: crossover(ema11, ema15) -> Bullish Push
  * Long EMA: crossover(ema11, ema33)
  * Short EMA: crossover(ema33, ema11)
"""

class MarketCipherAEngine:
    def __init__(self):
        self.ema_lens = [5, 11, 15, 18, 21, 25, 29, 33]
        self.n1 = 7
        self.n2 = 12

    def _calc_ema_series(self, series, period):
        if not series:
            return []
        k = 2.0 / (period + 1.0)
        res = [series[0]]
        for val in series[1:]:
            res.append((val * k) + (res[-1] * (1.0 - k)))
        return res

    def _calc_rsi(self, closes, period=14):
        if len(closes) < period + 1:
            return 50.0
        gains = []
        losses = []
        for i in range(1, len(closes)):
            chg = closes[i] - closes[i - 1]
            gains.append(max(chg, 0.0))
            losses.append(max(-chg, 0.0))
        # RMA
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))

    def analyze(self, candles):
        if len(candles) < 45:
            return {
                "blood_diamond": False,
                "yellow_cross": False,
                "blue_triangle": False,
                "signal_name": "NONE",
                "ribbon_bias": "NEUTRAL",
                "rsi": 50.0
            }

        closes = [c['c'] for c in candles]
        ohlc4 = [(c['o'] + c['h'] + c['l'] + c['c']) / 4.0 for c in candles]

        # 8-EMA Ribbon
        emas = {}
        for l in self.ema_lens:
            emas[l] = self._calc_ema_series(closes, l)

        e5_curr, e5_prev = emas[5][-1], emas[5][-2]
        e11_curr, e11_prev = emas[11][-1], emas[11][-2]
        e15_curr, e15_prev = emas[15][-1], emas[15][-2]
        e33_curr, e33_prev = emas[33][-1], emas[33][-2]

        # WaveTrend (n1=7, n2=12)
        esa = self._calc_ema_series(ohlc4, self.n1)
        abs_diff = [abs(ohlc4[i] - esa[i]) for i in range(len(ohlc4))]
        de = self._calc_ema_series(abs_diff, self.n1)

        ci = []
        for i in range(len(ohlc4)):
            de_val = de[i]
            ci_val = (ohlc4[i] - esa[i]) / (0.015 * de_val) if de_val > 0 else 0.0
            ci.append(ci_val)

        wt1 = self._calc_ema_series(ci, self.n2)
        wt2 = []
        for i in range(len(wt1)):
            if i < 2:
                wt2.append(wt1[i])
            else:
                wt2.append(sum(wt1[i-2:i+1]) / 3.0)

        curr_wt1, prev_wt1 = wt1[-1], wt1[-2]
        curr_wt2, prev_wt2 = wt2[-1], wt2[-2]

        wt_cross_down = (prev_wt1 >= prev_wt2) and (curr_wt1 < curr_wt2)
        red_diamond = wt_cross_down
        red_cross = (e5_prev >= e11_prev) and (e5_curr < e11_curr)

        rsi_val = self._calc_rsi(closes)

        blood_diamond = red_diamond and red_cross
        yellow_cross = red_diamond and (rsi_val <= 30.0) and (curr_wt2 <= -53.0)
        blue_triangle = (e11_prev <= e15_prev) and (e11_curr > e15_curr)

        sig_name = "NONE"
        if blood_diamond:
            sig_name = "🩸 BLOOD DIAMOND (Severe Bearish Crash Warning!)"
        elif yellow_cross:
            sig_name = "⭐ YELLOW CROSS (Capitulation Bottom Reversal!)"
        elif blue_triangle:
            sig_name = "🔺 BLUE TRIANGLE (Bullish Ribbon Expansion)"
        elif e11_curr > e33_curr:
            sig_name = "🟢 BULLISH RIBBON EXPANSION (EMA 11 > 33)"
        else:
            sig_name = "🔴 BEARISH RIBBON EXPANSION (EMA 11 < 33)"

        ribbon_bias = "BULLISH" if e11_curr > e33_curr else "BEARISH"

        return {
            "blood_diamond": blood_diamond,
            "yellow_cross": yellow_cross,
            "blue_triangle": blue_triangle,
            "signal_name": sig_name,
            "ribbon_bias": ribbon_bias,
            "rsi": round(rsi_val, 1),
            "wt2": round(curr_wt2, 1)
        }
