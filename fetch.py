import requests
from google.transit import gtfs_realtime_pb2
import time
import json

FEED_URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs"

# Map directions to stop IDs
STOP_IDS = {
    "UPTOWN": "123N",
    "DOWNTOWN": "123S"
}

OUTPUT_FILE = "subway_data.json"

def get_train_times():
    headers = {}
    feed = gtfs_realtime_pb2.FeedMessage()

    resp = requests.get(FEED_URL, headers=headers)
    feed.ParseFromString(resp.content)

    #print(f"Feed has {len(feed.entity)} entities")

    now = int(time.time())
    arrivals = {direction: [] for direction in STOP_IDS}

    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue

        for stu in entity.trip_update.stop_time_update:
            for direction, stop_id in STOP_IDS.items():
                if stu.stop_id == stop_id and stu.arrival.time: 
                    minutes = (stu.arrival.time - now) / 60
                    if 0 <= minutes <= 30:
                        arrivals[direction].append(round(minutes))

    # sort times for each direction and keep only the next two
    for direction in arrivals:
        arrivals[direction].sort()
        arrivals[direction] = arrivals[direction][:5]

    return arrivals

if __name__ == "__main__":
    arrivals = get_train_times()

    output = {
        "timestamp": int(time.time()),
        "subway": arrivals
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f)

    #print(f"Saved subway data to {OUTPUT_FILE}:")
    #print(json.dumps(output, indent=2))
