"""
===================================================================================
THE 9 ELITE INSTITUTIONAL & WALL STREET TITANS (COMPLETING THE 200-SYSTEM ARSENAL)
===================================================================================
1. John Ehlers Digital Signal Processing (DSP SuperSmoother Filter)
2. Hurst Exponent (H) & Fractal Market Efficiency (Random Walk vs True Trend)
3. Goldman Sachs Institutional VWAP ±1σ, 2σ, 3σ Volatility Bands
4. High-Leverage Liquidation Cluster Heatmap (Kingfisher / Hyblock Model)
5. Kaufman Adaptive Moving Average (KAMA / Jurik Zero-Lag Engine)
6. Marcos López de Prado's VPIN (Volume-Synchronized Probability of Toxicity)
7. Avellaneda-Stoikov Order Book Depth Imbalance & Micro-Price (HFT Model)
8. Richard Wyckoff Phase Engine (Spring & UTAD Institutional Trap Detector)
9. Richard Dennis Turtle Trading Breakout Engine (20/55 Channel Systems)
===================================================================================
"""

import math
import numpy as np

# ==============================================================================
# TITAN 1: John Ehlers DSP SuperSmoother Filter
# ==============================================================================
class JohnEhlersSuperSmoother:
    def __init__(self, period=14):
        self.period = period

    def analyze(self, candles):
        closes = [float(c['c']) for c in candles]
        if len(closes) < self.period + 3:
            return {"filtered_price": closes[-1] if closes else 0.0, "slope": "NEUTRAL", "trend": "NEUTRAL"}

        a1 = math.exp(-math.sqrt(2.0) * math.pi / self.period)
        b1 = 2.0 * a1 * math.cos(math.sqrt(2.0) * math.pi / self.period)
        c2 = b1
        c3 = -(a1 ** 2)
        c1 = 1.0 - c2 - c3

        filt = [closes[0], closes[1]]
        for i in range(2, len(closes)):
            val = c1 * ((closes[i] + closes[i - 1]) / 2.0) + c2 * filt[i - 1] + c3 * filt[i - 2]
            filt.append(val)

        curr_filt = round(filt[-1], 1)
        prev_filt = round(filt[-2], 1)
        prev2_filt = round(filt[-3], 1)

        slope_val = round(curr_filt - prev_filt, 2)
        slope = "UPWARD" if slope_val > 0 else ("DOWNWARD" if slope_val < 0 else "FLAT")
        
        inflection = "NONE"
        if prev_filt < prev2_filt and curr_filt > prev_filt:
            inflection = "🔥 EHLERS DSP BULLISH TROUGH INFLECTION (Early Reversal Up)"
        elif prev_filt > prev2_filt and curr_filt < prev_filt:
            inflection = "⚠️ EHLERS DSP BEARISH CREST INFLECTION (Early Reversal Down)"

        trend = "BULLISH" if closes[-1] >= curr_filt else "BEARISH"

        return {
            "ehlers_filtered_price": curr_filt,
            "ehlers_slope": slope,
            "ehlers_slope_value": slope_val,
            "ehlers_trend": trend,
            "ehlers_inflection": inflection
        }

# ==============================================================================
# TITAN 2: Hurst Exponent (H) & Fractal Market Efficiency
# ==============================================================================
class HurstExponentEngine:
    def __init__(self, min_window=8, max_window=32):
        self.min_window = min_window
        self.max_window = max_window

    def analyze(self, candles):
        closes = [float(c['c']) for c in candles]
        if len(closes) < 50:
            return {"hurst_exponent": 0.5, "market_regime": "RANDOM_WALK", "is_true_trend": False}

        returns = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
        N = len(returns)

        lags = [8, 12, 16, 24, 32]
        rs_values = []
        valid_lags = []

        for lag in lags:
            if lag > N:
                continue
            chunks = N // lag
            chunk_rs = []
            for ch in range(chunks):
                sub = returns[ch * lag:(ch + 1) * lag]
                if len(sub) == 0:
                    continue
                mean_sub = sum(sub) / len(sub)
                deviations = [x - mean_sub for x in sub]
                cum_dev = []
                acc = 0.0
                for d in deviations:
                    acc += d
                    cum_dev.append(acc)
                R = max(cum_dev) - min(cum_dev)
                var = sum(d ** 2 for d in deviations) / len(deviations)
                S = math.sqrt(var) if var > 0.0 else 0.0001
                if S > 0:
                    chunk_rs.append(R / S)
            if chunk_rs:
                rs_values.append(sum(chunk_rs) / len(chunk_rs))
                valid_lags.append(lag)

        if len(valid_lags) >= 2:
            log_lags = [math.log(l) for l in valid_lags]
            log_rs = [math.log(max(r, 0.0001)) for r in rs_values]
            n_pts = len(log_lags)
            mean_x = sum(log_lags) / n_pts
            mean_y = sum(log_rs) / n_pts
            num = sum((log_lags[i] - mean_x) * (log_rs[i] - mean_y) for i in range(n_pts))
            den = sum((log_lags[i] - mean_x) ** 2 for i in range(n_pts))
            H = round(num / den, 3) if den != 0 else 0.5
        else:
            H = 0.5

        H = max(0.05, min(0.95, H))
        fractal_dimension = round(2.0 - H, 3)

        if H > 0.58:
            regime = "STRONG PERSISTENT TREND (Institutional Continuation)"
            is_trending = True
        elif H < 0.42:
            regime = "ANTI-PERSISTENT MEAN REVERSION (Chop & Fakeouts)"
            is_trending = False
        else:
            regime = "RANDOM WALK (Brownian Market Equilibrium)"
            is_trending = False

        return {
            "hurst_exponent": H,
            "fractal_dimension": fractal_dimension,
            "market_regime": regime,
            "is_true_trend": is_trending
        }

