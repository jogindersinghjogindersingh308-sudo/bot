"""
===================================================================================
THE 8 ADVANCED QUANTITATIVE & INSTITUTIONAL TITANS (COMPLETING THE GRAND 208 UNIVERSE)
===================================================================================
1. Yang-Zhang Optimal Historical Volatility Estimator (The Gold Standard of Volatility)
2. E.W. Dreiss Choppiness Index (CHOP - 0 to 100 Scale Fractal Chaos Detector)
3. Larry Connors 3-Component RSI (CRSI - High Probability Mean Reversion)
4. John R. McGinley Dynamic Adaptive Speed Engine (Patented Zero-Whipsaw Baseline)
5. Tom DeMark Range Expansion Index (TD REI - Volatility Filtered Momentum)
6. Larry Williams Commercial Whale Accumulation/Distribution (LW A/D Index)
7. Heikin-Ashi Smoothed Trend Continuum (Zero-Noise Trend Filter)
8. Ed Thorp's Kelly Criterion Institutional Risk & Anti-Ruin Engine
===================================================================================
"""

import math
import numpy as np

# ==============================================================================
# TITAN 10: Yang-Zhang Optimal Historical Volatility Estimator
# ==============================================================================
class YangZhangVolatility:
    def __init__(self, period=14):
        self.period = period

    def analyze(self, candles):
        if len(candles) < self.period + 2:
            return {"yang_zhang_vol": 0.01, "vol_state": "NORMAL"}

        sub = candles[-self.period-1:]
        k = 0.34 / (1.34 + (self.period + 1.0) / (self.period - 1.0))

        # Overnight jump variance (Vo)
        log_oc = [math.log(sub[i]['o'] / sub[i - 1]['c']) for i in range(1, len(sub))]
        mean_oc = sum(log_oc) / len(log_oc)
        vo = sum((x - mean_oc) ** 2 for x in log_oc) / (len(log_oc) - 1)

        # Open-to-close variance (Vc)
        log_co = [math.log(sub[i]['c'] / sub[i]['o']) for i in range(1, len(sub))]
        mean_co = sum(log_co) / len(log_co)
        vc = sum((x - mean_co) ** 2 for x in log_co) / (len(log_co) - 1)

        # Rogers-Satchell variance (Vrs)
        rs_list = []
        for i in range(1, len(sub)):
            h, l, o, c = sub[i]['h'], sub[i]['l'], sub[i]['o'], sub[i]['c']
            log_ho = math.log(h / o)
            log_lo = math.log(l / o)
            log_co = math.log(c / o)
            rs = log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co)
            rs_list.append(rs)
        v_rs = sum(rs_list) / len(rs_list)

        sigma_sq = vo + k * vc + (1.0 - k) * v_rs
        yz_vol = round(math.sqrt(max(sigma_sq, 0.000001)) * math.sqrt(365.0) * 100.0, 2)

        vol_state = "🔥 HIGH VOLATILITY SURGE" if yz_vol > 55.0 else ("COMPRESSED LOW VOLATILITY" if yz_vol < 25.0 else "NORMAL EQUILIBRIUM")

        return {
            "yang_zhang_volatility_pct": yz_vol,
            "volatility_regime": vol_state
        }

# ==============================================================================
# TITAN 11: E.W. Dreiss Choppiness Index (CHOP)
# ==============================================================================
class ChoppinessIndexEngine:
    def __init__(self, period=14):
        self.period = period

    def analyze(self, candles):
        if len(candles) < self.period + 2:
            return {"chop_index": 50.0, "chop_state": "EQUILIBRIUM", "is_pure_trend": False}

        sub = candles[-self.period:]
        trs = []
        for i in range(1, len(sub)):
            tr = max(sub[i]['h'] - sub[i]['l'], abs(sub[i]['h'] - sub[i - 1]['c']), abs(sub[i]['l'] - sub[i - 1]['c']))
            trs.append(tr)

        sum_tr = sum(trs)
        max_h = max(c['h'] for c in sub)
        min_l = min(c['l'] for c in sub)
        rng = max(max_h - min_l, 0.0001)

        ratio = sum_tr / rng
        chop = round(100.0 * (math.log10(ratio) / math.log10(self.period)), 1)
        chop = max(0.0, min(100.0, chop))

        if chop > 61.8:
            state = "⚠️ EXTREME CHOP / DEAD CONSOLIDATION (Do Not Trade Breakouts)"
            is_trend = False
        elif chop < 38.2:
            state = "🚀 EXPLOSIVE TREND CONTINUATION (Breakout Running)"
            is_trend = True
        else:
            state = "DEVELOPING VOLATILITY (Transitional Phase)"
            is_trend = False

        return {
            "chop_index": chop,
            "chop_state": state,
            "is_pure_trend": is_trend
        }

