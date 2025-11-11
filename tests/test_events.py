import requests
import json
from datetime import datetime

# URL нашего сервиса
url = "http://localhost:8000/api/events"

# Тестовые события
test_events = [
    {
        "user_id": "user_001",
        "event_type": "page_view",
        "page": "/home",
        "timestamp": datetime.utcnow().isoformat()
    },
    {
        "user_id": "user_001",
        "event_type": "page_view",
        "page": "/products/iphone",
        "timestamp": datetime.utcnow().isoformat()
    },
    {
        "user_id": "user_002",
        "event_type": "add_to_cart",
        "page": "/products/iphone",
        "timestamp": datetime.utcnow().isoformat()
    }
]

# Отправляем события
for event in test_events:
    response = requests.post(url, json=event)
    print(f"Status: {response.status_code}, Response: {response.json()}")