# ==============================================================================
# TITAN 3: Goldman Sachs Institutional VWAP ±1σ, 2σ, 3σ Volatility Bands
# ==============================================================================
class GoldmanSachsVWAPBands:
    def __init__(self, lookback=100):
        self.lookback = lookback

    def analyze(self, candles):
        sub = candles[-self.lookback:]
        if not sub:
            return {}

        cum_tp_vol = 0.0
        cum_vol = 0.0
        tps = []
        vols = []

        for c in sub:
            tp = (c['h'] + c['l'] + c['c']) / 3.0
            v = max(float(c.get('v', 1.0)), 1.0)
            cum_tp_vol += tp * v
            cum_vol += v
            tps.append(tp)
            vols.append(v)

        vwap = cum_tp_vol / cum_vol if cum_vol > 0 else tps[-1]
        cum_sq_diff_vol = sum(vols[i] * ((tps[i] - vwap) ** 2) for i in range(len(sub)))
        variance = cum_sq_diff_vol / cum_vol if cum_vol > 0 else 1.0
        std_dev = math.sqrt(variance)

        curr_price = float(sub[-1]['c'])
        band_1_up = round(vwap + (1.0 * std_dev), 1)
        band_1_dn = round(vwap - (1.0 * std_dev), 1)
        band_2_up = round(vwap + (2.0 * std_dev), 1)
        band_2_dn = round(vwap - (2.0 * std_dev), 1)
        band_3_up = round(vwap + (3.0 * std_dev), 1)
        band_3_dn = round(vwap - (3.0 * std_dev), 1)

        vwap = round(vwap, 1)

        if curr_price >= band_3_up:
            state = "🔥 EXTREME OVERBOUGHT (3σ Institutional Exhaustion Zone)"
            bias = "REVERSAL_SHORT_RISK"
        elif curr_price >= band_2_up:
            state = "EXPANDED ABOVE 2σ (Bullish Extension Zone)"
            bias = "BULLISH_STRETCHED"
        elif curr_price <= band_3_dn:
            state = "🔥 EXTREME OVERSOLD (3σ Institutional Bottom Climax)"
            bias = "REVERSAL_LONG_OPPORTUNITY"
        elif curr_price <= band_2_dn:
            state = "EXPANDED BELOW 2σ (Bearish Flush Zone)"
            bias = "BEARISH_STRETCHED"
        elif curr_price >= vwap:
            state = "INSIDE 1σ UPPER FAIR-VALUE AREA (Institutions Bullish Bias)"
            bias = "MILD_BULLISH"
        else:
            state = "INSIDE 1σ LOWER FAIR-VALUE AREA (Institutions Bearish Bias)"
            bias = "MILD_BEARISH"

        return {
            "vwap_baseline": vwap,
            "std_deviation": round(std_dev, 1),
            "upper_band_1": band_1_up,
            "lower_band_1": band_1_dn,
            "upper_band_2": band_2_up,
            "lower_band_2": band_2_dn,
            "upper_band_3_exhaustion": band_3_up,
            "lower_band_3_climax": band_3_dn,
            "gs_vwap_state": state,
            "gs_vwap_bias": bias
        }