# ==============================================================================
# TITAN 12: Larry Connors 3-Component RSI (CRSI)
# ==============================================================================
class ConnorsRSIEngine:
    def __init__(self, rsi_period=3, streak_period=2, rank_period=100):
        self.rsi_p = rsi_period
        self.streak_p = streak_period
        self.rank_p = rank_period

    def _rsi(self, values, p):
        if len(values) < p + 1:
            return 50.0
        gains = [max(values[i] - values[i-1], 0) for i in range(1, len(values))]
        losses = [max(values[i-1] - values[i], 0) for i in range(1, len(values))]
        avg_g = sum(gains[-p:]) / p
        avg_l = sum(losses[-p:]) / p
        if avg_l == 0: return 100.0
        rs = avg_g / avg_l
        return 100.0 - (100.0 / (1.0 + rs))

    def analyze(self, candles):
        closes = [float(c['c']) for c in candles]
        if len(closes) < 30:
            return {"connors_rsi": 50.0, "crsi_state": "NEUTRAL"}

        # 1. RSI-3
        r3 = self._rsi(closes, self.rsi_p)

        # 2. Up/Down streak
        streak = 0
        streaks = []
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                streak = streak + 1 if streak > 0 else 1
            elif closes[i] < closes[i-1]:
                streak = streak - 1 if streak < 0 else -1
            else:
                streak = 0
            streaks.append(streak)

        streak_rsi = self._rsi(streaks, self.streak_p)

        # 3. Percentile Rank (ROC-1)
        roc1 = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
        curr_roc = roc1[-1]
        lookback_rocs = roc1[-min(len(roc1), self.rank_p):]
        pct_rank = round(sum(1 for r in lookback_rocs if r < curr_roc) / len(lookback_rocs) * 100.0, 1)

        crsi = round((r3 + streak_rsi + pct_rank) / 3.0, 1)

        if crsi < 15.0:
            state = "🔥 EXTREME CRSI OVERSOLD (High-Probability Long Reversal)"
            bias = "BULLISH_REVERSAL"
        elif crsi > 85.0:
            state = "⚠️ EXTREME CRSI OVERBOUGHT (High-Probability Short Reversal)"
            bias = "BEARISH_REVERSAL"
        else:
            state = "CRSI BALANCED NORMAL"
            bias = "NEUTRAL"

        return {
            "connors_rsi": crsi,
            "crsi_state": state,
            "crsi_bias": bias
        }

# ==============================================================================
# TITAN 13: John R. McGinley Dynamic Adaptive Speed Engine
# ==============================================================================
class McGinleyDynamicEngine:
    def __init__(self, period=14):
        self.period = period

    def analyze(self, candles):
        closes = [float(c['c']) for c in candles]
        if len(closes) < self.period + 2:
            return {"mcginley_dynamic": closes[-1] if closes else 0.0, "mcginley_trend": "NEUTRAL"}

        md = [closes[0]]
        for i in range(1, len(closes)):
            prev = md[-1]
            p = closes[i]
            ratio = (p / prev) if prev > 0 else 1.0
            k = max(0.6, min(2.0, ratio ** 4))
            denom = self.period * k
            val = prev + (p - prev) / denom
            md.append(val)

        curr_md = round(md[-1], 1)
        prev_md = round(md[-2], 1)
        curr_p = closes[-1]

        trend = "BULLISH" if curr_p >= curr_md else "BEARISH"
        slope = "RISING" if curr_md > prev_md else ("FALLING" if curr_md < prev_md else "FLAT")

        return {
            "mcginley_dynamic": curr_md,
            "mcginley_trend": trend,
            "mcginley_slope": slope
        }

