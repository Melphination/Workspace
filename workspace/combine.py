import json


def dupli(start1, end1, start2, end2):
    return (start1 <= start2 < end1) or (start2 <= start1 < end2)


def combine():
    data = json.load(open("./patterns.json", "r"))

    for key, values in data[1].items():
        for value in values:
            for v in data[0].get(key, {}):
                if dupli(value["start"], value["end"], v["start"], v["end"]):
                    data[0][key].remove(value)
                    break
    return data
