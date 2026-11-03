"""
LuxAlgo Nadaraya-Watson Envelope Engine (Official Pine Script Exact Port)
Implements:
- Gaussian Kernel Weighting: gauss(x, h) = exp(-(x^2) / (2 * h^2))
- Kernel Regression Smooth Curve (out)
- Mean Absolute Error (MAE) Envelope Bands: Upper = out + mae, Lower = out - mae
- Overbought (Above Upper Band) & Oversold (Below Lower Band) Inflection Reversal Signals
"""
import math

class NadarayaWatsonEnvelopeEngine:
    def __init__(self, h=8.0, mult=3.0, lookback=100):
        self.h = h
        self.mult = mult
        self.lookback = lookback
        # Precompute Gaussian weights
        self.weights = [math.exp(-(i ** 2) / (2.0 * (self.h ** 2))) for i in range(self.lookback)]
        self.weight_sum = sum(self.weights)

    def analyze(self, candles):
        if len(candles) < self.lookback:
            return {
                "nwe_out": 0.0,
                "upper_band": 0.0,
                "lower_band": 0.0,
                "envelope_status": "NORMAL",
                "inflection_arrow": "NONE"
            }

        closes = [c['c'] for c in candles[-self.lookback:]]
        # Endpoint calculation using Gaussian Kernel weights
        out = sum(closes[len(closes) - 1 - i] * self.weights[i] for i in range(self.lookback)) / self.weight_sum

        # Calculate Mean Absolute Error (MAE) over the window
        errors = [abs(c - out) for c in closes]
        mae = (sum(errors) / len(errors)) * self.mult

        upper = round(out + mae, 1)
        lower = round(out - mae, 1)
        out = round(out, 1)
        curr_price = closes[-1]
        prev_price = closes[-2] if len(closes) >= 2 else curr_price

        # Inflection signals
        arrow = "NONE"
        status = "INSIDE ENVELOPE (Normal Equilibrium)"
        if curr_price < lower:
            status = f"OVERSOLD BELOW ENVELOPE (Discount < ${lower:,.1f})"
            if prev_price <= lower and curr_price > prev_price:
                arrow = "▲ BULLISH REVERSAL ARROW (Bounced off Nadaraya-Watson Lower Band)"
        elif curr_price > upper:
            status = f"OVERBOUGHT ABOVE ENVELOPE (Premium > ${upper:,.1f})"
            if prev_price >= upper and curr_price < prev_price:
                arrow = "▼ BEARISH REVERSAL ARROW (Rejected by Nadaraya-Watson Upper Band)"

        return {
            "nwe_out": out,
            "upper_band": upper,
            "lower_band": lower,
            "envelope_status": status,
            "inflection_arrow": arrow
        }