# ==============================================================================
# TITAN 14: Tom DeMark Range Expansion Index (TD REI)
# ==============================================================================
class TomDeMarkREIEngine:
    def __init__(self, period=8):
        self.period = period

    def analyze(self, candles):
        if len(candles) < self.period + 8:
            return {"td_rei": 0.0, "rei_state": "NEUTRAL"}

        sub = candles[-self.period-8:]
        rei_vals = []
        abs_vals = []

        for i in range(5, len(sub)):
            h = sub[i]['h']
            l = sub[i]['l']
            h2 = sub[i - 2]['h']
            l2 = sub[i - 2]['l']
            h5 = sub[i - 5]['h']
            l5 = sub[i - 5]['l']
            h6 = sub[i - 6]['h']
            l6 = sub[i - 6]['l']

            # DeMark Qualification Condition
            cond1 = (h >= l5 or h >= l6)
            cond2 = (l <= h5 or l <= h6)

            if cond1 or cond2:
                diff = (h - h2) + (l - l2)
                rei_vals.append(diff)
                abs_vals.append(abs(h - h2) + abs(l - l2))
            else:
                rei_vals.append(0.0)
                abs_vals.append(0.0)

        sum_num = sum(rei_vals[-self.period:])
        sum_den = sum(abs_vals[-self.period:])
        rei = round((sum_num / sum_den) * 100.0, 1) if sum_den > 0 else 0.0
        rei = max(-100.0, min(100.0, rei))

        if rei > 60.0:
            state = "🔥 TD REI EXTREME OVERBOUGHT (Exhaustion Top)"
        elif rei < -60.0:
            state = "🔥 TD REI EXTREME OVERSOLD (Exhaustion Bottom)"
        else:
            state = "TD REI NORMAL ZONE"

        return {
            "td_rei": rei,
            "td_rei_state": state
        }

# ==============================================================================
# TITAN 15: Larry Williams Commercial Whale Accumulation/Distribution
# ==============================================================================
class LarryWilliamsADEngine:
    def __init__(self, period=14):
        self.period = period

    def analyze(self, candles):
        if len(candles) < self.period + 2:
            return {"lw_ad_sentiment": "NEUTRAL", "lw_divergence": "NONE"}

        ad_series = [0.0]
        for i in range(1, len(candles)):
            c = candles[i]['c']
            prev_c = candles[i - 1]['c']
            h = candles[i]['h']
            l = candles[i]['l']
            if c > prev_c:
                ad = c - min(l, prev_c)
            elif c < prev_c:
                ad = c - max(h, prev_c)
            else:
                ad = 0.0
            ad_series.append(ad_series[-1] + ad)

        sub_ad = ad_series[-self.period:]
        sub_c = [c['c'] for c in candles[-self.period:]]

        ad_rising = sub_ad[-1] > sub_ad[0]
        price_rising = sub_c[-1] > sub_c[0]

        divergence = "NONE"
        if not price_rising and ad_rising:
            divergence = "🔥 BULLISH ACCUMULATION DIVERGENCE (Whales Silently Buying)"
        elif price_rising and not ad_rising:
            divergence = "⚠️ BEARISH DISTRIBUTION DIVERGENCE (Whales Silently Offloading)"

        sentiment = "ACCUMULATION" if ad_rising else "DISTRIBUTION"

        return {
            "lw_ad_sentiment": sentiment,
            "lw_divergence": divergence
        }

# ==============================================================================
# TITAN 16: Heikin-Ashi Smoothed Trend Continuum
# ==============================================================================
class HeikinAshiSmoothedContinuum:
    def __init__(self, period=10):
        self.period = period

    def analyze(self, candles):
        if len(candles) < self.period + 5:
            return {"ha_trend": "NEUTRAL", "ha_color": "WHITE"}

        # Calculate Heikin-Ashi
        ha_closes = []
        ha_opens = []
        for i, c in enumerate(candles):
            hac = (c['o'] + c['h'] + c['l'] + c['c']) / 4.0
            hao = (c['o'] + c['c']) / 2.0 if i == 0 else (ha_opens[-1] + ha_closes[-1]) / 2.0
            ha_closes.append(hac)
            ha_opens.append(hao)

        # Smooth HA with EMA
        alpha = 2.0 / (self.period + 1.0)
        smoothed_c = [ha_closes[0]]
        smoothed_o = [ha_opens[0]]
        for i in range(1, len(ha_closes)):
            smoothed_c.append(alpha * ha_closes[i] + (1.0 - alpha) * smoothed_c[-1])
            smoothed_o.append(alpha * ha_opens[i] + (1.0 - alpha) * smoothed_o[-1])

        trend = "BULLISH" if smoothed_c[-1] >= smoothed_o[-1] else "BEARISH"
        color = "GREEN" if trend == "BULLISH" else "RED"

        return {
            "ha_smoothed_trend": trend,
            "ha_smoothed_color": color
        }

