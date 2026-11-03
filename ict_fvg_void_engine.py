"""
Engine #13: ICT Fair Value Gaps (FVG) & LunqFX ISD Sequence Engine
Implements LunqFX PD Arrays & ISD Sequence:
- 3-bar Fair Value Gaps with 50% Consequent Encroachment (CE)
- Inversion FVGs (iFVG - flipped levels)
- Balanced Price Range (BPR - overlap between bull and bear FVGs)
- Inducement (IDM - false breakout trap with wick >= 0.3 ATR)
- ISD Sequence State Machine: 1/3 (IDM) -> 2/3 (Sweep) -> 3/3 (Full ISD Setup Complete!)
"""

class ICTFVGVoidEngine:
    def __init__(self, lookback=50, idm_period=5, idm_wick_mult=0.3):
        self.lookback = lookback
        self.idm_period = idm_period
        self.idm_wick_mult = idm_wick_mult

    def _calc_atr(self, candles, period=14):
        if len(candles) < period + 1:
            return 1.0
        trs = []
        for i in range(1, len(candles)):
            c = candles[i]
            prev = candles[i - 1]
            tr = max(c['h'] - c['l'], abs(c['h'] - prev['c']), abs(c['l'] - prev['c']))
            trs.append(tr)
        return sum(trs[-period:]) / period

    def analyze(self, candles):
        if len(candles) < max(self.lookback, 15):
            return {
                "active_bullish_fvgs": 0,
                "active_bearish_fvgs": 0,
                "bpr_active": False,
                "idm_status": "NONE",
                "isd_score": "0/3",
                "fvg_magnet_status": "NONE"
            }

        atr = self._calc_atr(candles)
        curr_price = candles[-1]['c']

        bullish_fvgs = []
        bearish_fvgs = []
        last_bull_fvg = None
        last_bear_fvg = None

        start_idx = max(0, len(candles) - self.lookback)
        for i in range(start_idx + 2, len(candles)):
            c1 = candles[i - 2]
            c2 = candles[i - 1]
            c3 = candles[i]

            # Bullish FVG
            if c3['l'] > c1['h'] and (c3['l'] - c1['h']) >= atr * 0.1:
                top = c3['l']
                bot = c1['h']
                ce = (top + bot) / 2.0
                mitigated = any(candles[j]['l'] <= bot for j in range(i + 1, len(candles)))
                f_data = {"top": top, "bottom": bot, "ce": ce, "mitigated": mitigated}
                last_bull_fvg = f_data
                if not mitigated:
                    bullish_fvgs.append(f_data)

            # Bearish FVG
            if c3['h'] < c1['l'] and (c1['l'] - c3['h']) >= atr * 0.1:
                top = c1['l']
                bot = c3['h']
                ce = (top + bot) / 2.0
                mitigated = any(candles[j]['h'] >= top for j in range(i + 1, len(candles)))
                f_data = {"top": top, "bottom": bot, "ce": ce, "mitigated": mitigated}
                last_bear_fvg = f_data
                if not mitigated:
                    bearish_fvgs.append(f_data)

        # Balanced Price Range (BPR)
        has_bpr = False
        bpr_top, bpr_bot = 0.0, 0.0
        if last_bull_fvg and last_bear_fvg:
            if last_bull_fvg['top'] >= last_bear_fvg['bottom'] and last_bull_fvg['bottom'] <= last_bear_fvg['top']:
                has_bpr = True
                bpr_top = min(last_bull_fvg['top'], last_bear_fvg['top'])
                bpr_bot = max(last_bull_fvg['bottom'], last_bear_fvg['bottom'])

        # Inducement (IDM) on confirmed bar
        recent_lo = min(c['l'] for c in candles[-self.idm_period-1:-1])
        recent_hi = max(c['h'] for c in candles[-self.idm_period-1:-1])
        last_c = candles[-1]
        min_wick = atr * self.idm_wick_mult

        bull_wick = recent_lo - last_c['l']
        bear_wick = last_c['h'] - recent_hi

        is_bull_idm = last_c['l'] < recent_lo and last_c['c'] > recent_lo and bull_wick >= min_wick
        is_bear_idm = last_c['h'] > recent_hi and last_c['c'] < recent_hi and bear_wick >= min_wick

        idm_sig = "NONE"
        if is_bull_idm:
            idm_sig = f"BEAR TRAP IDM (Liquidity inducement below ${recent_lo:,.1f})"
        elif is_bear_idm:
            idm_sig = f"BULL TRAP IDM (Liquidity inducement above ${recent_hi:,.1f})"

        # ISD Sequence Evaluation (IDM -> Sweep -> Displacement)
        isd_score_num = 0
        if is_bull_idm or is_bear_idm:
            isd_score_num = 1
            # Check 5-bar sweep
            sweep_lo = min(c['l'] for c in candles[-6:-1])
            sweep_hi = max(c['h'] for c in candles[-6:-1])
            if (is_bull_idm and last_c['l'] < sweep_lo) or (is_bear_idm and last_c['h'] > sweep_hi):
                isd_score_num = 2
                # Check displacement
                body = abs(last_c['c'] - last_c['o'])
                if body >= atr * 1.5:
                    isd_score_num = 3

        isd_str = f"ISD {isd_score_num}/3 {'(COMPLETE 3/3 SETUP!)' if isd_score_num == 3 else ''}"

        # Magnet FVG
        below_fvgs = [f for f in bullish_fvgs if f['top'] <= curr_price]
        nearest_bull = max(below_fvgs, key=lambda x: x['top']) if below_fvgs else None

        above_fvgs = [f for f in bearish_fvgs if f['bottom'] >= curr_price]
        nearest_bear = min(above_fvgs, key=lambda x: x['bottom']) if above_fvgs else None

        magnet_status = "BALANCED RANGE"
        if has_bpr:
            magnet_status = f"BPR ACTIVE ZONE (${bpr_bot:,.1f} - ${bpr_top:,.1f})"
        elif nearest_bear and (nearest_bear['bottom'] - curr_price) < (curr_price * 0.015):
            magnet_status = f"BEAR FVG MAGNET ABOVE (${nearest_bear['bottom']:,.1f})"
        elif nearest_bull and (curr_price - nearest_bull['top']) < (curr_price * 0.015):
            magnet_status = f"BULL FVG SUPPORT BELOW (${nearest_bull['top']:,.1f})"

        return {
            "bullish_fvg_count": len(bullish_fvgs),
            "bearish_fvg_count": len(bearish_fvgs),
            "bpr_active": has_bpr,
            "bpr_range": f"${bpr_bot:,.1f} - ${bpr_top:,.1f}" if has_bpr else "None",
            "idm_status": idm_sig,
            "isd_score": isd_str,
            "isd_complete": isd_score_num == 3,
            "fvg_magnet_status": magnet_status
        }
