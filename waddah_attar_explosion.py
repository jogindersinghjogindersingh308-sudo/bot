"""
Engine #24: Waddah Attar Explosion (WAE) Engine (Official Formula Port)
Implements:
- MACD Velocity Sensitivity: t1 = (MACD(20,40) - MACD[1](20,40)) * 150
- Bollinger Band Explosion Line: e1 = UpperBB(20, 2.0) - LowerBB(20, 2.0)
- DeadZone Line: ATR(100) * 3.7
- Signals:
  * BULLISH EXPLOSION: UpTrend > e1 and UpTrend > DeadZone
  * BEARISH EXPLOSION: DownTrend > e1 and DownTrend > DeadZone
  * NO EXPLOSION / DEADZONE: Volume is asleep
"""
import math

class WaddahAttarExplosionEngine:
    def __init__(self, fast_len=20, slow_len=40, bb_len=20, bb_mult=2.0, atr_len=50, deadzone_mult=3.7):
        self.fast_len = fast_len
        self.slow_len = slow_len
        self.bb_len = bb_len
        self.bb_mult = bb_mult
        self.atr_len = atr_len
        self.deadzone_mult = deadzone_mult

    def _calc_ema_series(self, series, period):
        if not series:
            return []
        k = 2.0 / (period + 1.0)
        res = [series[0]]
        for val in series[1:]:
            res.append((val * k) + (res[-1] * (1.0 - k)))
        return res

    def _calc_atr(self, candles, period):
        if len(candles) < period + 1:
            return 1.0
        trs = []
        for i in range(1, len(candles)):
            c = candles[i]
            prev = candles[i - 1]
            tr = max(c['h'] - c['l'], abs(c['h'] - prev['c']), abs(c['l'] - prev['c']))
            trs.append(tr)
        return sum(trs[-period:]) / period if trs else 1.0

    def analyze(self, candles):
        if len(candles) < max(self.slow_len, self.bb_len, self.atr_len) + 5:
            return {
                "uptrend_val": 0.0,
                "downtrend_val": 0.0,
                "explosion_line": 0.0,
                "deadzone_line": 0.0,
                "status": "DEADZONE (Low Volatility)",
                "is_exploding": False
            }

        closes = [c['c'] for c in candles]

        # MACD (fast, slow)
        ema_fast = self._calc_ema_series(closes, self.fast_len)
        ema_slow = self._calc_ema_series(closes, self.slow_len)
        macd = [ema_fast[i] - ema_slow[i] for i in range(len(closes))]

        # Velocity t1
        t1_curr = (macd[-1] - macd[-2]) * 150.0
        uptrend = max(0.0, t1_curr)
        downtrend = max(0.0, -t1_curr)

        # Bollinger Band difference (Upper - Lower)
        sub_closes = closes[-self.bb_len:]
        mean = sum(sub_closes) / len(sub_closes)
        var = sum((x - mean) ** 2 for x in sub_closes) / len(sub_closes)
        dev = math.sqrt(var)
        upper_bb = mean + self.bb_mult * dev
        lower_bb = mean - self.bb_mult * dev
        e1 = upper_bb - lower_bb

        # Deadzone line via ATR
        atr_val = self._calc_atr(candles, self.atr_len)
        deadzone = atr_val * self.deadzone_mult

        is_exploding = False
        if uptrend > e1 and uptrend > deadzone:
            status = f"🟢 BULLISH EXPLOSION TRIGGERED (+{uptrend:.1f} > {e1:.1f})"
            is_exploding = True
        elif downtrend > e1 and downtrend > deadzone:
            status = f"🔴 BEARISH EXPLOSION TRIGGERED (+{downtrend:.1f} > {e1:.1f})"
            is_exploding = True
        elif uptrend > 0 and uptrend > deadzone:
            status = f"🟢 POSITIVE MOMENTUM (Above Deadzone, Below Explosion)"
        elif downtrend > 0 and downtrend > deadzone:
            status = f"🔴 NEGATIVE MOMENTUM (Above Deadzone, Below Explosion)"
        else:
            status = "⚪ DORMANT DEADZONE (Volatility Below Threshold)"

        return {
            "uptrend_val": round(uptrend, 1),
            "downtrend_val": round(downtrend, 1),
            "explosion_line": round(e1, 1),
            "deadzone_line": round(deadzone, 1),
            "status": status,
            "is_exploding": is_exploding
        }
