"""
Engine #10: ICT Institutional Displacement & DQS Scoring (TradingView Pine Script Exact Port)
Calculates Displacement Quality Score (DQS 0-100):
- Body Score (/30): Candle body vs ATR(14)
- Volatility Score (/30): Total range vs ATR(14)
- Conviction Score (/20): Body to range ratio
- Volume Score (/20): Relative volume vs 20-period SMA
Grades: A+ (>=90), A (80-89), B (65-79), C (50-64), FAIL (<50)
"""
import math

class ICTDisplacementEngine:
    def __init__(self, atr_period=14, vol_period=20):
        self.atr_period = atr_period
        self.vol_period = vol_period

    def _calc_atr(self, candles):
        if len(candles) < self.atr_period + 1:
            return 1.0
        trs = []
        for i in range(1, len(candles)):
            c = candles[i]
            prev = candles[i - 1]
            tr = max(c['h'] - c['l'], abs(c['h'] - prev['c']), abs(c['l'] - prev['c']))
            trs.append(tr)
        return sum(trs[-self.atr_period:]) / self.atr_period

    def analyze(self, candles):
        if len(candles) < max(self.atr_period, self.vol_period) + 2:
            return {
                "has_displacement": False,
                "dqs_score": 0.0,
                "grade": "N/A",
                "displacement_type": "NEUTRAL",
                "mss_status": "NONE",
                "atr": 1.0
            }

        atr = self._calc_atr(candles)
        last_c = candles[-1]
        body = abs(last_c['c'] - last_c['o'])
        rng = max(last_c['h'] - last_c['l'], 0.0001)
        body_ratio = body / rng
        is_bullish = last_c['c'] > last_c['o']

        # Volume score
        vols = [float(c.get('v', 0)) for c in candles[-self.vol_period-1:-1]]
        avg_vol = sum(vols) / len(vols) if vols else 1.0
        curr_vol = float(last_c.get('v', 0))
        vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 1.0

        # Sub-scores
        body_score = min(30.0, (body / (atr * 2.0)) * 30.0)
        vol_score = min(30.0, (rng / (atr * 1.8)) * 30.0)
        conviction_score = min(20.0, body_ratio * 20.0)
        volume_score = min(20.0, (vol_ratio / 2.0) * 20.0)

        total_dqs = round(body_score + vol_score + conviction_score + volume_score, 1)

        # Grade
        if total_dqs >= 90:
            grade = "A+ (90-100 Institutional Climax)"
        elif total_dqs >= 80:
            grade = "A (80-89 High Conviction)"
        elif total_dqs >= 65:
            grade = "B (65-79 Moderate Displacement)"
        elif total_dqs >= 50:
            grade = "C (50-64 Weak Displacement)"
        else:
            grade = "FAIL (<50 Normal Trading)"

        meets_min_grade = total_dqs >= 65
        has_disp = meets_min_grade and (body >= atr * 1.2)

        disp_type = f"{'BULLISH' if is_bullish else 'BEARISH'} DISPLACEMENT (Grade {grade.split(' ')[0]})" if has_disp else "NORMAL CANDLE"

        # Check Market Structure Shift (MSS)
        recent = candles[-15:-1]
        swing_high = max(c['h'] for c in recent)
        swing_low = min(c['l'] for c in recent)

        mss_status = "NONE"
        if has_disp and is_bullish and last_c['c'] > swing_high:
            mss_status = f"BULLISH MSS (Displaced above ${swing_high:,.1f})"
        elif has_disp and not is_bullish and last_c['c'] < swing_low:
            mss_status = f"BEARISH MSS (Displaced below ${swing_low:,.1f})"

        return {
            "has_displacement": has_disp,
            "dqs_score": total_dqs,
            "grade": grade,
            "displacement_type": disp_type,
            "mss_status": mss_status,
            "body_ratio_pct": round(body_ratio * 100, 1),
            "atr_multiple": round(body / atr, 2) if atr > 0 else 1.0,
            "atr": round(atr, 1)
        }
