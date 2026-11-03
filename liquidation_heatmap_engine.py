"""
Liquidation Heatmap & Whale Magnet Engine
Ported & Adapted from agiprolabs/claude-trading-skills institutional quantitative models.
Calculates high-density liquidation clusters for 25x, 50x, and 100x leverage on BTCUSD.
Identifies Whale Liquidation Magnets (Where big players will hunt retail stop-losses).
"""
import math

class LiquidationHeatmapEngine:
    def __init__(self):
        # Standard retail leverage distribution in Crypto Perpetual Futures
        self.leverage_tiers = [
            {"leverage": 100, "liq_dist_pct": 0.008, "est_weight": 0.25}, # 0.8% away
            {"leverage": 50,  "liq_dist_pct": 0.018, "est_weight": 0.40}, # 1.8% away
            {"leverage": 25,  "liq_dist_pct": 0.038, "est_weight": 0.25}, # 3.8% away
            {"leverage": 10,  "liq_dist_pct": 0.095, "est_weight": 0.10}, # 9.5% away
        ]

    def calculate_heatmap(self, candles_1h, current_price):
        """
        Calculates Upper (Short Liquidations) and Lower (Long Liquidations) clusters.
        """
        if not candles_1h or len(candles_1h) < 10:
            return {
                "status": "INSUFFICIENT_DATA",
                "nearest_short_cluster": current_price * 1.015,
                "nearest_long_cluster": current_price * 0.985,
                "whale_magnet": "NEUTRAL"
            }

        highs = [float(c["h"]) for c in candles_1h]
        lows = [float(c["l"]) for c in candles_1h]
        volumes = [float(c.get("v", 1000)) for c in candles_1h]

        recent_swing_high = max(highs[-24:]) # 24h high
        recent_swing_low = min(lows[-24:])   # 24h low
        avg_vol = sum(volumes[-24:]) / len(volumes[-24:])

        # Short liquidation clusters (Above current price / resistance)
        short_clusters = []
        for tier in self.leverage_tiers:
            liq_price = recent_swing_high * (1.0 + tier["liq_dist_pct"])
            est_volume = avg_vol * tier["est_weight"] * 1.6
            short_clusters.append({
                "leverage": f"{tier['leverage']}x Shorts",
                "liquidation_price": round(liq_price, 1),
                "distance_pct": round(((liq_price - current_price) / current_price) * 100, 2),
                "est_liquidated_contracts": int(est_volume)
            })

        # Long liquidation clusters (Below current price / support)
        long_clusters = []
        for tier in self.leverage_tiers:
            liq_price = recent_swing_low * (1.0 - tier["liq_dist_pct"])
            est_volume = avg_vol * tier["est_weight"] * 1.6
            long_clusters.append({
                "leverage": f"{tier['leverage']}x Longs",
                "liquidation_price": round(liq_price, 1),
                "distance_pct": round(((current_price - liq_price) / current_price) * 100, 2),
                "est_liquidated_contracts": int(est_volume)
            })

        # Find Nearest Dense Clusters
        nearest_short = min(short_clusters, key=lambda x: abs(x["liquidation_price"] - current_price))
        nearest_long = min(long_clusters, key=lambda x: abs(x["liquidation_price"] - current_price))

        # Whale Magnet Determination
        dist_to_short = abs(nearest_short["liquidation_price"] - current_price)
        dist_to_long = abs(nearest_long["liquidation_price"] - current_price)

        if dist_to_short < dist_to_long:
            whale_magnet = "BULLISH MAGNET (SHORT SQUEEZE POOL)"
            target_cluster = nearest_short
        else:
            whale_magnet = "BEARISH MAGNET (LONG FLUSH POOL)"
            target_cluster = nearest_long

        return {
            "status": "SUCCESS",
            "current_price": current_price,
            "recent_24h_swing_high": recent_swing_high,
            "recent_24h_swing_low": recent_swing_low,
            "nearest_short_cluster": nearest_short,
            "nearest_long_cluster": nearest_long,
            "short_clusters": short_clusters,
            "long_clusters": long_clusters,
            "whale_magnet_direction": whale_magnet,
            "primary_magnet_target": target_cluster["liquidation_price"],
            "magnet_distance_pct": target_cluster["distance_pct"]
        }

if __name__ == "__main__":
    import urllib.request, json
    engine = LiquidationHeatmapEngine()
    # Test run with sample data
    test_candles = [
        {"h": 77800, "l": 77200, "c": 77600, "v": 150000} for _ in range(25)
    ]
    res = engine.calculate_heatmap(test_candles, 77650.0)
    print("Liquidation Heatmap Test:", json.dumps(res, indent=2))
