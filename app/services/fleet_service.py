from typing import List, Dict
from uuid import UUID

def get_fleet_status() -> Dict:
    # מימוש לדוגמה: שליפת סטטוס של נהגים ורכבים
    # כאן אפשר להרחיב לנתונים אמיתיים מה־DB
    return {
        "drivers_online": 7,
        "vehicles_available": 4,
        "drivers": [
            {"id": "d1", "name": "יוסי", "online": True},
            {"id": "d2", "name": "שרה", "online": True},
            {"id": "d3", "name": "אבי", "online": False},
        ],
        "vehicles": [
            {"id": "v1", "type": "מסחרית", "available": True},
            {"id": "v2", "type": "אופנוע", "available": True},
            {"id": "v3", "type": "רכב פרטי", "available": False},
        ]
    }
