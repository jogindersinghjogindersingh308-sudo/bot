"""
===================================================================================
SUPREME UNIVERSAL INSTITUTIONAL MASTER ALGORITHM (THE UNBEATABLE 200-SYSTEM CORE)
===================================================================================
Combines:
- 26 Core Institutional Engines (LuxAlgo SMC, Anchored VWAP, Order Flow CVD, DQS Displacement, etc.)
- 15 VIP Commercial Systems (Carter Squeeze Pro, VuManChu Cipher B, UT Bot Alerts, TD 9/13, Lorentzian ML, etc.)
- 150 Omni-Quant Technical Indicators Universe
- Universal Multi-Timeframe Engine (1m, 3m, 5m, 15m, 30m, 1H, 4H, Daily)
- Deep Institutional Big Players Footprint (Whale VFI, CVD Delta, Stop-Hunt Liquidity Sweeps)
- Real-Time Chart Marking Generator for Delta Exchange Platform
===================================================================================
"""

import sys
import os
import json
import time
import math
import datetime
import urllib.request
import urllib.error

# sys.path handled locally

from ict_auto_bot import (
    get_candles, LuxAlgoSMC, AlgoAlphaBreakoutChannels, AlgoAlphaTrendTargets,
    LuxAlgoVolumeProfile, AnchoredVWAP, HarmonicFibonacciEngine, LuxAlgoElliottWave,
    LiquiditySweepsEngine, MarketCipherBEngine, ICTDisplacementEngine, ICTKillZonesEngine,
    RelativeVolumeEngine, ICTFVGVoidEngine, NadarayaWatsonEnvelopeEngine, DynamicSRHeatmap,
    DeltaFundingOIEngine, LuxAlgoReversalEngine, MTFTrendAlignmentEngine, LuxAlgoOrderFlow,
    MarketCipherAEngine, RipsterCloudsEngine, ZeiiermanKalmanEngine, WaddahAttarExplosionEngine,
    AlgoAlphaVolumeFlowIndex, HighWatermarkProfitEngine, quant_suite, vip_suite
)
from predictive_forecast_engine import PredictiveForecastEngine
from extended_master_titans import MasterExpandedTitansSuite
from daviddme_kill_switch_guard import DavidDMEKillSwitchGuard
from liquidation_heatmap_engine import LiquidationHeatmapEngine
from trader_timemachine_engine import TraderTimeMachineEngine
from ultimate_global_quant_universe import UltimateGlobalQuantUniverse
from infinite_frontier_quant_titans import InfiniteFrontierQuantTitans

