"""
Harmonic Fibonacci Bands Pure Python Engine
Directly translated from official Pine Script: 'Auto Fibonacci Bands for Harmonic (AFB4H)' by madoqa.
Calculates exact Previous Day Range (PDR), Golden Ratio Extensions (1.618, 2.618),
and Harmonic Potential Reversal Zones (0.886 Bat, 0.786 Gartley, 0.618 Golden Pocket).
"""
import datetime

class HarmonicFibonacciEngine:
    def __init__(self):
        pass

    def analyze(self, candles):
        """
        candles: list of 1H or 15m candles with 'o', 'h', 'l', 'c', 'v', 't'
        """
        n = len(candles)
        if n < 24:
            return {"error": "Not enough candle data for Harmonic Fibonacci calculation"}

        curr_price = candles[-1]['c']
        last_t = candles[-1]['t']
        last_dt = datetime.datetime.fromtimestamp(last_t, tz=datetime.timezone.utc)

        # Separate into UTC Days
        # Current UTC day start
        cur_day_start = datetime.datetime(last_dt.year, last_dt.month, last_dt.day, tzinfo=datetime.timezone.utc).timestamp()
        prev_day_start = cur_day_start - 86400

        # Filter previous day candles
        prev_day_candles = [c for c in candles if prev_day_start <= c['t'] < cur_day_start]
        
        if not prev_day_candles:
            # Fallback to 24 bars ago
            prev_day_candles = candles[-48:-24] if n >= 48 else candles[:n//2]

        pdh = max(c['h'] for c in prev_day_candles)
        pdl = min(c['l'] for c in prev_day_candles)
        pdc = prev_day_candles[-1]['c']
        pdr = pdh - pdl # Previous day range (pzs in Pine Script)

        # Exact Harmonic Fib Calculations as defined in AFB4H:
        # pc = Previous Close, pzs = Previous Range
        # Upper Levels
        fib_2618 = pdc + pdr * 2.1018 * 2.0  # 2.618 Extension
        fib_1618 = pdc + pdr * 1.1018 * 2.0  # 1.618 Golden Ratio Target
        fib_1382 = pdc + pdr * 0.882 * 2.0   # 1.382 Extension
        fib_1000 = pdc + pdr                 # 1.000 Range Top (ch in Pine)
        fib_0886 = pdc + pdr * 0.386 * 2.0   # 0.886 Harmonic Bat PRZ
        fib_0786 = pdc + pdr * 0.286 * 2.0   # 0.786 Harmonic Gartley PRZ
        fib_0618 = pdc + pdr * 0.118 * 2.0   # 0.618/0.682 Golden Pocket
        
        # Center Level
        fib_center = pdc                     # Center Anchor (pc in Pine)

        # Lower Levels
        fib_0382 = pdc - pdr * 0.118 * 2.0   # 0.382 Retracement
        fib_0286 = pdc - pdr * 0.286 * 2.0   # 0.286 Retracement
        fib_0000 = pdc - pdr                 # 0.000 Range Bottom (cl in Pine)
        fib_neg_0382 = pdc - pdr * 0.882 * 2.0   # -0.382 Downside Extension
        fib_neg_0618 = pdc - pdr * 1.1018 * 2.0  # -0.618 Downside Extension
        fib_neg_1618 = pdc - pdr * 2.1018 * 2.0  # -1.618 Golden Downside Target

        # Harmonic Zone Analysis
        if curr_price >= fib_1618:
            zone = "1.618+ EXTENSION (Super Bullish Expansion)"
        elif curr_price >= fib_1000:
            zone = "1.000 - 1.382 EXPANSION ZONE"
        elif curr_price >= fib_0886:
            zone = "0.886 HARMONIC BAT PRZ (Reversal Resistance Zone)"
        elif curr_price >= fib_0618:
            zone = "0.618 - 0.786 GOLDEN POCKET (Harmonic Bullish Zone)"
        elif curr_price >= fib_center:
            zone = "CENTER - 0.618 (Upper Equilibrium)"
        elif curr_price >= fib_0382:
            zone = "0.382 - CENTER (Lower Equilibrium)"
        elif curr_price >= fib_0000:
            zone = "0.000 - 0.382 HARMONIC DISCOUNT ZONE"
        elif curr_price >= fib_neg_0618:
            zone = "DOWNSIDE EXTENSION (-0.618)"
        else:
            zone = "-1.618 GOLDEN DOWNSIDE TARGET"

        # Nearest Harmonic Support & Resistance
        all_levels = [
            ("2.618 Ext", fib_2618),
            ("1.618 Golden Ext", fib_1618),
            ("1.382 Ext", fib_1382),
            ("1.000 Top", fib_1000),
            ("0.886 Bat PRZ", fib_0886),
            ("0.786 Gartley", fib_0786),
            ("0.618 Golden Pocket", fib_0618),
            ("Center (PDC)", fib_center),
            ("0.382 Retracement", fib_0382),
            ("0.000 Bottom", fib_0000),
            ("-0.618 Down Ext", fib_neg_0618),
            ("-1.618 Golden Down", fib_neg_1618)
        ]

        resistances = [lvl for lvl in all_levels if lvl[1] > curr_price]
        supports = [lvl for lvl in all_levels if lvl[1] <= curr_price]

        next_res = min(resistances, key=lambda x: x[1]) if resistances else ("None", fib_2618)
        next_sup = max(supports, key=lambda x: x[1]) if supports else ("None", fib_neg_1618)

        return {
            "current_price": curr_price,
            "pdh": round(pdh, 2),
            "pdl": round(pdl, 2),
            "pdc": round(pdc, 2),
            "pdr_range": round(pdr, 2),
            "harmonic_zone": zone,
            "fib_1618": round(fib_1618, 2),
            "fib_0886_bat": round(fib_0886, 2),
            "fib_0618_golden": round(fib_0618, 2),
            "fib_center": round(fib_center, 2),
            "fib_0382": round(fib_0382, 2),
            "fib_neg_0618": round(fib_neg_0618, 2),
            "fib_neg_1618": round(fib_neg_1618, 2),
            "next_harmonic_resistance": f"{next_res[0]} (${next_res[1]:,.1f})",
            "next_harmonic_support": f"{next_sup[0]} (${next_sup[1]:,.1f})"
        }
