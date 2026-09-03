import json
import os
import random
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen


API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/sensors/readings")
SENSOR_ID = int(os.getenv("SENSOR_ID", "1"))
FIELD_ID = int(os.getenv("FIELD_ID", "1"))
INTERVAL = float(os.getenv("INTERVAL", "10"))


def next_moisture(current: float) -> float:
    return max(0.0, min(100.0, current + random.uniform(-1.2, 0.6)))


def send_reading(moisture: float) -> dict:
    payload = {
        "sensor_id": SENSOR_ID,
        "field_id": FIELD_ID,
        "soil_moisture": round(moisture, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    request = Request(API_URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read())


def main() -> None:
    moisture = float(os.getenv("STARTING_MOISTURE", "42.5"))
    print(f"Sending readings to {API_URL} every {INTERVAL:g}s. Press Ctrl+C to stop.")
    while True:
        moisture = next_moisture(moisture)
        try:
            print(send_reading(moisture), flush=True)
        except Exception as error:
            print(f"Unable to send reading: {error}", flush=True)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()