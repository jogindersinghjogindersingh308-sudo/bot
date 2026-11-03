"""
Engine #15: Institutional Dynamic Support & Resistance Clusters (Heatmap)
Clusters multi-touch pivot highs and pivot lows into high-probability supply & demand zones:
- Identifies major horizontal clusters with 2+ touches
- Measures cluster density & proximity to current price
- Computes nearest institutional wall (Supply overhead vs Demand beneath)
"""

class DynamicSRHeatmap:
    def __init__(self, pivot_left=3, pivot_right=3, cluster_tolerance=0.003):
        self.pivot_left = pivot_left
        self.pivot_right = pivot_right
        self.cluster_tolerance = cluster_tolerance

    def analyze(self, candles):
        if len(candles) < (self.pivot_left + self.pivot_right + 10):
            return {
                "strongest_support": 0.0,
                "strongest_resistance": 0.0,
                "sr_status": "NORMAL"
            }

        pivots = []
        n = len(candles)
        for i in range(self.pivot_left, n - self.pivot_right):
            high = candles[i]['h']
            low = candles[i]['l']
            is_pivot_high = all(high >= candles[j]['h'] for j in range(i - self.pivot_left, i + self.pivot_right + 1) if j != i)
            is_pivot_low = all(low <= candles[j]['l'] for j in range(i - self.pivot_left, i + self.pivot_right + 1) if j != i)

            if is_pivot_high:
                pivots.append(("H", high))
            if is_pivot_low:
                pivots.append(("L", low))

        curr_price = candles[-1]['c']

        # Cluster pivots
        clusters = []
        for p_type, price in pivots:
            matched = False
            for c in clusters:
                if abs(price - c['price']) / c['price'] <= self.cluster_tolerance:
                    c['count'] += 1
                    c['prices'].append(price)
                    c['price'] = sum(c['prices']) / len(c['prices'])
                    matched = True
                    break
            if not matched:
                clusters.append({'price': price, 'count': 1, 'prices': [price], 'type': p_type})

        # Filter clusters with >= 2 touches
        strong_clusters = [c for c in clusters if c['count'] >= 2]
        if not strong_clusters:
            strong_clusters = clusters

        supports = [c for c in strong_clusters if c['price'] < curr_price]
        resistances = [c for c in strong_clusters if c['price'] > curr_price]

        nearest_supp = max(supports, key=lambda x: x['price']) if supports else None
        nearest_res = min(resistances, key=lambda x: x['price']) if resistances else None

        supp_price = nearest_supp['price'] if nearest_supp else curr_price * 0.98
        res_price = nearest_res['price'] if nearest_res else curr_price * 1.02

        return {
            "strongest_support": round(supp_price, 1),
            "support_touches": nearest_supp['count'] if nearest_supp else 1,
            "strongest_resistance": round(res_price, 1),
            "resistance_touches": nearest_res['count'] if nearest_res else 1,
            "sr_status": f"Channel Range: [${supp_price:,.1f} SUPP] <---> [${res_price:,.1f} RES]"
        }