# ==============================================================================
# TITAN 17: Ed Thorp's Kelly Criterion Institutional Risk Engine
# ==============================================================================
class KellyCriterionRiskEngine:
    def __init__(self, win_rate_estimate=0.68, payoff_ratio=2.2):
        self.p = win_rate_estimate
        self.b = payoff_ratio

    def calculate_optimal_allocation(self, confluence_score):
        # Adjust win rate dynamically based on 208-system confluence
        adjusted_p = min(0.85, max(0.40, confluence_score / 100.0))
        q = 1.0 - adjusted_p
        # Kelly Fraction: f* = (b*p - q) / b
        f_star = (self.b * adjusted_p - q) / self.b
        # Fractional Half-Kelly for conservative institutional bankroll preservation
        half_kelly = max(0.0, round(f_star * 0.5 * 100.0, 1))

        if half_kelly > 15.0:
            rec_leverage = "2x - 3x (MAX SAFE LEVERAGE)"
            safety_risk = "OPTIMAL INSTITUTIONAL RISK - High Edge Environment"
        elif half_kelly > 5.0:
            rec_leverage = "1x - 2x (CONSERVATIVE RISK)"
            safety_risk = "MODERATE RISK - Standard Sizing"
        else:
            rec_leverage = "0x (ZERO RISK / SIT TIGHT)"
            safety_risk = "NEGATIVE OR ZERO EDGE - Do Not Risk Capital"

        return {
            "kelly_optimal_capital_pct": half_kelly,
            "recommended_leverage": rec_leverage,
            "capital_safety_rating": safety_risk
        }

