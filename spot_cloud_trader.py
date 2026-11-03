"""
===================================================================================
DELTA EXCHANGE 24/7 CLOUD AUTO-TRADER (301-SYSTEM SUPREME GRAND MEGAVERSE)
===================================================================================
Executes 24/7 on Cloud (Render) with ZERO computer required.
- Powered by 301 Technical Systems, VIP Algos, Frontier Quants & Titans.
- Follows Big Players (Order Flow CVD, Whale VFI, Stop-Hunt Sweeps, Wyckoff).
- Bull Score >= 70% + Whale Accumulation -> AUTO BUY / LONG (Delta Testnet)
- Bear Score >= 70% + Whale Distribution -> AUTO SELL / SHORT (Delta Testnet)
- Zero Hanging Orders Policy: Pending orders cleared after execution.
- Web Dashboard on Port with 1-Click Remote Kill-Switch (/stop & /start).
===================================================================================
"""

import os
import sys
import time
import json
import hmac
import hashlib
import datetime
import threading
import urllib.request
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

# Ensure local directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from supreme_universal_algo import SupremeUniversalAlgo
    _HAS_301_ENGINE = True
except Exception as e:
    print(f"Warning: could not import SupremeUniversalAlgo: {e}", flush=True)
    _HAS_301_ENGINE = False

# 1. Credentials & Configuration
BASE_URL = os.environ.get("DELTA_BASE_URL", "https://cdn-ind.testnet.deltaex.org")
API_KEY = os.environ.get("DELTA_API_KEY", "EfMq2GXNOJ3Nvp6rwbR5vP57OdDHgN")
API_SECRET = os.environ.get("DELTA_API_SECRET", "Vf44M5CBiTr5NYxdF7iwjvR4xiOyS974eF6pp809zhXxBmFDW7BCbts95Ndb")

SYMBOL_FUTURES = "BTCUSD"
PRODUCT_ID_FUTURES = 139  # BTCUSD Perp

PORT = int(os.environ.get("PORT", 8080))

_bot_lock = threading.Lock()
_bot_state = {
    "is_trading_active": True,
    "last_price": 77000.0,
    "total_systems_active": 301,
    "supreme_verdict": "INITIALIZING 301-SYSTEM ARSENAL...",
    "big_players_mode": "SCANNING BIG PLAYERS...",
    "last_cvd": 0,
    "bull_score": 50.0,
    "bear_score": 50.0,
    "last_action": "HOLD",
    "last_reason": "301-System Engine Loading...",
    "trade_history": [],
    "last_cycle_time": "Initializing",
    "mode": "301-SYSTEM SUPREME ARSENAL (BIG PLAYERS TRACKING)"
}

def log_trade(action, price, reason):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {action} at ${price:,.1f} | {reason}"
    print(f"⚡ {entry}", flush=True)
    with _bot_lock:
        _bot_state["trade_history"].append(entry)
        if len(_bot_state["trade_history"]) > 25:
            _bot_state["trade_history"].pop(0)