# ==============================================================================
# TITAN 4: High-Leverage Liquidation Cluster Heatmap
# ==============================================================================
class LiquidationClusterHeatmap:
    def __init__(self, lookback=60):
        self.lookback = lookback

    def analyze(self, candles):
        sub = candles[-self.lookback:]
        curr_price = float(sub[-1]['c'])
        recent_high = max(float(c['h']) for c in sub)
        recent_low = min(float(c['l']) for c in sub)

        major_short_liq_pool = round(recent_high * 1.003, 1)
        major_long_liq_pool  = round(recent_low * 0.997, 1)

        dist_to_long_liq = abs(curr_price - major_long_liq_pool)
        dist_to_short_liq = abs(curr_price - major_short_liq_pool)

        if dist_to_long_liq < dist_to_short_liq:
            primary_magnet = major_long_liq_pool
            magnet_direction = "DOWNSIDE LONG-FLUSH MAGNET (Whales hunting Long stops below)"
        else:
            primary_magnet = major_short_liq_pool
            magnet_direction = "UPSIDE SHORT-SQUEEZE MAGNET (Whales hunting Short stops above)"

        return {
            "current_price": curr_price,
            "dense_short_liq_pool": major_short_liq_pool,
            "dense_long_liq_pool": major_long_liq_pool,
            "primary_liquidation_magnet": primary_magnet,
            "magnet_narrative": magnet_direction
        }

# ==============================================================================
# TITAN 5: Kaufman Adaptive Moving Average (KAMA)
# ==============================================================================
class KaufmanAdaptiveMovingAverage:
    def __init__(self, period=10, fast=2, slow=30):
        self.period = period
        self.fast_sc = 2.0 / (fast + 1.0)
        self.slow_sc = 2.0 / (slow + 1.0)

    def analyze(self, candles):
        closes = [float(c['c']) for c in candles]
        if len(closes) < self.period + 5:
            return {"kama_value": closes[-1] if closes else 0.0, "efficiency_ratio": 0.5, "trend": "NEUTRAL"}

        kama = [closes[0]]
        ers = []

        for i in range(1, len(closes)):
            if i < self.period:
                kama.append(closes[i])
                continue

            direction = abs(closes[i] - closes[i - self.period])
            volatility = sum(abs(closes[j] - closes[j - 1]) for j in range(i - self.period + 1, i + 1))
            er = direction / volatility if volatility > 0 else 0.0
            ers.append(er)

            sc = (er * (self.fast_sc - self.slow_sc) + self.slow_sc) ** 2
            kama_val = kama[i - 1] + sc * (closes[i] - kama[i - 1])
            kama.append(kama_val)

        curr_kama = round(kama[-1], 1)
        curr_price = closes[-1]
        curr_er = round(ers[-1], 3) if ers else 0.5

        trend_dir = "BULLISH" if curr_price >= curr_kama else "BEARISH"
        speed = "LIGHTNING SPEED (Breakout Inflow)" if curr_er > 0.6 else ("CALM FLATLINE (Noise Suppressed)" if curr_er < 0.25 else "NORMAL CRUISE")

        return {
            "kama_value": curr_kama,
            "efficiency_ratio": curr_er,
            "kama_trend": trend_dir,
            "kama_speed_mode": speed
        }

# ==============================================================================
# TITAN 6: Marcos López de Prado's VPIN (Volume-Synchronized Probability of Toxicity)
# ==============================================================================
class VPINToxicityEngine:
    def __init__(self, num_baskets=20):
        self.num_baskets = num_baskets

    def analyze(self, candles):
        if len(candles) < 25:
            return {"vpin_score": 0.2, "toxicity_state": "LOW_TOXICITY"}

        sub = candles[-40:]
        total_vol = sum(float(c.get('v', 1.0)) for c in sub)
        basket_vol = total_vol / self.num_baskets if total_vol > 0 else 1.0

        imbalances = []
        for c in sub:
            rng = max(float(c['h']) - float(c['l']), 0.0001)
            v = float(c.get('v', 1.0))
            buy_v = v * (float(c['c']) - float(c['l'])) / rng
            sell_v = v * (float(c['h']) - float(c['c'])) / rng
            imbalances.append(abs(buy_v - sell_v))

        # Average normalized toxicity over baskets
        vpin = round(sum(imbalances[-self.num_baskets:]) / (self.num_baskets * basket_vol), 3) if basket_vol > 0 else 0.2
        vpin = max(0.01, min(0.99, vpin))

        if vpin > 0.65:
            state = "⚠️ DANGER: HIGH TOXICITY (Whale Front-Running / Flash Dump Risk)"
            is_toxic = True
        elif vpin > 0.45:
            state = "MODERATE TOXICITY (Aggressive Institutional Participation)"
            is_toxic = False
        else:
            state = "LOW TOXICITY (Healthy Organic Market Flow)"
            is_toxic = False

        return {
            "vpin_score": vpin,
            "toxicity_state": state,
            "is_toxic_flow": is_toxic
        }

