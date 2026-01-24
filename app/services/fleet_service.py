from typing import List, Dict
from uuid import UUID

def get_fleet_status() -> Dict:
    return {
        "drivers_online": 7,
        "vehicles_available": 4,
        "drivers": [
            {"id": "d1", "name": "Yossi", "online": True},
            {"id": "d2", "name": "Maya", "online": True},
            {"id": "d3", "name": "Avi", "online": False},
        ],
        "vehicles": [
            {"id": "v1", "type": "Van", "available": True},
            {"id": "v2", "type": "Motorcycle", "available": True},
            {"id": "v3", "type": "Pritve Car", "available": False},
        ]
    }
