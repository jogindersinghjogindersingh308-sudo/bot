"""
Zeiierman Adaptive Kalman Filter - Trend Strength Oscillator Engine (Official Pine Script Exact Port)
Implements:
- 2x2 State-Space Kalman Filter (Estimate & Velocity/Oscillator)
- Adaptive Measurement & Process Noise
- Trend Strength Percentage: -100% to +100%
- Overbought (> +70%) & Oversold (< -70%) Trend Velocity Exhaustion
"""

class ZeiiermanKalmanEngine:
    def __init__(self, process_noise_1=0.01, process_noise_2=0.01, measurement_noise=500.0, trend_lookback=10, smooth_r=10):
        self.pn1 = process_noise_1
        self.pn2 = process_noise_2
        self.r_noise = measurement_noise
        self.trend_lb = trend_lookback
        self.smooth_r = smooth_r

    def _wma(self, series, period):
        if len(series) < period:
            return series[-1] if series else 0.0
        weights = list(range(1, period + 1))
        weight_sum = sum(weights)
        sub = series[-period:]
        return sum(sub[i] * weights[i] for i in range(period)) / weight_sum

    def analyze(self, candles):
        if len(candles) < 30:
            return {
                "filtered_price": 0.0,
                "trend_strength_pct": 0.0,
                "trend_status": "NEUTRAL",
                "is_overbought": False,
                "is_oversold": False
            }

        # Initialize Kalman Matrices
        # F: 2x2
        F00, F01 = 1.0, 1.0
        F10, F11 = 0.0, 1.0

        # P: 2x2
        P00, P01 = 1.0, 0.0
        P10, P11 = 0.0, 1.0

        # Q: 2x2
        Q00 = self.pn1
        Q01 = self.pn1 * self.pn2
        Q10 = self.pn2 * self.pn1
        Q11 = self.pn2

        R = self.r_noise
        # H = [1.0, 0.0]

        closes = [c['c'] for c in candles]
        X0, X1 = closes[0], 0.0

        osc_buffer = []
        strength_series = []

        for c in closes:
            # Predict
            x1_pred = F00 * X0 + F01 * X1
            x2_pred = F10 * X0 + F11 * X1

            # P_pred = F * P * F^T + Q
            # F * P
            FP00 = F00 * P00 + F01 * P10
            FP01 = F00 * P01 + F01 * P11
            FP10 = F10 * P00 + F11 * P10
            FP11 = F10 * P01 + F11 * P11

            # (F * P) * F^T
            P_pred00 = FP00 * F00 + FP01 * F01 + Q00
            P_pred01 = FP00 * F10 + FP01 * F11 + Q01
            P_pred10 = FP10 * F00 + FP11 * F01 + Q10
            P_pred11 = FP10 * F10 + FP11 * F11 + Q11

            # S = H * P_pred * H^T + R = P_pred00 + R
            S = P_pred00 + R
            inv_S = 1.0 / S if S != 0 else 0.0

            # K = P_pred * H^T * inv_S
            K0 = P_pred00 * inv_S
            K1 = P_pred10 * inv_S

            # Innovation = c - H * X_pred = c - x1_pred
            innov = c - x1_pred

            # Update X
            X0 = x1_pred + K0 * innov
            X1 = x2_pred + K1 * innov

            # Update P = (I - K * H) * P_pred
            P00 = (1.0 - K0) * P_pred00
            P01 = (1.0 - K0) * P_pred01
            P10 = -K1 * P_pred00 + P_pred10
            P11 = -K1 * P_pred01 + P_pred11

            osc_buffer.append(X1)
            if len(osc_buffer) >= self.trend_lb:
                sub_osc = osc_buffer[-self.trend_lb:]
                max_abs = max(abs(x) for x in sub_osc) if sub_osc else 1.0
                if max_abs == 0:
                    max_abs = 1.0
                raw_strength = (X1 / max_abs) * 100.0
                strength_series.append(raw_strength)

        final_strength = self._wma(strength_series, self.smooth_r) if len(strength_series) >= self.smooth_r else (strength_series[-1] if strength_series else 0.0)
        final_strength = round(max(-100.0, min(100.0, final_strength)), 1)

        is_ob = final_strength >= 70.0
        is_os = final_strength <= -70.0

        if is_ob:
            status = f"🔥 OVERBOUGHT VELOCITY ({final_strength}%) - Potential Inflection Top"
        elif is_os:
            status = f"❄️ OVERSOLD VELOCITY ({final_strength}%) - Potential Inflection Bottom"
        elif final_strength > 20.0:
            status = f"🟢 POSITIVE TREND STRENGTH ({final_strength}%)"
        elif final_strength < -20.0:
            status = f"🔴 NEGATIVE TREND STRENGTH ({final_strength}%)"
        else:
            status = f"⚪ NEUTRAL / ACCUMULATION ({final_strength}%)"

        return {
            "filtered_price": round(X0, 1),
            "trend_strength_pct": final_strength,
            "trend_status": status,
            "is_overbought": is_ob,
            "is_oversold": is_os
        }
