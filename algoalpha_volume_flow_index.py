"""
Engine #25: AlgoAlpha Volume Flow Index (VFI) Engine (Official Formula Port)
Implements:
- Katsanos & AlgoAlpha Institutional Volume Flow Index:
  * Logarithmic Typical Price Variation (HLC3)
  * Standard Deviation Inter-bar Cutoff Filter (Eliminates Retail Noise)
  * Capped Volume (2.5x Volume Ceiling)
  * Directional Money Flow (MF) Summation
  * VFI Oscillator & VFI Signal Line (3-period EMA)
- Whale Accumulation (+VFI Inflow) vs Whale Distribution (-VFI Outflow)
"""
import math

class AlgoAlphaVolumeFlowIndex:
    def __init__(self, period=50, coef=0.2, v_coef=2.5, signal_len=3):
        self.period = period
        self.coef = coef
        self.v_coef = v_coef
        self.signal_len = signal_len

    def analyze(self, candles):
        if len(candles) < self.period + 5:
            return {
                "vfi": 0.0,
                "vfi_signal": 0.0,
                "status": "NEUTRAL",
                "whale_flow": "BALANCED"
            }

        typicals = [(c['h'] + c['l'] + c['c']) / 3.0 for c in candles]
        volumes = [float(c.get('v', 0)) for c in candles]

        # Calculate inter-bar log returns
        inter = []
        for i in range(1, len(typicals)):
            t_curr = typicals[i]
            t_prev = typicals[i - 1]
            inter.append(math.log(t_curr) - math.log(t_prev) if t_prev > 0 and t_curr > 0 else 0.0)

        # Standard deviation of inter
        sub_inter = inter[-self.period:]
        mean_inter = sum(sub_inter) / len(sub_inter) if sub_inter else 0.0
        var_inter = sum((x - mean_inter) ** 2 for x in sub_inter) / len(sub_inter) if sub_inter else 0.0
        vinter = math.sqrt(var_inter)

        cutoff = self.coef * vinter * candles[-1]['c']

        # Volume moving average
        sub_vols = volumes[-self.period:]
        vave = sum(sub_vols) / len(sub_vols) if sub_vols else 1.0
        vmax = self.v_coef * vave

        # Directional Money Flow over the period
        mf_sum = 0.0
        vfi_series = []

        start_i = max(1, len(candles) - self.period - 10)
        for i in range(start_i, len(candles)):
            diff = typicals[i] - typicals[i - 1]
            vol_capped = min(volumes[i], vmax)

            if diff > cutoff:
                mf = vol_capped
            elif diff < -cutoff:
                mf = -vol_capped
            else:
                mf = 0.0

            mf_sum += mf
            vfi_val = mf_sum / vave if vave > 0 else 0.0
            vfi_series.append(vfi_val)

        curr_vfi = round(vfi_series[-1], 2) if vfi_series else 0.0
        prev_vfi = round(vfi_series[-2], 2) if len(vfi_series) >= 2 else curr_vfi

        # 3-period EMA signal line
        k = 2.0 / (self.signal_len + 1.0)
        vfi_signal = curr_vfi * k + prev_vfi * (1.0 - k)
        vfi_signal = round(vfi_signal, 2)

        if curr_vfi > 0 and curr_vfi > vfi_signal:
            status = f"🟢 STRONG WHALE INFLOW (+{curr_vfi} VFI)"
            whale_flow = "INSTITUTIONAL ACCUMULATION"
        elif curr_vfi < 0 and curr_vfi < vfi_signal:
            status = f"🔴 STRONG WHALE OUTFLOW ({curr_vfi} VFI)"
            whale_flow = "INSTITUTIONAL DISTRIBUTION"
        elif curr_vfi > 0:
            status = f"🟢 MILD POSITIVE FLOW (+{curr_vfi} VFI)"
            whale_flow = "BULLISH BIAS"
        else:
            status = f"🔴 MILD NEGATIVE FLOW ({curr_vfi} VFI)"
            whale_flow = "BEARISH BIAS"

        return {
            "vfi": curr_vfi,
            "vfi_signal": vfi_signal,
            "status": status,
            "whale_flow": whale_flow
        }