def get_server_timestamp():
    try:
        req = urllib.request.Request(f"{BASE_URL}/v2/products?limit=1", headers={"User-Agent": "DeltaCloudBot/301"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            d = resp.headers.get("Date")
            if d:
                return str(int(time.mktime(time.strptime(d, "%a, %d %b %Y %H:%M:%S GMT"))))
    except Exception:
        pass
    return str(int(time.time()))

def make_signed_request(method, endpoint, payload_dict=None):
    if not API_KEY or not API_SECRET:
        return {"error": "no_credentials"}
    ts = get_server_timestamp()
    payload_str = json.dumps(payload_dict, separators=(',', ':')) if payload_dict and method in ["POST", "PUT", "DELETE"] else ""
    path = endpoint.split("?")[0]
    query = endpoint.split("?")[1] if "?" in endpoint else ""
    sig_data = method + ts + path + ("?" + query if query else "") + payload_str
    sig = hmac.new(API_SECRET.encode("utf-8"), sig_data.encode("utf-8"), hashlib.sha256).hexdigest()
    
    headers = {
        "api-key": API_KEY,
        "signature": sig,
        "timestamp": ts,
        "User-Agent": "DeltaCloudBot/301",
        "Content-Type": "application/json"
    }
    url = BASE_URL + endpoint
    data_bytes = payload_str.encode("utf-8") if payload_str else None
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

def execute_delta_order(side, price, reason):
    try:
        # Cancel any hanging orders first
        make_signed_request("DELETE", f"/v2/orders/all?product_id={PRODUCT_ID_FUTURES}")
        
        # Place Market Order on Delta
        order_payload = {
            "product_id": PRODUCT_ID_FUTURES,
            "size": 1,
            "side": side.lower(),
            "order_type": "market_order"
        }
        res = make_signed_request("POST", "/v2/orders", order_payload)
        log_trade(f"AUTO-{side.upper()}", price, f"{reason} | Delta Res: {res.get('success', True)}")
        print(f"Delta API Result: {res}", flush=True)
    except Exception as e:
        print(f"Execution Error: {e}", flush=True)

def run_trading_engine_loop():
    print("🚀 [301-SYSTEM CLOUD BOT ACTIVE] Initializing Grand Megaverse...", flush=True)
    supreme_algo = None
    if _HAS_301_ENGINE:
        try:
            supreme_algo = SupremeUniversalAlgo()
            print("✅ [301-SYSTEM CORE READY] All 301 Quant Titans and Institutional Engines Active!", flush=True)
        except Exception as e:
            print(f"❌ [INIT ERROR] {e}", flush=True)

    current_position_side = None

    while True:
        try:
            with _bot_lock:
                active = _bot_state["is_trading_active"]
                
            if not active:
                time.sleep(15)
                continue

            if supreme_algo:
                # Run full 301-System multi-timeframe analysis
                analysis = supreme_algo.analyze_market(60)
                curr_price = float(analysis.get("btc_price", 77000.0))
                verdict = analysis.get("supreme_verdict", "NEUTRAL")
                big_players = analysis.get("big_players_mode", "TRACKING")
                cvd = float(analysis.get("cvd_value", 0.0))
                bull_score = float(analysis.get("master_bull_score", 50.0))
                bear_score = float(analysis.get("master_bear_score", 50.0))
                total_systems = int(analysis.get("total_systems_active", 301))

                with _bot_lock:
                    _bot_state["last_price"] = curr_price
                    _bot_state["supreme_verdict"] = verdict
                    _bot_state["big_players_mode"] = big_players
                    _bot_state["last_cvd"] = cvd
                    _bot_state["bull_score"] = bull_score
                    _bot_state["bear_score"] = bear_score
                    _bot_state["total_systems_active"] = total_systems
                    _bot_state["last_cycle_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # STRICT BIG PLAYERS EXECUTION LOGIC
                # Buy only when Bull Score >= 70% and CVD indicates institutional accumulation
                if bull_score >= 70.0 and cvd > 0:
                    action = "AUTO BUY / LONG"
                    reason = f"301 ਅਲਗੋਜ਼ ਦਾ ਬਹੁਮਤ ({bull_score:.1f}% Bullish) + ਵੱਡੇ ਪਲੇਅਰਾਂ ਦਾ Accumulation! CVD: +{cvd:,.0f}"
                    with _bot_lock:
                        _bot_state["last_action"] = action
                        _bot_state["last_reason"] = reason

                    if current_position_side != "BUY":
                        execute_delta_order("buy", curr_price, reason)
                        current_position_side = "BUY"

                # Sell only when Bear Score >= 70% and CVD indicates institutional distribution
                elif bear_score >= 70.0 and cvd < 0:
                    action = "AUTO SELL / SHORT"
                    reason = f"301 ਅਲਗੋਜ਼ ਦਾ ਬਹੁਮਤ ({bear_score:.1f}% Bearish) + ਵੱਡੇ ਪਲੇਅਰਾਂ ਦੀ Distribution! CVD: {cvd:,.0f}"
                    with _bot_lock:
                        _bot_state["last_action"] = action
                        _bot_state["last_reason"] = reason

                    if current_position_side != "SELL":
                        execute_delta_order("sell", curr_price, reason)
                        current_position_side = "SELL"

                else:
                    action = "HOLD (ਧੀਰਜ ਰੱਖੋ)"
                    reason = f"ਮਾਰਕਿਟ ਸਾਈਡਵੇਜ਼ ਰੇਂਜ / ਰਿਟੇਲ ਟਰੈਪ ਹੈ (Bull: {bull_score:.1f}% | Bear: {bear_score:.1f}%). ਵੱਡੇ ਪਲੇਅਰਾਂ ਦੀ ਪੱਕੀ ਮੂਵ ਦੀ ਉਡੀਕ."
                    with _bot_lock:
                        _bot_state["last_action"] = action
                        _bot_state["last_reason"] = reason

            time.sleep(60)
        except Exception as e:
            print(f"Loop Exception: {e}", flush=True)
            time.sleep(15)

class CloudBotWebHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

    def do_GET(self):
        global _bot_state
        if self.path == "/stop":
            with _bot_lock:
                _bot_state["is_trading_active"] = False
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h1>🛑 ਟਰੇਡਿੰਗ ਰੋਕ ਦਿੱਤੀ ਗਈ ਹੈ (TRADING PAUSED)</h1><p><a href='/'>ਵਾਪਸ ਡੈਸ਼ਬੋਰਡ ਜਾਓ</a></p>".encode("utf-8"))
            return
            
        if self.path == "/start":
            with _bot_lock:
                _bot_state["is_trading_active"] = True
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<h1>🟢 ਟਰੇਡਿੰਗ ਦੁਬਾਰਾ ਚਾਲੂ ਹੋ ਗਈ ਹੈ (TRADING ACTIVE)</h1><p><a href='/'>ਵਾਪਸ ਡੈਸ਼ਬੋਰਡ ਜਾਓ</a></p>".encode("utf-8"))
            return
            
        with _bot_lock:
            state = _bot_state.copy()
            
        status_badge = "<span style='color: lime;'>● ਚਾਲੂ ਹੈ (ACTIVE 24/7)</span>" if state["is_trading_active"] else "<span style='color: red;'>■ ਰੁਕਿਆ ਹੋਇਆ ਹੈ (PAUSED)</span>"
        action_color = "lime" if "BUY" in state["last_action"] else ("red" if "SELL" in state["last_action"] else "orange")
        history_html = "".join(f"<li>{h}</li>" for h in reversed(state["trade_history"])) or "<li>301 ਸਿਸਟਮ ਤਿਆਰ ਹਨ - ਵੱਡੇ ਪਲੇਅਰਾਂ ਦੀ ਪੱਕੀ ਮੂਵ ਦੀ ਉਡੀਕ</li>"
        
        bull_pct = state['bull_score']
        bear_pct = state['bear_score']

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Delta 24/7 Cloud Auto-Trader (301 Systems)</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0f19; color: #fff; padding: 20px; }}
        .card {{ background: #151c2c; border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid #2d3748; }}
        .btn {{ display: inline-block; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-right: 10px; }}
        .btn-danger {{ background: #ef4444; color: white; }}
        .btn-success {{ background: #10b981; color: white; }}
        .metric {{ font-size: 32px; font-weight: bold; color: #38bdf8; }}
        .badge {{ background: #1e293b; padding: 4px 10px; border-radius: 6px; border: 1px solid #475569; font-weight: bold; }}
        .bar-container {{ width: 100%; background: #334155; border-radius: 8px; overflow: hidden; height: 24px; display: flex; margin: 10px 0; }}
        .bar-bull {{ background: #10b981; text-align: center; font-weight: bold; font-size: 13px; line-height: 24px; color: #000; width: {bull_pct}%; }}
        .bar-bear {{ background: #ef4444; text-align: center; font-weight: bold; font-size: 13px; line-height: 24px; color: #fff; width: {bear_pct}%; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>⚡ DELTA 24/7 CLOUD AUTO-TRADER (301-SYSTEM SUPREME)</h2>
        <p>ਕੁੱਲ ਸਰਗਰਮ ਸਿਸਟਮ: <span class="badge" style="color: #facc15;">301 SYSTEMS ACTIVE</span> | ਸਟੇਟਸ: {status_badge}</p>
        <p>ਆਖਰੀ ਚੈੱਕ: <strong>{state['last_cycle_time']}</strong> | ਵੱਡੇ ਪਲੇਅਰਾਂ ਦਾ ਮੋਡ: <strong style="color: #a78bfa;">{state['big_players_mode']}</strong></p>
        <p>ਬਿਟਕੋਇਨ ਲਾਈਵ ਭਾਅ: <span class="metric">${state['last_price']:,.1f}</span></p>
        <p>ਵੱਡੇ ਪਲੇਅਰਾਂ ਦਾ CVD: <strong>{state['last_cvd']:,.0f} contracts</strong></p>
        
        <p><strong>301 ਸਿਸਟਮਾਂ ਦੀ ਸਾਂਝੀ ਵੋਟਿੰਗ (Consensus):</strong></p>
        <div class="bar-container">
            <div class="bar-bull">Bull: {bull_pct:.1f}%</div>
            <div class="bar-bear">Bear: {bear_pct:.1f}%</div>
        </div>
        
        <p>ਸੁਪਰੀਮ ਫੈਸਲਾ: <strong style="font-size: 18px;">{state['supreme_verdict']}</strong></p>
        <p>ਮੌਜੂਦਾ ਹੁਕਮ: <strong style="color: {action_color}; font-size: 22px;">{state['last_action']}</strong></p>
        <p style="color: #94a3b8; font-style: italic;">{state['last_reason']}</p>
    </div>

    <div class="card">
        <h3>🛑 ਐਮਰਜੈਂਸੀ ਰਿਮੋਟ ਕੰਟਰੋਲ (ਕਿਸੇ ਵੀ ਡਿਵਾਈਸ ਤੋਂ ਬੰਦ/ਚਾਲੂ ਕਰੋ):</h3>
        <p>ਜੇ ਕਦੇ ਵੀ ਟਰੇਡਿੰਗ ਰੋਕਣੀ ਹੋਵੇ:</p>
        <a href="/stop" class="btn btn-danger">🛑 ਟਰੇਡਿੰਗ ਰੋਕੋ (PAUSE BOT)</a>
        <a href="/start" class="btn btn-success">🟢 ਟਰੇਡਿੰਗ ਚਲਾਓ (RESUME)</a>
    </div>

    <div class="card">
        <h3>📜 ਆਟੋ-ਟਰੇਡ ਹਿਸਟਰੀ (Live Executions):</h3>
        <ul>{history_html}</ul>
    </div>
</body>
</html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

def main():
    t = threading.Thread(target=run_trading_engine_loop, daemon=True)
    t.start()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), CloudBotWebHandler)
    print(f"🌐 [301-SYSTEM CLOUD SERVER READY] Listening on 0.0.0.0:{PORT}...", flush=True)
    server.serve_forever()

if __name__ == "__main__":
    main()