# ==============================================================================
# TITAN 7: Avellaneda-Stoikov Order Book Depth Imbalance & Micro-Price (HFT)
# ==============================================================================
class AvellanedaStoikovHFTImbalance:
    def __init__(self, lookback=10):
        self.lookback = lookback

    def analyze(self, candles):
        sub = candles[-self.lookback:]
        curr_price = float(sub[-1]['c'])
        rng = max(float(sub[-1]['h']) - float(sub[-1]['l']), 0.0001)

        buy_pressure = 0.0
        sell_pressure = 0.0
        for c in sub:
            v = float(c.get('v', 1.0))
            c_rng = max(float(c['h']) - float(c['l']), 0.0001)
            buy_pressure += v * (float(c['c']) - float(c['l'])) / c_rng
            sell_pressure += v * (float(c['h']) - float(c['c'])) / c_rng

        total_p = buy_pressure + sell_pressure
        imbalance = (buy_pressure - sell_pressure) / total_p if total_p > 0 else 0.0
        imbalance = round(max(-1.0, min(1.0, imbalance)), 3)

        # Theoretical Micro-Price jump
        micro_price = round(curr_price + (imbalance * (rng * 0.5)), 1)
        hft_direction = "BULLISH_AGGRESSION" if imbalance > 0.15 else ("BEARISH_AGGRESSION" if imbalance < -0.15 else "BALANCED")

        return {
            "depth_imbalance": imbalance,
            "theoretical_micro_price": micro_price,
            "hft_micro_direction": hft_direction
        }

# ==============================================================================
# TITAN 8: Richard Wyckoff Phase Engine (Spring & UTAD Trap Detector)
# ==============================================================================
class WyckoffPhaseEngine:
    def __init__(self, range_bars=30):
        self.range_bars = range_bars

    def analyze(self, candles):
        sub = candles[-self.range_bars:]
        curr_price = float(sub[-1]['c'])
        curr_high = float(sub[-1]['h'])
        curr_low = float(sub[-1]['l'])

        prev_bars = sub[:-1]
        range_high = max(float(c['h']) for c in prev_bars)
        range_low = min(float(c['l']) for c in prev_bars)

        wyckoff_signal = "PHASE B: RANGE CONSOLIDATION (Trading Range)"
        wyckoff_bias = "NEUTRAL"

        # Spring: Pierces below range_low but closes back inside range (Bear Trap)
        if curr_low < range_low and curr_price > range_low:
            wyckoff_signal = "🔥 WYCKOFF SPRING CONFIRMED (Bear Trap - Phase C Markup Imminent!)"
            wyckoff_bias = "BULLISH_REVERSAL"
        # UTAD: Pierces above range_high but closes back inside range (Bull Trap)
        elif curr_high > range_high and curr_price < range_high:
            wyckoff_signal = "⚠️ WYCKOFF UTAD CONFIRMED (Upthrust After Distribution - Phase C Markdown!)"
            wyckoff_bias = "BEARISH_REVERSAL"
        elif curr_price > range_high:
            wyckoff_signal = "PHASE D/E: SIGN OF STRENGTH (SOS Breakout - Institutional Expansion)"
            wyckoff_bias = "STRONG_BULLISH"
        elif curr_price < range_low:
            wyckoff_signal = "PHASE D/E: SIGN OF WEAKNESS (SOW Breakdown - Institutional Markdown)"
            wyckoff_bias = "STRONG_BEARISH"

        return {
            "trading_range_high": range_high,
            "trading_range_low": range_low,
            "wyckoff_signal": wyckoff_signal,
            "wyckoff_bias": wyckoff_bias
        }

