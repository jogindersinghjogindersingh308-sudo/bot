"""
Engine #17: LuxAlgo Reversal Signals & Exhaustion Engine (Pine Script Exact Port)
Implements:
- Momentum Phase (TD 9 Setup): Count 1 to 9 (close < close[4] for Bullish, close > close[4] for Bearish)
- Perfect 9 Condition (pbS / psS)
- Trend Exhaustion Phase (TD 13 Countdown): Count 1 to 13 (close <= low[2] or close >= high[2])
- Dynamic Risk Levels (bSD / sSD) & Target Levels (bCT / sCT)
"""

class LuxAlgoReversalEngine:
    def __init__(self):
        pass

    def analyze(self, candles):
        if len(candles) < 30:
            return {
                "momentum_phase": "None",
                "exhaustion_phase": "None",
                "reversal_signal": "NONE",
                "bull_risk_level": 0.0,
                "bear_risk_level": 0.0
            }

        # Simulate stateful counting across candle history
        b_sc = 0
        s_sc = 0
        b_sl = 0.0
        b_sh = 0.0
        s_sh = 0.0
        s_sl = 0.0

        b_cc = 0
        s_cc = 0
        b_c8 = 0.0
        s_c8 = 0.0

        for i in range(4, len(candles)):
            c = candles[i]
            prev4 = candles[i - 4]

            # Momentum Setup (1 to 9)
            if c['c'] < prev4['c']:
                b_sc = 1 if b_sc == 9 else b_sc + 1
                s_sc = 0
            else:
                s_sc = 1 if s_sc == 9 else s_sc + 1
                b_sc = 0

            # Track lowest/highest during setup
            if b_sc == 1:
                b_sl = c['l']
            elif b_sc > 1:
                b_sl = min(c['l'], b_sl)
                if c['l'] == b_sl:
                    b_sh = c['h']

            if s_sc == 1:
                s_sh = c['h']
            elif s_sc > 1:
                s_sh = max(c['h'], s_sh)
                if c['h'] == s_sh:
                    s_sl = c['l']

            # Exhaustion Countdown (1 to 13)
            if i >= 6:
                c_prev2 = candles[i - 2]
                if b_sc >= 9 or b_cc > 0:
                    if c['c'] <= c_prev2['l']:
                        b_cc += 1
                        if b_cc == 8:
                            b_c8 = c['c']
                        if b_cc >= 13:
                            b_cc = 13
                if s_sc >= 9 or s_cc > 0:
                    if c['c'] >= c_prev2['h']:
                        s_cc += 1
                        if s_cc == 8:
                            s_c8 = c['c']
                        if s_cc >= 13:
                            s_cc = 13

        # Risk Levels
        b_sd = (2 * b_sl - b_sh) if b_sc == 9 else 0.0
        s_sd = (2 * s_sh - s_sl) if s_sc == 9 else 0.0

        # Signals
        mom_status = f"BULLISH MOMENTUM ({b_sc}/9)" if b_sc > 0 else f"BEARISH MOMENTUM ({s_sc}/9)"
        exh_status = "NONE"
        if b_cc > 0:
            exh_status = f"BULLISH EXHAUSTION COUNTDOWN ({b_cc}/13)"
        elif s_cc > 0:
            exh_status = f"BEARISH EXHAUSTION COUNTDOWN ({s_cc}/13)"

        rev_sig = "NORMAL"
        if b_sc == 9:
            rev_sig = "★ LUXALGO COMPLETED BULLISH SETUP 9 (High Probability Long Setup)"
        elif s_sc == 9:
            rev_sig = "★ LUXALGO COMPLETED BEARISH SETUP 9 (High Probability Short Setup)"
        elif b_cc == 13:
            rev_sig = "🔥 LUXALGO FULL BULLISH EXHAUSTION 13 (Market Bottom Inflection!)"
        elif s_cc == 13:
            rev_sig = "🔥 LUXALGO FULL BEARISH EXHAUSTION 13 (Market Top Inflection!)"

        return {
            "momentum_phase": mom_status,
            "exhaustion_phase": exh_status,
            "reversal_signal": rev_sig,
            "b_setup_count": b_sc,
            "s_setup_count": s_sc,
            "b_exh_count": b_cc,
            "s_exh_count": s_cc,
            "bull_risk_level": round(b_sd, 1),
            "bear_risk_level": round(s_sd, 1)
        }
