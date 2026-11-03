"""
Engine #12: Kurtsmock Relative Volume (rVol) & Better-er Volume Engine
Implements:
- RVOL Ratio (Current Volume / 20-period SMA Volume)
- Minimum Volume Validation (Threshold > 300 contracts)
- vBuy & vSell intra-bar calculation
- vChurn = Volume / Range (Institutional Absorption)
- Climax Up / Climax Down & Climax+Churn Signals
"""

class RelativeVolumeEngine:
    def __init__(self, period=20, min_contracts=300):
        self.period = period
        self.min_contracts = min_contracts

    def analyze(self, candles):
        if len(candles) < self.period + 2:
            return {
                "rvol": 1.0,
                "current_volume": 0,
                "volume_status": "NORMAL",
                "meets_threshold": True,
                "better_volume_signal": "NONE",
                "vbuy_pct": 50.0
            }

        recent = candles[-self.period-1:-1]
        vols = [float(c.get('v', 0)) for c in recent]
        avg_vol = sum(vols) / len(vols) if vols else 1.0

        curr_vol = float(candles[-1].get('v', 0))
        rvol = round(curr_vol / avg_vol, 2) if avg_vol > 0 else 1.0

        # Kurtsmock Better-er Volume over last `period` candles
        v_buys = []
        v_sells = []
        v_churns = []
        
        for c in candles[-self.period:]:
            rng = max(c['h'] - c['l'], 0.0001)
            v = float(c.get('v', 0))
            vb = (c['c'] - c['l']) / rng * v
            vs = (c['h'] - c['c']) / rng * v
            churn = v / rng
            v_buys.append(vb)
            v_sells.append(vs)
            v_churns.append(churn)

        last_vb = v_buys[-1]
        last_vs = v_sells[-1]
        last_churn = v_churns[-1]
        total_v = last_vb + last_vs
        vbuy_pct = round((last_vb / total_v * 100), 1) if total_v > 0 else 50.0

        t_climax_up = last_vb >= max(v_buys)
        t_climax_dn = last_vs >= max(v_sells)
        t_churn = last_churn >= max(v_churns)

        bv_sig = "NORMAL VOLUME"
        if t_churn and (t_climax_up or t_climax_dn):
            bv_sig = f"CLIMAX {'UP' if t_climax_up else 'DOWN'} + CHURN (Ultra Institutional Absorption)"
        elif t_climax_up and last_vb > last_vs:
            bv_sig = "CLIMAX BUYING VOLUME (Aggressive Accumulation)"
        elif t_climax_dn and last_vs > last_vb:
            bv_sig = "CLIMAX SELLING VOLUME (Aggressive Distribution)"
        elif t_churn:
            bv_sig = "CHURN VOLUME (High Volume in Narrow Range - Hidden Reversal)"

        meets_threshold = curr_vol >= self.min_contracts

        return {
            "rvol": rvol,
            "current_volume": round(curr_vol, 1),
            "avg_volume": round(avg_vol, 1),
            "volume_status": f"{rvol}x RVOL ({bv_sig})",
            "better_volume_signal": bv_sig,
            "vbuy_pct": vbuy_pct,
            "meets_threshold": meets_threshold
        }
