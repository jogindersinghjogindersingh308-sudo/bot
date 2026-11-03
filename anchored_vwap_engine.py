"""
Anchored VWAP Pure Python Engine
Directly translated from official Pine Script: 'Anchored VWAP'
Calculates institutional Session Anchored VWAP (Daily 00:00 UTC / IST), Weekly VWAP,
and provides exact Institutional Average Price Benchmarks.
"""
import datetime

class AnchoredVWAP:
    def __init__(self, use_ohlc4=True):
        self.use_ohlc4 = use_ohlc4

    def analyze(self, candles):
        """
        candles: list of dicts with 'o', 'h', 'l', 'c', 'v', 't'
        sorted chronologically.
        """
        n = len(candles)
        if n < 5:
            return {"error": "Not enough candle data for Anchored VWAP"}

        curr_price = candles[-1]['c']
        last_t = candles[-1]['t']
        last_dt = datetime.datetime.fromtimestamp(last_t, tz=datetime.timezone.utc)
        
        # Start of current UTC day
        start_of_day_utc = datetime.datetime(last_dt.year, last_dt.month, last_dt.day, tzinfo=datetime.timezone.utc).timestamp()
        
        # Start of current week (Monday 00:00 UTC)
        days_since_monday = last_dt.weekday()
        start_of_week_dt = datetime.datetime(last_dt.year, last_dt.month, last_dt.day, tzinfo=datetime.timezone.utc) - datetime.timedelta(days=days_since_monday)
        start_of_week_utc = start_of_week_dt.timestamp()

        # Find Swing High and Swing Low index in lookback
        lookback = min(100, n)
        subset = candles[-lookback:]
        highest_c = max(subset, key=lambda x: x['h'])
        lowest_c = min(subset, key=lambda x: x['l'])

        # 1. Daily Session Anchored VWAP
        daily_vwap_sum = 0.0
        daily_vol_sum = 0.0
        daily_bars = 0

        # 2. Weekly Anchored VWAP
        weekly_vwap_sum = 0.0
        weekly_vol_sum = 0.0
        weekly_bars = 0

        # 3. Swing High Anchored VWAP
        sh_vwap_sum = 0.0
        sh_vol_sum = 0.0

        # 4. Swing Low Anchored VWAP
        sl_vwap_sum = 0.0
        sl_vol_sum = 0.0

        for c in candles:
            t = c['t']
            o = c['o']
            h = c['h']
            l = c['l']
            cl = c['c']
            v = c.get('v', 1.0)
            
            typical = (o + h + l + cl) / 4.0 if self.use_ohlc4 else (h + l + cl) / 3.0
            pv = typical * v

            if t >= start_of_day_utc:
                daily_vwap_sum += pv
                daily_vol_sum += v
                daily_bars += 1

            if t >= start_of_week_utc:
                weekly_vwap_sum += pv
                weekly_vol_sum += v
                weekly_bars += 1

            if t >= highest_c['t']:
                sh_vwap_sum += pv
                sh_vol_sum += v

            if t >= lowest_c['t']:
                sl_vwap_sum += pv
                sl_vol_sum += v

        # Fallback if day just started
        if daily_vol_sum == 0:
            daily_avwap = curr_price
        else:
            daily_avwap = daily_vwap_sum / daily_vol_sum

        if weekly_vol_sum == 0:
            weekly_avwap = curr_price
        else:
            weekly_avwap = weekly_vwap_sum / weekly_vol_sum

        sh_avwap = (sh_vwap_sum / sh_vol_sum) if sh_vol_sum > 0 else curr_price
        sl_avwap = (sl_vwap_sum / sl_vol_sum) if sl_vol_sum > 0 else curr_price

        # Institutional Position Assessment
        diff = curr_price - daily_avwap
        if diff > 0:
            bias = "ABOVE DAILY AVWAP (Institutional Buyers in Profit / Bullish Premium)"
        elif diff < 0:
            bias = "BELOW DAILY AVWAP (Institutional Sellers Dominating / Bearish Discount)"
        else:
            bias = "AT DAILY AVWAP (Equilibrium)"

        return {
            "current_price": curr_price,
            "daily_avwap": round(daily_avwap, 2),
            "weekly_avwap": round(weekly_avwap, 2),
            "swing_high_avwap": round(sh_avwap, 2),
            "swing_low_avwap": round(sl_avwap, 2),
            "distance_to_daily_avwap": round(diff, 2),
            "daily_bars_counted": daily_bars,
            "institutional_bias": bias
        }
