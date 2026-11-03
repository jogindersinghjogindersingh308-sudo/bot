"""
Engine #11: ICT Kill Zones & Macro Delivery Windows (Pine Script Exact Port)
Tracks ICT Sessions & High-Probability Execution Macro Windows (NY Time America/New_York):
- Sessions: Asian (20:00-00:00 NY), London Open (02:00-05:00 NY), NY Open (08:30-11:00 NY), Silver Bullet (10:00-11:00 NY)
- Intra-hour Micro-Macros:
  * Macro :50 -> :10 (Hourly Algo Delivery Cycle)
  * Macro :20 -> :40 (Mid-Hour Injections - 02:20, 03:20, 07:20, 08:20, 09:20, 10:20 NY)
  * Macro :45 -> :15
"""
import datetime
from zoneinfo import ZoneInfo

class ICTKillZonesEngine:
    def __init__(self):
        self.ny_tz = ZoneInfo("America/New_York")

    def analyze(self, candles):
        now_ny = datetime.datetime.now(self.ny_tz)
        h = now_ny.hour
        m = now_ny.minute
        time_dec = h + m / 60.0

        # Session detection (New York Time)
        is_asian = (h >= 20 or h < 0)
        is_london = (2 <= h < 5)
        is_ny_open = (8.5 <= time_dec <= 11.0)
        is_silver_bullet = (10.0 <= time_dec <= 11.0)
        is_ny_close = (13.0 <= time_dec <= 16.0)

        session_name = "Off-Hours"
        is_killzone = False
        if is_silver_bullet:
            session_name = "SILVER BULLET KILLZONE (10:00 - 11:00 NY)"
            is_killzone = True
        elif is_ny_open:
            session_name = "NEW YORK OPEN KILLZONE (08:30 - 11:00 NY)"
            is_killzone = True
        elif is_london:
            session_name = "LONDON OPEN KILLZONE (02:00 - 05:00 NY)"
            is_killzone = True
        elif is_ny_close:
            session_name = "NEW YORK PM / CLOSE (13:00 - 16:00 NY)"
            is_killzone = True
        elif is_asian:
            session_name = "ASIAN SESSION (20:00 - 00:00 NY)"

        # Micro Macros
        macro_50_10 = (m >= 50 or m < 10)
        macro_20_40 = (20 <= m <= 40) and (h in [2, 3, 4, 7, 8, 9, 10, 13, 14])
        macro_45_15 = (m >= 45 or m <= 15)

        active_macros = []
        if macro_50_10:
            active_macros.append("Macro :50->:10 (Hourly Algo Delivery)")
        if macro_20_40:
            active_macros.append("Macro :20->:40 (Mid-Hour Institutional Injection)")
        if not active_macros and macro_45_15:
            active_macros.append("Macro :45->:15")

        macro_status = " | ".join(active_macros) if active_macros else "Inter-Macro Range"

        return {
            "ny_time": f"{h:02d}:{m:02d} NY",
            "current_session": session_name,
            "is_killzone": is_killzone,
            "active_macro": macro_status,
            "is_macro_active": len(active_macros) > 0
        }
