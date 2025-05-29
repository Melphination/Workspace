
def get_num(user):
    res = 0
    if user["gender"] == "F":
        res += 3
    res += user["grade"] - 1
    return res

def basic_filtering(data1, data2):
    gender = data1["gender"] == data2["gender"]
    grade = data1["grade"] == data2["grade"]
    return gender and grade