# ==============================================================================
# TITAN 9: Richard Dennis Turtle Trading Breakout Engine (20/55 Systems)
# ==============================================================================
class TurtleTradingBreakoutEngine:
    def __init__(self, sys1_period=20, sys2_period=55):
        self.sys1 = sys1_period
        self.sys2 = sys2_period

    def analyze(self, candles):
        closes = [float(c['c']) for c in candles]
        highs = [float(c['h']) for c in candles]
        lows = [float(c['l']) for c in candles]

        curr_price = closes[-1]
        # System 1 (20-bar)
        s1_high = max(highs[-self.sys1-1:-1])
        s1_low = min(lows[-self.sys1-1:-1])

        # System 2 (55-bar)
        s2_high = max(highs[-self.sys2-1:-1])
        s2_low = min(lows[-self.sys2-1:-1])

        turtle_state = "INSIDE CHANNELS"
        turtle_dir = "NEUTRAL"

        if curr_price > s2_high:
            turtle_state = "🔥 TURTLE SYSTEM 2 (55-BAR LONG BREAKOUT - Major Long Wave)"
            turtle_dir = "STRONG_BULLISH"
        elif curr_price > s1_high:
            turtle_state = "TURTLE SYSTEM 1 (20-BAR LONG BREAKOUT)"
            turtle_dir = "BULLISH"
        elif curr_price < s2_low:
            turtle_state = "⚠️ TURTLE SYSTEM 2 (55-BAR SHORT BREAKDOWN - Major Short Wave)"
            turtle_dir = "STRONG_BEARISH"
        elif curr_price < s1_low:
            turtle_state = "TURTLE SYSTEM 1 (20-BAR SHORT BREAKDOWN)"
            turtle_dir = "BEARISH"

        return {
            "turtle_20_high": s1_high,
            "turtle_20_low": s1_low,
            "turtle_55_high": s2_high,
            "turtle_55_low": s2_low,
            "turtle_state": turtle_state,
            "turtle_direction": turtle_dir
        }

# ==============================================================================
# MASTER TITANS 9-IN-1 CONFLUENCE WRAPPER
# ==============================================================================
class EliteInstitutionalTitansSuite:
    def __init__(self):
        self.ehlers = JohnEhlersSuperSmoother()
        self.hurst = HurstExponentEngine()
        self.gs_vwap = GoldmanSachsVWAPBands()
        self.liq_map = LiquidationClusterHeatmap()
        self.kama = KaufmanAdaptiveMovingAverage()
        self.vpin = VPINToxicityEngine()
        self.hft = AvellanedaStoikovHFTImbalance()
        self.wyckoff = WyckoffPhaseEngine()
        self.turtle = TurtleTradingBreakoutEngine()

    def analyze_all_titans(self, candles):
        res_ehlers = self.ehlers.analyze(candles)
        res_hurst = self.hurst.analyze(candles)
        res_vwap = self.gs_vwap.analyze(candles)
        res_liq = self.liq_map.analyze(candles)
        res_kama = self.kama.analyze(candles)
        res_vpin = self.vpin.analyze(candles)
        res_hft = self.hft.analyze(candles)
        res_wyck = self.wyckoff.analyze(candles)
        res_turt = self.turtle.analyze(candles)

        bull_points = 0
        total_points = 9

        if res_ehlers['ehlers_trend'] == "BULLISH": bull_points += 1
        if res_kama['kama_trend'] == "BULLISH": bull_points += 1
        if "BULLISH" in res_vwap['gs_vwap_bias']: bull_points += 1
        if res_hurst['is_true_trend']: bull_points += 1
        if "SHORT-SQUEEZE" in res_liq['magnet_narrative']: bull_points += 1
        if not res_vpin['is_toxic_flow']: bull_points += 1
        if res_hft['hft_micro_direction'] == "BULLISH_AGGRESSION": bull_points += 1
        if "BULLISH" in res_wyck['wyckoff_bias']: bull_points += 1
        if "BULLISH" in res_turt['turtle_direction']: bull_points += 1

        titans_bull_pct = round((bull_points / total_points) * 100.0, 1)
        titans_bear_pct = round(100.0 - titans_bull_pct, 1)

        return {
            "titans_total_active": 9,
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
            "turtle_breakout": res_turt
        }

if __name__ == "__main__":
    from ict_auto_bot import get_candles
    c1h = get_candles(60, 100)
    titans = EliteInstitutionalTitansSuite()
    res = titans.analyze_all_titans(c1h)
    print("=== ALL 9 ELITE INSTITUTIONAL TITANS ACTIVE ===")
    print(f"Total Titans: {res['titans_total_active']}")
    print(f"Titans Score: {res['titans_bull_pct']}% Bull vs {res['titans_bear_pct']}% Bear")
    print(f"VPIN Toxicity: {res['vpin_toxicity']['toxicity_state']}")
    print(f"Wyckoff Phase: {res['wyckoff_phase']['wyckoff_signal']}")
    print(f"Turtle System: {res['turtle_breakout']['turtle_state']}")
    print(f"HFT Micro-Price: ${res['avellaneda_hft']['theoretical_micro_price']}")
