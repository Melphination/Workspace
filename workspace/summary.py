from datetime import datetime
from collections import defaultdict


def summarize(player: str, data):
    times = defaultdict(list)
    res = defaultdict(list)
    for pattern in data[player]["patterns"]:
        match pattern[0]:
            case "wake_up" | "sleep" | "air":
                # TODO: Fix 23:00 and 01:00 -> 12:00 (X), 00:00 (O)
                time = datetime.strptime(pattern[1], "%H:%M:%S")
                times[pattern[0]].append(time.seconds)
            case "early_bird":
                times[pattern[0]].append(pattern[1])
    for key, arr in times.items():
        match key:
            case "wake_up" | "sleep" | "air":
                value = sum(arr) / len(arr)
                hour = value // 3600
                minute = (value % 3600) // 60
                second = value % 60
                res[key] = f"{hour:02d}:{minute:02d}{second:02d}"
            case "early_bird" | "light_off":
                res[key] = arr[0] / arr[1]
            # TODO: "study"
    return res