class SupremeUniversalAlgo:
    def __init__(self):
        # 1-8 Core Technical Engines
        self.lux_smc = LuxAlgoSMC()
        self.algo_chan = AlgoAlphaBreakoutChannels(norm_length=100, box_length=14, strong=True)
        self.algo_targets = AlgoAlphaTrendTargets()
        self.vp_engine = LuxAlgoVolumeProfile(lookback=200, row_size=100)
        self.vwap_engine = AnchoredVWAP(use_ohlc4=True)
        self.hf_engine = HarmonicFibonacciEngine()
        self.ew_engine = LuxAlgoElliottWave()
        self.lq_engine = LiquiditySweepsEngine()

        # 9-24 Institutional Engines
        self.mc_engine = MarketCipherBEngine()
        self.disp_engine = ICTDisplacementEngine()
        self.kz_engine = ICTKillZonesEngine()
        self.rvol_engine = RelativeVolumeEngine(min_contracts=300)
        self.fvg_engine = ICTFVGVoidEngine()
        self.nwe_engine = NadarayaWatsonEnvelopeEngine()
        self.sr_heatmap = DynamicSRHeatmap()
        self.delta_oi = DeltaFundingOIEngine()
        self.rev_engine = LuxAlgoReversalEngine()
        self.mtf_engine = MTFTrendAlignmentEngine()
        self.of_engine = LuxAlgoOrderFlow()
        self.mca_engine = MarketCipherAEngine()
        self.rip_engine = RipsterCloudsEngine()
        self.zk_engine = ZeiiermanKalmanEngine()
        self.wae_engine = WaddahAttarExplosionEngine()
        self.vfi_engine = AlgoAlphaVolumeFlowIndex()
        self.profit_trail = HighWatermarkProfitEngine()
        self.pred_engine = PredictiveForecastEngine()

        # Suites (Total 301 Systems Grand Universe: 150 Quant + 50 Frontier + 40 Global + 26 Core + 17 Titans + 15 VIP + 3 Claude)
        self.quant_suite = quant_suite
        self.vip_suite = vip_suite
        self.titans_suite = MasterExpandedTitansSuite()
        self.ks_guard = DavidDMEKillSwitchGuard()
        self.liq_heatmap = LiquidationHeatmapEngine()
        self.time_machine = TraderTimeMachineEngine()
        self.global_quant_universe = UltimateGlobalQuantUniverse()
        self.frontier_titans = InfiniteFrontierQuantTitans()

    def analyze_market(self, timeframe=60):
        """
        Universal Multi-Timeframe Analysis:
        Accepts any timeframe: 1, 3, 5, 15, 30, 60, 240, 'D'
        Synthesizes chosen timeframe with Higher Timeframes (1H, 4H, Daily) to obey Big Players.
        """
        tf_str = str(timeframe).upper()
        
        # 1. Fetch Multiframe Candles from Delta Exchange Live API
        c_daily = get_candles('D', 40)
        c_4h = get_candles(240, 80)
        c_1h = get_candles(60, 200)
        
        # User requested timeframe candles
        if tf_str in ['60', '1H']:
            c_target = c_1h
        elif tf_str in ['240', '4H']:
            c_target = c_4h
        elif tf_str in ['D', '1D', 'DAILY']:
            c_target = c_daily
        else:
            try:
                res_num = int(tf_str.replace('M', ''))
            except Exception:
                res_num = 15
            c_target = get_candles(res_num, 150)

        curr_price = float(c_target[-1]['c'])

        # 2. Big Players Core Tracking (Order Flow CVD & Whales VFI)
        of_res = self.of_engine.analyze(c_1h)
        vfi_res = self.vfi_engine.analyze(c_1h)
        disp_res = self.disp_engine.analyze(c_1h)
        lq_res = self.lq_engine.analyze(c_1h)
        oi_res = self.delta_oi.analyze()
        
        cvd_val = float(of_res.get('cvd_value', 0.0))
        cvd_sentiment = of_res.get('delta_sentiment', 'NEUTRAL')
        is_whale_inflow = "BULLISH" in str(vfi_res.get('whale_flow', '')).upper()
        dqs_score = float(disp_res.get('dqs_score', 0.0))

        # 3. Target Timeframe SMC & Algos
        smc_target = self.lux_smc.analyze(c_target)
        smc_1h = self.lux_smc.analyze(c_1h)
        algo_1h = self.algo_chan.analyze(c_1h)
        targets_1h = self.algo_targets.analyze(c_1h)
        vp_target = self.vp_engine.analyze(c_target)
        vwap_target = self.vwap_engine.analyze(c_target)
        hf_target = self.hf_engine.analyze(c_target)
        ew_target = self.ew_engine.analyze(c_target)
        kz_res = self.kz_engine.analyze(c_1h)
        rvol_res = self.rvol_engine.analyze(c_1h)
        fvg_res = self.fvg_engine.analyze(c_1h)
        nwe_res = self.nwe_engine.analyze(c_1h)
        sr_res = self.sr_heatmap.analyze(c_1h)
        rev_res = self.rev_engine.analyze(c_1h)
        mtf_res = self.mtf_engine.analyze(c_daily, c_4h, c_1h, c_target)
        mca_res = self.mca_engine.analyze(c_1h)
        rip_res = self.rip_engine.analyze(c_1h)
        zk_res = self.zk_engine.analyze(c_1h)
        wae_res = self.wae_engine.analyze(c_1h)
        mc_res = self.mc_engine.analyze(c_1h)
        
        # 4. VIP Commercial 15 Systems, 150 Quant Universe & 17 Wall Street Titans
        vip_target = self.vip_suite.analyze_all_vip_algos(c_target)
        vip_1h = self.vip_suite.analyze_all_vip_algos(c_1h)
        quant_target = self.quant_suite.analyze_full_universe(c_target)
        titans_target = self.titans_suite.analyze_all_17_titans(c_target)
        
        # Squeeze Pro Check on Target & 4H
        sq_target = vip_target['squeeze_pro']
        sq_4h = self.vip_suite.analyze_all_vip_algos(c_4h)['squeeze_pro']

        # 5. Core 26 Predictive AI Synthesis (ALL ENGINES CONNECTED)
        engine_context = {
            "smc_1h": smc_1h,
            "smc_15m": smc_target,
            "algo_1h": algo_1h,
            "targets_1h": targets_1h,
            "vp_1h": vp_target,
            "vwap_res": vwap_target,
            "hf_res": hf_target,
            "ew_res": ew_target,
            "lq_res": lq_res,
            "mc_res": mc_res,
            "disp_res": disp_res,
            "kz_res": kz_res,
            "rvol_res": rvol_res,
            "fvg_res": fvg_res,
            "nwe_res": nwe_res,
            "sr_res": sr_res,
            "oi_res": oi_res,
            "rev_res": rev_res,
            "mtf_res": mtf_res,
            "of_res": of_res,
            "mca_res": mca_res,
            "rip_res": rip_res,
            "zk_res": zk_res,
            "wae_res": wae_res,
            "vfi_res": vfi_res,
            "quant_res": quant_target,
            "vip_res": vip_target,
            "titans_res": titans_target
        }
        pred_res = self.pred_engine.analyze(c_1h, c_target, engine_context=engine_context)

        # 6. Big Players Synthesis (ਵੱਡੇ ਪਲੇਅਰਾਂ ਦਾ ਹਿਸਾਬ)
        # Big players rule: If CVD is deeply negative (< -100k) and DQS Bearish, Big Players are dumping/flushing.
        # Do not allow early retail buy signals without absorption confirmation.
        big_players_mode = "NEUTRAL"
        if cvd_val < -100000 and "SELLERS" in cvd_sentiment:
            big_players_mode = "INSTITUTIONAL LIQUIDATION FLUSH (ਵੱਡੇ ਪਲੇਅਰ ਵੇਚ ਰਹੇ ਹਨ)"
            institutional_bias = "BEARISH_PRESSURE"
        elif cvd_val > 100000 and "BUYERS" in cvd_sentiment:
            big_players_mode = "INSTITUTIONAL ACCUMULATION (ਵੱਡੇ ਪਲੇਅਰ ਮਾਲ ਚੁੱਕ ਰਹੇ ਹਨ)"
            institutional_bias = "BULLISH_PRESSURE"
        else:
            big_players_mode = "MANIPULATION / CHOP RANGE (ਜਾਲ ਵਿਛਾਇਆ ਹੋਇਆ ਹੈ)"
            institutional_bias = "EQUILIBRIUM"

        # 7. Generate Master Chart Marking Lines for Delta Exchange
        poc = float(vp_target.get('poc', curr_price))
        vah = float(vp_target.get('vah', curr_price * 1.01))
        val = float(vp_target.get('val', curr_price * 0.99))
        d_vwap = float(vwap_target.get('daily_avwap', curr_price))
        w_vwap = float(vwap_target.get('weekly_avwap', curr_price))

        pdh = float(c_daily[-2]['h'])
        pdl = float(c_daily[-2]['l'])
        eq_50 = round((pdh + pdl) / 2.0, 1)

        bsl = float(lq_res.get('nearest_bsl_pool', pdh))
        ssl = float(lq_res.get('nearest_ssl_pool', pdl))

        # Dynamic Targets
        tp1_up = round(curr_price + (pdh - pdl) * 0.382, 1)
        tp2_up = round(curr_price + (pdh - pdl) * 0.618, 1)
        tp1_down = round(curr_price - (pdh - pdl) * 0.382, 1)
        tp2_down = round(curr_price - (pdh - pdl) * 0.618, 1)

        chart_marking_lines = [
            {"label": "PDH (Previous Day High)", "price": pdh, "color": "#e0a96d", "style": "solid", "type": "MAJOR_RESISTANCE"},
            {"label": "PDL (Previous Day Low)", "price": pdl, "color": "#e0a96d", "style": "solid", "type": "MAJOR_SUPPORT"},
            {"label": "50% Daily Equilibrium", "price": eq_50, "color": "#ffffff", "style": "dashed", "type": "EQUILIBRIUM"},
            {"label": "Volume Profile POC", "price": poc, "color": "#ff0055", "style": "bold_solid", "type": "HEAVY_VOLUME_NODE"},
            {"label": "Value Area High (VAH)", "price": vah, "color": "#f59e0b", "style": "dashed", "type": "RANGE_HIGH"},
            {"label": "Value Area Low (VAL)", "price": val, "color": "#10b981", "style": "dashed", "type": "RANGE_LOW"},
            {"label": "Daily Anchored VWAP", "price": d_vwap, "color": "#00e5ff", "style": "solid", "type": "INSTITUTIONAL_AVG"},
            {"label": "Weekly Institutional VWAP", "price": w_vwap, "color": "#d500f9", "style": "bold_solid", "type": "MACRO_BASELINE"},
            {"label": "Buy-Side Liquidity (BSL)", "price": bsl, "color": "#ef4444", "style": "dashed", "type": "STOP_HUNT_TARGET"},
            {"label": "Sell-Side Liquidity (SSL)", "price": ssl, "color": "#22c55e", "style": "dashed", "type": "STOP_HUNT_TARGET"},
        ]

        # Add Goldman Sachs VWAP Volatility Bands, Liquidation Magnet Lines & McGinley Dynamic
        gs_vwap = titans_target['goldman_sachs_vwap']
        liq_data = titans_target['liquidation_heatmap']
        # Claude Quant Systems #209, #210, #211
        liq_hm = self.liq_heatmap.calculate_heatmap(c_1h, curr_price)
        ks_eval = self.ks_guard.evaluate_kill_switch(None, curr_price, c_1h[-1] if c_1h else None)

        chart_marking_lines.extend([
            {"label": "GS VWAP +1σ Band", "price": gs_vwap['upper_band_1'], "color": "#38bdf8", "style": "dashed", "type": "VOLATILITY_BAND"},
            {"label": "GS VWAP -1σ Band", "price": gs_vwap['lower_band_1'], "color": "#38bdf8", "style": "dashed", "type": "VOLATILITY_BAND"},
            {"label": "GS VWAP +2σ Band", "price": gs_vwap['upper_band_2'], "color": "#f97316", "style": "dashed", "type": "EXPANSION_BAND"},
            {"label": "GS VWAP -2σ Band", "price": gs_vwap['lower_band_2'], "color": "#f97316", "style": "dashed", "type": "EXPANSION_BAND"},
            {"label": "GS VWAP +3σ Exhaustion", "price": gs_vwap['upper_band_3_exhaustion'], "color": "#ef4444", "style": "bold_solid", "type": "REVERSAL_ZONE"},
            {"label": "GS VWAP -3σ Climax", "price": gs_vwap['lower_band_3_climax'], "color": "#22c55e", "style": "bold_solid", "type": "CLIMAX_ZONE"},
            {"label": f"Whale Liq Magnet ({liq_hm['whale_magnet_direction'][:14]})", "price": liq_hm['primary_magnet_target'], "color": "#ff007f", "style": "bold_solid", "type": "LIQUIDATION_MAGNET"},
            {"label": "McGinley Dynamic Baseline", "price": titans_target['mcginley_dynamic']['mcginley_dynamic'], "color": "#a855f7", "style": "solid", "type": "ADAPTIVE_BASELINE"}
        ])

        # Order Blocks for Visual Box Drawing
        order_blocks = []
        if smc_target.get('bullish_order_block'):
            bob = smc_target['bullish_order_block']
            order_blocks.append({
                "type": "BULLISH_ORDER_BLOCK",
                "top": float(bob.get('top', 0)),
                "bottom": float(bob.get('bottom', 0)),
                "color": "rgba(34, 197, 94, 0.25)",
                "border": "#22c55e"
            })
        if smc_target.get('bearish_order_block'):
            sob = smc_target['bearish_order_block']
            order_blocks.append({
                "type": "BEARISH_ORDER_BLOCK",
                "top": float(sob.get('top', 0)),
                "bottom": float(sob.get('bottom', 0)),
                "color": "rgba(239, 68, 68, 0.25)",
                "border": "#ef4444"
            })

        # Master Confluence Agreement (301 Complete Sovereign Global Systems Universe)
        global_quant_res = self.global_quant_universe.analyze_40_global_algos(c_1h, curr_price)
        frontier_res = self.frontier_titans.analyze_50_frontier_titans(c_1h, curr_price)
        quant_bull = float(quant_target.get('omni_bullish_consensus_pct', 50.0))
        vip_bull = float(vip_target.get('vip_bull_pct', 50.0))
        pred_bull = float(pred_res.get('bull_confidence_pct', 50.0))
        titans_bull = float(titans_target.get('titans_bull_pct', 50.0))
        global_bull = float(global_quant_res.get('global_bull_pct', 50.0))
        frontier_bull = float(frontier_res.get('frontier_bull_pct', 50.0))

        master_bull_score = round((quant_bull * 0.20) + (frontier_bull * 0.20) + (global_bull * 0.20) + (vip_bull * 0.15) + (titans_bull * 0.15) + (pred_bull * 0.10), 1)
        master_bear_score = round(100.0 - master_bull_score, 1)

        kelly_info = titans_target.get('kelly_criterion', {})
        rec_lev = kelly_info.get('recommended_leverage', '1x-2x')
        safe_rat = kelly_info.get('capital_safety_rating', 'ULTRA_SAFE')

        # Final Supreme Actionable Guidance
        if master_bull_score >= 65.0 and institutional_bias != "BEARISH_PRESSURE":
            supreme_verdict = "🟢 SUPREME BULLISH BREAKOUT CONFIRMED"
            action_advice = f"Big Players + 301 Systems Bullish Alignment. Target: ${tp1_up:,.1f} - ${tp2_up:,.1f}. Floor: ${val:,.1f}. Kelly: {rec_lev} ({safe_rat})"
        elif master_bear_score >= 65.0 and institutional_bias != "BULLISH_PRESSURE":
            supreme_verdict = "🔴 SUPREME BEARISH DUMP CONFIRMED"
            action_advice = f"Big Players Dumping (CVD Negative). Target: ${tp1_down:,.1f} - ${tp2_down:,.1f}. Ceiling: ${d_vwap:,.1f}. Kelly: {rec_lev} ({safe_rat})"
        else:
            supreme_verdict = "⚖️ BIG PLAYERS RANGE CONSOLIDATION (TRAP ZONE)"
            action_advice = f"Big Players manipulating within [${val:,.1f}] and [${d_vwap:,.1f}]. No early retail guesses. Wait for clean 1H candle breakout. Kelly: {rec_lev}"

        return {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "target_timeframe": tf_str,
            "btc_price": curr_price,
            "total_systems_active": 301,
            "supreme_verdict": supreme_verdict,
            "action_advice": action_advice,
            "master_bull_score": master_bull_score,
            "master_bear_score": master_bear_score,
            "big_players_mode": big_players_mode,
            "cvd_value": cvd_val,
            "cvd_sentiment": cvd_sentiment,
            "dqs_displacement": dqs_score,
            "liquidation_heatmap": liq_hm,
            "kill_switch_guard": ks_eval,
            "global_quant": global_quant_res,
            "frontier_titans": frontier_res,
            "squeeze_status_target": sq_target['squeeze_state'],
            "squeeze_status_4h": sq_4h['squeeze_state'],
            "fourier_cycle": pred_res['fourier_cycle'],
            "key_chart_lines": chart_marking_lines,
            "order_blocks": order_blocks,
            "titans_summary": {
                "ehlers_dsp": titans_target['ehlers_dsp']['ehlers_trend'],
                "hurst_exponent": titans_target['hurst_exponent']['hurst_exponent'],
                "market_regime": titans_target['hurst_exponent']['market_regime'],
                "vpin_toxicity": titans_target['vpin_toxicity']['toxicity_state'],
                "wyckoff_phase": titans_target['wyckoff_phase']['wyckoff_signal'],
                "turtle_state": titans_target['turtle_breakout']['turtle_state'],
                "hft_micro_price": titans_target['avellaneda_hft']['theoretical_micro_price'],
                "yang_zhang_vol": titans_target['yang_zhang_vol']['yang_zhang_volatility_pct'],
                "dreiss_chop": titans_target['dreiss_chop']['chop_index'],
                "connors_rsi": titans_target['connors_rsi']['connors_rsi'],
                "mcginley_dynamic": titans_target['mcginley_dynamic']['mcginley_dynamic'],
                "td_rei": titans_target['td_rei']['td_rei'],
                "larry_williams_ad": titans_target['larry_williams_ad']['lw_ad_sentiment'],
                "ha_smoothed": titans_target['heikin_ashi_smoothed']['ha_smoothed_trend'],
                "kelly_leverage": rec_lev
            },
            "tp_targets": {
                "upside_tp1": tp1_up,
                "upside_tp2": tp2_up,
                "downside_tp1": tp1_down,
                "downside_tp2": tp2_down
            }
        }

if __name__ == "__main__":
    algo = SupremeUniversalAlgo()
    print("Testing Supreme Universal Master Algorithm on 1H and 15M...")
    res_1h = algo.analyze_market(60)
    print(f"1H Price: ${res_1h['btc_price']} | Verdict: {res_1h['supreme_verdict']}")
    print(f"Big Players Mode: {res_1h['big_players_mode']} (CVD: {res_1h['cvd_value']:,.0f})")
    print(f"Score: {res_1h['master_bull_score']}% Bull vs {res_1h['master_bear_score']}% Bear")
    print(f"Marked Lines Count: {len(res_1h['key_chart_lines'])} Lines Ready for Delta Chart!")
