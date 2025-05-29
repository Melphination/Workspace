from tkinter import ttk
from tksheet import Sheet
from connect_db import rooms
from matcher import greedy_matching
from match_utils import get_num
from random import shuffle
from nava import play

root = None

def start_matching():
    play("./sounds/button.mp3")
    matched = greedy_matching()
    print("Greedy matching finished")
    shuffle(matched)
    print(len(matched))
    for pair in matched:
        match get_num(pair[0]):
            case 0:
                room = rooms.find_one({"floor": 5, "reset": False})
            case 1:
                room = rooms.find_one({"floor": 4, "reset": False})
            case 2:
                room = rooms.find_one({"floor": 3, "reset": False})
            case 3 | 4 | 5:
                room = rooms.find_one({"floor": 2, "reset": False})
        rooms.update_one(room, {"$set": {"reset": True, "students": pair}})
    print("Each pair got their room")
    for room in rooms.find():
        if not room["reset"]:
            rooms.update_one(room, {"$set": {"students": tuple()}})
        else:
            rooms.update_one(room, {"$set": {"reset": False}})
    print("Matching finished")


def matcher_ui(rt):
    global root
    root = rt
    match_button = ttk.Button(root, text="새로운 룸메이트 매칭?", command=start_matching)
    match_button.pack()
    rooms_sheet = Sheet(
        root,
        data=[[room["number"], *[student["username"] for student in room["students"]]] for room in rooms.find()],
        height=520,
        width=200,
    )
    rooms_sheet.pack()
