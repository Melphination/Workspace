from connect_db import rooms

nums = list(range(201, 299))
nums += list(range(301, 399))
nums += list(range(401, 499))
nums += list(range(501, 599))
rooms.insert_many([{"number": i, "students": tuple(), "floor": i // 100, "place": "old", "reset": False} for i in nums])
