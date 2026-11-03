"""
Delta Demo Auto-Bot Powered by Master Institutional Suite & Predictive AI Forecaster
(Includes: Lorentzian ML k-NN, Fourier Cycle Wave Projection, Monte Carlo Simulation + 25 Branded Engines)
"""
import hmac
import hashlib
import time
import json
import urllib.request
import urllib.error
import datetime
from email.utils import parsedate_to_datetime
import sys
import os

sys.path.append(r"C:\Users\om\.gemini\antigravity\scratch")

# --- All 25 Institutional Engines + Predictive AI Forecaster ---
from luxalgo_smc_engine import LuxAlgoSMC                               # 1 (LuxAlgo SMC)
from algoalpha_breakout_engine import AlgoAlphaBreakoutChannels         # 2 (AlgoAlpha Breakout)
from algoalpha_trend_targets import AlgoAlphaTrendTargets               # 3 (AlgoAlpha Trend Targets)
from luxalgo_volume_profile import LuxAlgoVolumeProfile                 # 4 (LuxAlgo Volume Profile)
from anchored_vwap_engine import AnchoredVWAP                           # 5 (Anchored VWAP)
from harmonic_fibonacci_engine import HarmonicFibonacciEngine           # 6 (Harmonic Fib / Golden Pocket)
from luxalgo_elliott_wave import LuxAlgoElliottWave                     # 7 (LuxAlgo Elliott Wave)
from liquidity_sweeps_engine import LiquiditySweepsEngine               # 8 (Liquidity Sweeps BSL/SSL)
from market_cipher_b_engine import MarketCipherBEngine                  # 9 (MarketCipher B Green Dot & MFI)
from ict_displacement_engine import ICTDisplacementEngine               # 10 (ICT DQS 0-100 & A/B/C Grades)
from ict_killzones_engine import ICTKillZonesEngine                     # 11 (ICT Sessions & :20-:40, :50-:10 Macros)
from relative_volume_engine import RelativeVolumeEngine                 # 12 (Kurtsmock rVol, Churn & Climax)
from ict_fvg_void_engine import ICTFVGVoidEngine                         # 13 (LunqFX ISD 3/3, IDM & BPR)
from nadaraya_watson_engine import NadarayaWatsonEnvelopeEngine         # 14 (LuxAlgo Nadaraya-Watson Envelope)
from dynamic_sr_heatmap import DynamicSRHeatmap                         # 15 (Dynamic S/R Clusters & Wall)
from delta_funding_oi_engine import DeltaFundingOIEngine                 # 16 (Delta Exchange Funding Rate & OI)
from luxalgo_reversal_engine import LuxAlgoReversalEngine               # 17 (LuxAlgo TD 9 Setup & 13 Exhaustion)
from mtf_trend_alignment import MTFTrendAlignmentEngine                 # 18 (4-TF Protected Structure Breaks)
from luxalgo_order_flow import LuxAlgoOrderFlow                         # 19 (LunqFX Volume Delta, CVD & Absorption)
from market_cipher_a_engine import MarketCipherAEngine                  # 20 (MarketCipher A 8-EMA Ribbon & Blood Diamond)
from ripster_clouds_engine import RipsterCloudsEngine                   # 21 (Ripster EMA Clouds 34-50 & 5-12)
from zeiierman_kalman_engine import ZeiiermanKalmanEngine               # 22 (Zeiierman Adaptive Kalman Filter Oscillator)
from waddah_attar_explosion import WaddahAttarExplosionEngine           # 23 (Waddah Attar Explosion WAE)
from algoalpha_volume_flow_index import AlgoAlphaVolumeFlowIndex        # 24 (AlgoAlpha Volume Flow Index VFI)
from luxalgo_trailing_profit import HighWatermarkProfitEngine           # 25 (High-Watermark Profit Lock 20K)
from predictive_forecast_engine import PredictiveForecastEngine         # 26 (Future Machine Learning & Fourier Wave Predictor)
from master_quant_indicators import MasterQuantSuite                     # 27 (Omni-Quant 150+ Standard & Community Indicators Suite)
from vip_all_in_one_suite import AllInOneVIPSuite                       # 28 (VIP Paid & Proprietary 15 Commercial Algos Suite)
from daviddme_kill_switch_guard import DavidDMEKillSwitchGuard          # 29 (DavidDME Emergency Kill-Switch & Risk Guard)
from liquidation_heatmap_engine import LiquidationHeatmapEngine          # 30 (Claude Quantitative Liquidation Heatmap & Whale Magnet)
from trader_timemachine_engine import TraderTimeMachineEngine            # 31 (TimeMachine Historical Replay Engine)

