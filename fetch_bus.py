#!/usr/bin/env python3
import requests
import json
from datetime import datetime, timezone
import time

# ----------------------------
# CONFIGURATION
# ----------------------------
API_KEY = ""
BUS_STOP_IDS = {
    "UPTOWN": "403103",
    "DOWNTOWN": "403167"
}
MAX_ARRIVALS = 5          # How many upcoming arrivals to fetch per stop
OUTPUT_FILE = "bus_data.json"

# MTA SIRI Stop Monitoring API endpoint
API_URL = "https://bustime.mta.info/api/siri/stop-monitoring.json"

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def fetch_stop(stop_id):
    """Fetch arrivals for a single bus stop."""
    params = {
        "key": API_KEY,
        "MonitoringRef": stop_id,
        "MaximumStopVisits": MAX_ARRIVALS
    }
    resp = requests.get(API_URL, params=params)
    resp.raise_for_status()  # raise error if request fails
    data = resp.json()
    
    arrivals = []
    try:
        stop_visits = data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]
        now = datetime.now(timezone.utc)
        for visit in stop_visits:
            journey = visit["MonitoredVehicleJourney"]
            line = journey["PublishedLineName"]
            expected_iso = journey["MonitoredCall"]["ExpectedArrivalTime"]
            expected_dt = datetime.fromisoformat(expected_iso.replace("Z", "+00:00"))
            minutes = int((expected_dt - now).total_seconds() / 60)
            if minutes >= 0:
                arrivals.append(minutes)
    except (KeyError, IndexError):
        pass  # no arrivals found

    arrivals.sort()
    return arrivals[:MAX_ARRIVALS]

# ----------------------------
# MAIN SCRIPT
# ----------------------------
def main():
    all_arrivals = {}
    timestamp = int(time.time())

    for direction, stop_id in BUS_STOP_IDS.items():
        arrivals = fetch_stop(stop_id)
        all_arrivals[direction] = arrivals

    output = {
        "timestamp": timestamp,
        "bus": all_arrivals
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f)
    
    # print(f"Fetched bus data: {output}")

if __name__ == "__main__":
    main()