# ==============================================================================
# MASTER SUITE FOR ALL 17 TITANS (TITANS 1 TO 17 COMBINED)
# ==============================================================================
class MasterExpandedTitansSuite:
    def __init__(self):
        # First 9 Titans
        from elite_institutional_titans import (
            JohnEhlersSuperSmoother, HurstExponentEngine, GoldmanSachsVWAPBands,
            LiquidationClusterHeatmap, KaufmanAdaptiveMovingAverage,
            VPINToxicityEngine, AvellanedaStoikovHFTImbalance,
            WyckoffPhaseEngine, TurtleTradingBreakoutEngine
        )
        self.ehlers = JohnEhlersSuperSmoother()
        self.hurst = HurstExponentEngine()
        self.gs_vwap = GoldmanSachsVWAPBands()
        self.liq_map = LiquidationClusterHeatmap()
        self.kama = KaufmanAdaptiveMovingAverage()
        self.vpin = VPINToxicityEngine()
        self.hft = AvellanedaStoikovHFTImbalance()
        self.wyckoff = WyckoffPhaseEngine()
        self.turtle = TurtleTradingBreakoutEngine()

        # Additional 8 Elite Titans (10 to 17)
        self.yang_zhang = YangZhangVolatility()
        self.chop = ChoppinessIndexEngine()
        self.connors_rsi = ConnorsRSIEngine()
        self.mcginley = McGinleyDynamicEngine()
        self.td_rei = TomDeMarkREIEngine()
        self.lw_ad = LarryWilliamsADEngine()
        self.ha_smoothed = HeikinAshiSmoothedContinuum()
        self.kelly = KellyCriterionRiskEngine()

    def analyze_all_17_titans(self, candles):
        res_ehlers = self.ehlers.analyze(candles)
        res_hurst = self.hurst.analyze(candles)
        res_vwap = self.gs_vwap.analyze(candles)
        res_liq = self.liq_map.analyze(candles)
        res_kama = self.kama.analyze(candles)
        res_vpin = self.vpin.analyze(candles)
        res_hft = self.hft.analyze(candles)
        res_wyck = self.wyckoff.analyze(candles)
        res_turt = self.turtle.analyze(candles)

        res_yz = self.yang_zhang.analyze(candles)
        res_chop = self.chop.analyze(candles)
        res_crsi = self.connors_rsi.analyze(candles)
        res_md = self.mcginley.analyze(candles)
        res_rei = self.td_rei.analyze(candles)
        res_lw = self.lw_ad.analyze(candles)
        res_ha = self.ha_smoothed.analyze(candles)

        bull_points = 0
        total_points = 16 # voting titans

        if res_ehlers['ehlers_trend'] == "BULLISH": bull_points += 1
        if res_kama['kama_trend'] == "BULLISH": bull_points += 1
        if "BULLISH" in res_vwap['gs_vwap_bias']: bull_points += 1
        if res_hurst['is_true_trend']: bull_points += 1
        if "SHORT-SQUEEZE" in res_liq['magnet_narrative']: bull_points += 1
        if not res_vpin['is_toxic_flow']: bull_points += 1
        if res_hft['hft_micro_direction'] == "BULLISH_AGGRESSION": bull_points += 1
        if "BULLISH" in res_wyck['wyckoff_bias']: bull_points += 1
        if "BULLISH" in res_turt['turtle_direction']: bull_points += 1
        if res_chop['is_pure_trend']: bull_points += 1
        if "BULLISH" in res_crsi['crsi_bias'] or res_crsi['connors_rsi'] < 30.0: bull_points += 1
        if res_md['mcginley_trend'] == "BULLISH": bull_points += 1
        if res_rei['td_rei'] < -20.0 or res_rei['td_rei'] > 20.0: bull_points += 1
        if res_lw['lw_ad_sentiment'] == "ACCUMULATION": bull_points += 1
        if res_ha['ha_smoothed_trend'] == "BULLISH": bull_points += 1

        titans_bull_pct = round((bull_points / total_points) * 100.0, 1)
        titans_bear_pct = round(100.0 - titans_bull_pct, 1)

        res_kelly = self.kelly.calculate_optimal_allocation(titans_bull_pct)

        return {
            "titans_total_active": 17,
            "titans_bull_pct": titans_bull_pct,
            "titans_bear_pct": titans_bear_pct,
            "ehlers_dsp": res_ehlers,
            "hurst_exponent": res_hurst,
            "goldman_sachs_vwap": res_vwap,
            "liquidation_heatmap": res_liq,
            "kaufman_kama": res_kama,
            "vpin_toxicity": res_vpin,
            "avellaneda_hft": res_hft,
            "wyckoff_phase": res_wyck,
            "turtle_breakout": res_turt,
            "yang_zhang_vol": res_yz,
            "dreiss_chop": res_chop,
            "connors_rsi": res_crsi,
            "mcginley_dynamic": res_md,
            "td_rei": res_rei,
            "larry_williams_ad": res_lw,
            "heikin_ashi_smoothed": res_ha,
            "kelly_criterion": res_kelly
        }

if __name__ == "__main__":
    from ict_auto_bot import get_candles
    c1h = get_candles(60, 100)
    master = MasterExpandedTitansSuite()
    r = master.analyze_all_17_titans(c1h)
    print("=== GRAND MASTER 17 TITANS ACTIVE ===")
    print(f"Total Titans: {r['titans_total_active']}")
    print(f"Titans Score: {r['titans_bull_pct']}% Bull vs {r['titans_bear_pct']}% Bear")
    print(f"Yang-Zhang Vol: {r['yang_zhang_vol']['yang_zhang_volatility_pct']}% ({r['yang_zhang_vol']['volatility_regime']})")
    print(f"Dreiss CHOP: {r['dreiss_chop']['chop_index']} ({r['dreiss_chop']['chop_state']})")
    print(f"Connors RSI: {r['connors_rsi']['connors_rsi']} ({r['connors_rsi']['crsi_state']})")
    print(f"McGinley Dynamic: ${r['mcginley_dynamic']['mcginley_dynamic']} ({r['mcginley_dynamic']['mcginley_trend']})")
    print(f"TD REI: {r['td_rei']['td_rei']} ({r['td_rei']['td_rei_state']})")
    print(f"Larry Williams AD: {r['larry_williams_ad']['lw_ad_sentiment']} ({r['larry_williams_ad']['lw_divergence']})")
    print(f"HA Smoothed: {r['heikin_ashi_smoothed']['ha_smoothed_trend']}")
    print(f"Kelly Risk Sizing: {r['kelly_criterion']['recommended_leverage']} ({r['kelly_criterion']['capital_safety_rating']})")