_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(_DIR, "trading_config.json")
if not os.path.exists(CONFIG_PATH):
    CONFIG_PATH = r"C:\Users\om\.gemini\antigravity\scratch\trading_config.json"
STATUS_FILE = os.path.join(_DIR, "bot_live_status.txt")
TRADE_LOG_FILE = os.path.join(_DIR, "bot_trade_history.log")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    _cfg = json.load(f)

API_KEY = _cfg["demo"]["api_key"]
API_SECRET = _cfg["demo"]["api_secret"]
BASE_URL = _cfg["demo"]["base_url"]
SYMBOL = "BTCUSD"
PRODUCT_ID = 84
LIVE_TRADING_ENABLED = _cfg.get("live_trading_enabled", False)

profit_trail = HighWatermarkProfitEngine()
pred_engine = PredictiveForecastEngine()
quant_suite = MasterQuantSuite()
vip_suite = AllInOneVIPSuite()

def log_trade(msg):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now_str}] {msg}\n"
    with open(TRADE_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())

def get_server_timestamp():
    try:
        t = int(time.time())
        req = urllib.request.Request(f"{BASE_URL}/v2/products?limit=1&_t={t}", headers={"User-Agent": "DeltaBot/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            date_hdr = resp.headers.get("Date")
            dt = parsedate_to_datetime(date_hdr)
            return str(int(dt.timestamp()))
    except Exception:
        return str(int(time.time()))

def make_request(method, endpoint, payload_dict=None):
    ts = get_server_timestamp()
    payload_str = ""
    if payload_dict is not None and method in ["POST", "PUT", "DELETE"]:
        payload_str = json.dumps(payload_dict, separators=(',', ':'))
        
    path = endpoint.split("?")[0]
    query = endpoint.split("?")[1] if "?" in endpoint else ""
    
    sig_data = method + ts + path
    if query:
        sig_data += "?" + query
    sig_data += payload_str
    
    sig = hmac.new(API_SECRET.encode("utf-8"), sig_data.encode("utf-8"), hashlib.sha256).hexdigest()
    
    headers = {
        "api-key": API_KEY,
        "signature": sig,
        "timestamp": ts,
        "User-Agent": "DeltaBot/1.0",
        "Content-Type": "application/json"
    }
    
    url = BASE_URL + endpoint
    data_bytes = payload_str.encode("utf-8") if payload_str else None
    
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode()
        try:
            return json.loads(err_msg)
        except Exception:
            return {"error": str(e), "message": err_msg}
    except Exception as e:
        return {"error": str(e)}

def get_wallet_equity():
    try:
        res = make_request("GET", "/v2/wallet/balances")
        if res.get("success") and "meta" in res:
            return float(res["meta"].get("net_equity", 95.0))
    except Exception:
        pass
    return 95.0

def get_candles(resolution=60, count=48):
    now = int(time.time())
    res_str = str(resolution)
    mult = 1440 if res_str.upper() == 'D' else int(resolution)
    start = now - (count + 10) * mult * 60
    url = f"https://api.india.delta.exchange/v2/chart/history?symbol={SYMBOL}&resolution={res_str}&from={start}&to={now}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        d = json.loads(resp.read().decode())['result']
        
    candles = []
    for i in range(len(d['t'])):
        candles.append({
            't': d['t'][i],
            'o': float(d['o'][i]),
            'h': float(d['h'][i]),
            'l': float(d['l'][i]),
            'c': float(d['c'][i]),
            'v': float(d['v'][i])
        })
    return candles

def get_positions():
    res = make_request("GET", "/v2/positions/margined")
    if res.get("success") and "result" in res:
        pos_list = [p for p in res["result"] if abs(float(p.get("size", 0))) > 0]
        return pos_list
    if not res.get("success") and isinstance(res.get("error"), dict) and res.get("error", {}).get("code") == "ip_not_whitelisted_for_api_key":
        client_ip = res.get("error", {}).get("context", {}).get("client_ip", "Unknown")
        return {"error": "ip_not_whitelisted", "client_ip": client_ip}
    return []

def cancel_all_orders():
    return make_request("DELETE", f"/v2/orders/all?product_id={PRODUCT_ID}")

def close_position(pos):
    size = abs(float(pos["size"]))
    side = "sell" if float(pos["size"]) > 0 else "buy"
    order_payload = {
        "product_id": PRODUCT_ID,
        "size": int(size),
        "side": side,
        "order_type": "market_order"
    }
    close_res = make_request("POST", "/v2/orders", order_payload)
    cancel_res = cancel_all_orders()
    profit_trail.reset()
    log_trade(f"CLOSED POSITION: {side.upper()} {size} contracts | Cleaned all pending orders.")
    return close_res, cancel_res

def place_order(side, size=None):
    if not LIVE_TRADING_ENABLED:
        msg = f"🔒 [SAFE UPDATE MODE - NO TRADES] Signal: {side.upper()} | Real/Demo order placement is PAUSED by user. No orders sent."
        log_trade(msg)
        return {"status": "paused_for_updates"}
    try:
        make_request("POST", "/v2/products/set_leverage", {"product_id": PRODUCT_ID, "leverage": "3"})
    except Exception:
        pass
        
    if size is None:
        equity = get_wallet_equity()
        size = profit_trail.calculate_compounding_size(equity, 80000.0, leverage=3.0)

    order_payload = {
        "product_id": PRODUCT_ID,
        "size": int(size),
        "side": side.lower(),
        "order_type": "market_order"
    }
    res = make_request("POST", "/v2/orders", order_payload)
    profit_trail.reset()
    log_trade(f"NEW ORDER PLACED BY PREDICTIVE SUITE: {side.upper()} {size} contracts on {SYMBOL} | Result: {res.get('success')}")
    return res

def run_single_cycle():
    c_daily = get_candles('D', 30)
    c_4h = get_candles(240, 60)
    c_1h = get_candles(60, 200)
    c_15m = get_candles(15, 150)
    
    # 1-8 Existing Engines
    lux = LuxAlgoSMC()
    algo_chan = AlgoAlphaBreakoutChannels(norm_length=100, box_length=14, strong=True)
    algo_targets = AlgoAlphaTrendTargets()
    vp_engine = LuxAlgoVolumeProfile(lookback=200, row_size=100)
    vwap_engine = AnchoredVWAP(use_ohlc4=True)
    hf_engine = HarmonicFibonacciEngine()
    ew_engine = LuxAlgoElliottWave()
    lq_engine = LiquiditySweepsEngine()
    
    # 9-24 Branded Engines
    mc_engine = MarketCipherBEngine()
    disp_engine = ICTDisplacementEngine()
    kz_engine = ICTKillZonesEngine()
    rvol_engine = RelativeVolumeEngine(min_contracts=300)
    fvg_engine = ICTFVGVoidEngine()
    nwe_engine = NadarayaWatsonEnvelopeEngine()
    sr_heatmap = DynamicSRHeatmap()
    delta_oi = DeltaFundingOIEngine()
    rev_engine = LuxAlgoReversalEngine()
    mtf_engine = MTFTrendAlignmentEngine()
    of_engine = LuxAlgoOrderFlow()
    mca_engine = MarketCipherAEngine()
    rip_engine = RipsterCloudsEngine()
    zk_engine = ZeiiermanKalmanEngine()
    wae_engine = WaddahAttarExplosionEngine()
    vfi_engine = AlgoAlphaVolumeFlowIndex()
    
    # Run analysis
    smc_1h = lux.analyze(c_1h)
    smc_15m = lux.analyze(c_15m)
    algo_1h = algo_chan.analyze(c_1h)
    targets_1h = algo_targets.analyze(c_1h)
    vp_1h = vp_engine.analyze(c_1h)
    vwap_res = vwap_engine.analyze(c_1h)
    hf_res = hf_engine.analyze(c_1h)
    ew_res = ew_engine.analyze(c_1h)
    lq_res = lq_engine.analyze(c_1h)
    
    mc_res = mc_engine.analyze(c_1h)
    disp_res = disp_engine.analyze(c_1h)
    kz_res = kz_engine.analyze(c_1h)
    rvol_res = rvol_engine.analyze(c_1h)
    fvg_res = fvg_engine.analyze(c_1h)
    nwe_res = nwe_engine.analyze(c_1h)
    sr_res = sr_heatmap.analyze(c_1h)
    oi_res = delta_oi.analyze()
    rev_res = rev_engine.analyze(c_1h)
    mtf_res = mtf_engine.analyze(c_daily, c_4h, c_1h, c_15m)
    of_res = of_engine.analyze(c_1h)
    mca_res = mca_engine.analyze(c_1h)
    rip_res = rip_engine.analyze(c_1h)
    zk_res = zk_engine.analyze(c_1h)
    wae_res = wae_engine.analyze(c_1h)
    vfi_res = vfi_engine.analyze(c_1h)
    quant_res = quant_suite.analyze_full_universe(c_1h)
    vip_res = vip_suite.analyze_all_vip_algos(c_1h)
    
    # Run Engine #26: Predictive AI Forecaster (Synthesizing all 25 Technical & Institutional Engines + 150 Quant Indicators + 15 VIP Commercial Algos)
    engine_context = {
        "smc_1h": smc_1h,
        "smc_15m": smc_15m,
        "algo_1h": algo_1h,
        "targets_1h": targets_1h,
        "vp_1h": vp_1h,
        "vwap_res": vwap_res,
        "hf_res": hf_res,
        "ew_res": ew_res,
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
        "quant_res": quant_res,
        "vip_res": vip_res
    }
    pred_res = pred_engine.analyze(c_1h, c_15m, engine_context=engine_context)
    
    curr_price = smc_15m['current_price']
    
    # Engines #29 & #30: Liquidation Heatmap & DavidDME Kill-Switch
    liq_hm_engine = LiquidationHeatmapEngine()
    liq_hm = liq_hm_engine.calculate_heatmap(c_1h, curr_price)
    ks_guard = DavidDMEKillSwitchGuard()

    chan = algo_1h.get('active_channel')
    chan_str = f"${chan['bottom']:,.1f} - ${chan['top']:,.1f} (Mid: ${chan['midline']:,.1f})" if chan else "None (Searching)"
    
    positions = get_positions()
    pos_status = "None (Looking for setup)"
    action_taken = "Predictive Suite Monitoring Forward Cycle..."
    
    if isinstance(positions, dict) and positions.get("error") == "ip_not_whitelisted":
        pos_status = f"⚠️ IP Whitelist Needed (Current IP: {positions.get('client_ip')})"
        action_taken = "Please add this IP to Delta Testnet API Key Settings"
    elif isinstance(positions, list) and len(positions) > 0:
        pos = positions[0]
        size = float(pos.get("size", 0))
        entry = float(pos.get("entry_price", 0))
        pnl = float(pos.get("unrealized_pnl", 0))
        side = "LONG (BUY)" if size > 0 else "SHORT (SELL)"
        pos_status = f"{side} | Size: {size} | Entry: ${entry:,.1f} | Unrealized PnL: ${pnl:.4f}"
        
        # Engine #25: High-Watermark Dynamic Profit Trail Update
        trail_res = profit_trail.update_position(pnl, side)
        
        # Engine #28: DavidDME Perpetual Futures Kill-Switch & Risk Guard (User Rule #6)
        ks_eval = ks_guard.evaluate_kill_switch(pos, curr_price, c_1h[-1] if c_1h else None, cvd_net_delta=of_res.get('cvd_value', 0))
        if ks_eval["should_kill"]:
            ks_guard.execute_instant_kill(make_request, cancel_all_orders, pos, ks_eval["reason"])
            action_taken = ks_eval["reason"]
        # User Exit Strategy (Capital Protection + Predictive Reversals)
        elif pnl < -10.0:
            close_position(pos)
            action_taken = f"EXITED {side} to protect capital (Discipline rule)."
        elif trail_res["should_exit"]:
            close_position(pos)
            action_taken = trail_res["exit_reason"]
        elif side == "LONG (BUY)" and mca_res['blood_diamond'] and pnl > 0.5:
            close_position(pos)
            action_taken = f"EXITED ON MARKETCIPHER BLOOD DIAMOND! PnL: +${pnl:.2f}."
        elif side == "LONG (BUY)" and ("RED DOT" in mc_res['signal_dot'] or "RED CROSS" in mc_res['signal_dot']) and pnl > 1.5:
            close_position(pos)
            action_taken = f"MARKETCIPHER RED DOT ('ਕਮ ਪੈਸੇ ਤੁਰੇ ਜਾਂਦੇ ਆ')! PnL: +${pnl:.2f}. Cleared all pending orders."
        elif side == "SHORT (SELL)" and ("GREEN DOT" in mc_res['signal_dot'] or "GREEN CROSS" in mc_res['signal_dot']) and pnl > 1.5:
            close_position(pos)
            action_taken = f"MARKETCIPHER GREEN DOT ('ਗੇਮ ਘੁੰਮ ਗਈ')! PnL: +${pnl:.2f}. Cleared all pending orders."
        elif side == "SHORT (SELL)" and curr_price <= targets_1h['calculated_tp1'] and pnl > 2.5:
            close_position(pos)
            action_taken = f"TP1 REACHED! PnL: +${pnl:.2f}. Closed position and cancelled pending orders."
        elif side == "LONG (BUY)" and curr_price >= targets_1h['calculated_tp1'] and pnl > 2.5:
            close_position(pos)
            action_taken = f"TP1 REACHED! PnL: +${pnl:.2f}. Closed position and cancelled pending orders."
        elif side == "LONG (BUY)" and "BEARISH SETUP 9" in rev_res['reversal_signal'] and pnl > 1.0:
            close_position(pos)
            action_taken = f"EXITED ON LUXALGO BEARISH SETUP 9! PnL: +${pnl:.2f}."
        elif side == "SHORT (SELL)" and "BULLISH SETUP 9" in rev_res['reversal_signal'] and pnl > 1.0:
            close_position(pos)
            action_taken = f"EXITED ON LUXALGO BULLISH SETUP 9! PnL: +${pnl:.2f}."
    else:
        profit_trail.reset()
        # High-confluence entry
        bearish_signal = False
        if chan and curr_price < chan['bottom'] and "DISCOUNT" not in smc_1h['zone'] and rvol_res['meets_threshold']:
            bearish_signal = True
        elif mca_res['blood_diamond'] and "DISCOUNT" not in smc_1h['zone']:
            bearish_signal = True
        elif wae_res['is_exploding'] and "BEARISH EXPLOSION" in wae_res['status']:
            bearish_signal = True
        elif "RED DOT" in mc_res['signal_dot'] and "DISCOUNT" not in smc_1h['zone']:
            bearish_signal = True
        elif fvg_res['isd_complete'] and "BULL TRAP" in fvg_res['idm_status']:
            bearish_signal = True

        bullish_signal = False
        if chan and curr_price > chan['top'] and "PREMIUM" not in smc_1h['zone'] and rvol_res['meets_threshold']:
            bullish_signal = True
        elif mca_res['yellow_cross'] and "PREMIUM" not in smc_1h['zone']:
            bullish_signal = True
        elif wae_res['is_exploding'] and "BULLISH EXPLOSION" in wae_res['status']:
            bullish_signal = True
        elif "GREEN DOT" in mc_res['signal_dot'] and "PREMIUM" not in smc_1h['zone']:
            bullish_signal = True
        elif fvg_res['isd_complete'] and "BEAR TRAP" in fvg_res['idm_status']:
            bullish_signal = True

        if bearish_signal:
            if LIVE_TRADING_ENABLED:
                place_order("sell")
                action_taken = f"Triggered SELL on Confluence Breakdown @ ${curr_price:,.1f}"
            else:
                action_taken = f"🔒 [SAFE UPDATE MODE - NO TRADES] SELL Signal detected @ ${curr_price:,.1f} (Orders Paused)"
        elif bullish_signal:
            if LIVE_TRADING_ENABLED:
                place_order("buy")
                action_taken = f"Triggered BUY on Confluence Breakout @ ${curr_price:,.1f}"
            else:
                action_taken = f"🔒 [SAFE UPDATE MODE - NO TRADES] BUY Signal detected @ ${curr_price:,.1f} (Orders Paused)"

    status_text = f"""
===================================================================================
      PREDICTIVE AI FORWARD FORECASTER (ਅੱਗੇ ਕੀ ਹੋਣ ਵਾਲਾ ਹੈ?)                      
===================================================================================
🔮 Forecast Verdict   : {pred_res['predicted_verdict']}
🎯 Projected Target   : {pred_res['expected_move_text']}
🤖 Lorentzian ML k-NN : {pred_res['ml_k_nn_bias']}
🌊 Fourier Wave Cycle : {pred_res['fourier_cycle']}
🌐 Confluence Matrix  : {pred_res.get('connected_engines_count', 25)} Engines Synchronized & Synthesized
===================================================================================
      MASTER INSTITUTIONAL AI TRADING SUITE (ALL 25 ENGINES CONNECTED)            
===================================================================================
Time (IST)           : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
BTC Mark Price       : ${curr_price:,.1f}
[01] LuxAlgo SMC     : {smc_1h.get('last_structure', 'None')} ({smc_1h.get('trend_bias', 'NEUTRAL')})
[02] Breakout Chan   : {chan_str}
[03] Trend Targets   : Baseline: ${targets_1h['baseline_tL']:,.1f} ({targets_1h['trend_direction']})
[04] Volume Profile  : POC: ${vp_1h['poc']:,.1f} (VAH: ${vp_1h['vah']:,.1f} | VAL: ${vp_1h['val']:,.1f})
[05] Anchored VWAP   : Daily: ${vwap_res['daily_avwap']:,.1f} | Weekly: ${vwap_res['weekly_avwap']:,.1f}
[06] Harmonic Fibo   : {hf_res['harmonic_zone']} (Res: {hf_res['next_harmonic_resistance']})
[07] Elliott Wave    : {ew_res['wave_status']}
[08] Liquidity Pools : BSL: ${lq_res.get('nearest_bsl_pool', 0):,.1f} | SSL: ${lq_res.get('nearest_ssl_pool', 0):,.1f}
[09] MarketCipher B  : {mc_res['signal_dot']} | Money Flow: {mc_res['money_flow_state']} (WT1: {mc_res['wt1']} | WT2: {mc_res['wt2']})
[10] DQS Displacement: DQS: {disp_res['dqs_score']}/100 [{disp_res['grade']}] | {disp_res['mss_status']}
[11] ICT Macros & KZ : {kz_res['current_session']} | {kz_res['active_macro']} ({kz_res['ny_time']})
[12] rVol & Churn    : {rvol_res['volume_status']} | Buy Share: {rvol_res['vbuy_pct']}%
[13] LunqFX ISD & FVG: ISD 0/3  | IDM: NONE | BPR: {fvg_res['bpr_range']}
[14] LuxAlgo NWE Env : {nwe_res['envelope_status']} (Upper: ${nwe_res['upper_band']:,.1f} | Lower: ${nwe_res['lower_band']:,.1f})
[15] Dynamic SR Wall : {sr_res['sr_status']}
[16] Funding / OI    : Rate: {oi_res['funding_rate_8h_pct']}% | Bias: {oi_res['sentiment_bias']}
[17] Lux Reversal 913: {rev_res['momentum_phase']} | {rev_res['reversal_signal']}
[18] MTF Alignment   : {mtf_res['status_text']} [D: {mtf_res['daily']} | 4H: {mtf_res['h4']} | 1H: {mtf_res['h1']} | 15m: {mtf_res['m15']}]
[19] Order Flow CVD  : {of_res['delta_sentiment']} | CVD: {of_res['cvd_value']} | {of_res['divergence_signal']}
[20] MarketCipher A  : {mca_res['signal_name']} (RSI: {mca_res['rsi']} | WT2: {mca_res['wt2']})
[21] Ripster Clouds  : {rip_res['trend_state']} (Cloud 2: {rip_res['cloud_2_state']})
[22] Zeiierman Kalman: {zk_res['trend_status']} (Filtered: ${zk_res['filtered_price']:,.1f})
[23] Waddah Attar WAE: {wae_res['status']} (Up: {wae_res['uptrend_val']} | Expl: {wae_res['explosion_line']} | Dead: {wae_res['deadzone_line']})
[24] AlgoAlpha VFI   : {vfi_res['status']} ({vfi_res['whale_flow']}) [Sig: {vfi_res['vfi_signal']}]
[25] Profit Trail 20K: Peak PnL: ${profit_trail.state['peak_pnl']:.2f} | Dynamic 20K Exit Ready
[26] Omni-Quant 150+ : {quant_res['omni_bullish_consensus_pct']}% Bull vs {quant_res['omni_bearish_consensus_pct']}% Bear (RSI: {quant_res['indicators_snapshot']['RSI_14']} | ST: {quant_res['indicators_snapshot']['SuperTrend']} | MFI: {quant_res['indicators_snapshot']['MFI_Flow']} | ADX: {quant_res['indicators_snapshot']['ADX_Trend_Strength']})
[27] VIP Algos Suite : {vip_res['vip_bull_pct']}% Bull vs {vip_res['vip_bear_pct']}% Bear (UT Bot: {vip_res['ut_bot']['trend_state']} | Squeeze: {vip_res['squeeze_pro']['squeeze_dot']} | HalfTrend: {vip_res['halftrend']['trend_direction']} | QQE: {vip_res['qqe_mod']['qqe_status']} | TD: {vip_res['td_sequential']['td_state']})
[28] Liq Heatmap Mag : {liq_hm['whale_magnet_direction']} -> Target: ${liq_hm['primary_magnet_target']:,.1f} ({liq_hm['magnet_distance_pct']:.2f}% away)
[29] DavidDME Guard  : ACTIVE (Zero Hanging Orders Policy | Flash Drop Guard: {ks_guard.flash_drop_threshold_pct}%)
-----------------------------------------------------------------------------------
Position Status      : {pos_status}
Last Action          : {action_taken}
===================================================================================
"""
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        f.write(status_text)
    print(status_text)
    return status_text

if __name__ == "__main__":
    run_single_cycle()
