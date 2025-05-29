from collections import defaultdict
from datetime import datetime
from summary import summarize
from connect_db import users
from match_utils import get_num, basic_filtering
from random import shuffle

pattern_weights = {
    "sleep": 3,
    "early_bird": 2,
    "air": 1,
    "light_off": 2.7,
    "study": 3,
}
time_pat = ["air", "study", "sleep"]
likely_pat = ["early_bird"]
off_pat = "light_off"

# TODO: study.....
# summary 포맷
# sleep, study, air => 01:01:01-05:05:05
# early_bird, light_off => 0.1
def calc_diff(p1, p2, pattern):
    pat1 = p1[pattern]
    pat2 = p2[pattern]
    if pattern in time_pat:
        time_list = [[[0] * 60 for i in range(60)] for j in range(24)]
        for pat in pat1.split(" ")
        diff = datetime.strptime(pat2, "%H:%M:%S") - datetime.strptime(pat1, "%H:%M:%S")
        d = diff.seconds / 60
        return abs(d)
    elif pattern == off_pat:
        # TODO: 늦게 자는 사람에 가중치 추가
        return (pat1 + pat2) / 2
        """diff = datetime.strptime(p2["sleep"], "%H:%M:%S") - datetime.strptime(p1["sleep"], "%H:%M:%S")
        if diff.seconds > 0:
            return (pat1 ** 2 + pat2) / 2
        elif diff.seconds < 0:
            return (pat1 + pat2 ** 2) / 2
        else:
            return (pat1**2 + pat2**2) / 2"""
    elif pattern in likely_pat:
        return abs(pat1 - pat2)

    raise Exception("Invalid pattern")

def score(data1, data2) -> float:
    sco = 0
    for pattern, weight in pattern_weights.items():
        sco += (
            calc_diff(
                data1["summary"],
                data2["summary"],
                pattern,
            )
            * weight
        )
    return sco

def filtering(data1, data2):
    wake_diff = calc_diff(data1["summary"], data2["summary"], "wake_up")
    sleep_diff = calc_diff(data1["summary"], data2["summary"], "sleep")
    early = calc_diff(data1["summary"], data2["summary"], "early_bird")

    sleep_wake = (
        (wake_diff <= 30 and sleep_diff <= 30)
        or (wake_diff <= 15 and sleep_diff <= 60)
        or (wake_diff <= 60 and sleep_diff <= 15)
        or (wake_diff <= 60 and sleep_diff <= 60 and early >= 0.5)
    )
    return sleep_wake and basic_filtering(data1, data2)


def gen_candidates():
    data1 = list(users.find({"gender": "M", "grade": 1}))
    data2 = list(users.find({"gender": "M", "grade": 2}))
    data3 = list(users.find({"gender": "M", "grade": 3}))
    data4 = list(users.find({"gender": "F", "grade": 1}))
    data5 = list(users.find({"gender": "F", "grade": 2}))
    data6 = list(users.find({"gender": "F", "grade": 3}))
    datas = [data1, data2, data3, data4, data5, data6]
    two_pairs = []
    three_pairs = []
    for data in datas:
        for i, person1 in enumerate(data):
            for j in range(i + 1, len(data)):
                person2 = data[j]
                if filtering(person1, person2):
                    if len(data) % 3 != 0:
                        two_pairs.append((person1, person2))
                    for k in range(j + 1, len(data)):
                        person3 = data[k]
                        if filtering(
                            person3, person2
                        ) and filtering(person3, person1):
                            three_pairs.append(
                                (
                                    person1,
                                    person2,
                                    person3,
                                )
                            )
    return two_pairs, three_pairs

def greedy_matching() -> list[tuple[str, str, str]]:
    data1 = list(users.find({"gender": "M", "grade": 1}))
    data2 = list(users.find({"gender": "M", "grade": 2}))
    data3 = list(users.find({"gender": "M", "grade": 3}))
    data4 = list(users.find({"gender": "F", "grade": 1}))
    data5 = list(users.find({"gender": "F", "grade": 2}))
    data6 = list(users.find({"gender": "F", "grade": 3}))
    shuffle(data1)
    shuffle(data2)
    shuffle(data3)
    shuffle(data4)
    shuffle(data5)
    shuffle(data6)
    datas = [data1, data2, data3, data4, data5, data6]
    students = list(users.find())
    """for student in students:
        summarize(student)"""
    print("Generating candidates")
    two_pairs, three_pairs = gen_candidates()
    print("Finished generation")
    scores = defaultdict(list)
    paired_result = []
    need_twos = [int(len(data) % 3 == 2) if len(data) % 3 != 1 else 2 for data in datas]

    # 필터링을 한 선호도 계산
    for pair in three_pairs:
        score1 = score(pair[0], pair[1])
        score2 = score(pair[1], pair[2])
        score3 = score(pair[2], pair[0])
        scores[(score1 + score2 + score3) / 3].append(pair)
    for pair in two_pairs:
        score1 = score(pair[0], pair[1])
        scores[score1].append(pair)

    # 그리디 매칭
    for sco in sorted(scores.keys(), reverse=True):
        for pair in scores[sco]:
            ind = get_num(pair[0])
            if any((student not in students) for student in pair) or (
                need_twos[ind] == 0 and len(pair) == 2
            ):
                continue
            if len(pair) == 2:
                need_twos[ind] -= 1
            paired_result.append(pair)
            for student in pair:
                students.remove(student)

    # 매칭이 되지 않은 사람들끼리 선호도 계산
    unmatched_pairs = defaultdict(list)
    for i, student1 in enumerate(students):
        for j in range(i + 1, len(students)):
            student2 = students[j]
            if not basic_filtering(student1, student2):
                continue
            score1 = score(student1, student2)
            if need_twos[get_num(student1)] > 0:
                unmatched_pairs[score1].append((student1, student2))
            for k in range(j + 1, len(students)):
                student3 = students[k]
                if (not basic_filtering(student1, student3)) or (not basic_filtering(student2, student3)):
                    continue
                score2 = score(student2, student3)
                score3 = score(student3, student1)
                unmatched_pairs[(score1 + score2 + score3) / 3].append((student1, student2, student3))
        unmatched_pairs[0].append((student1,))

    # 매칭이 되지 않은 사람들끼리 그리디 매칭
    for sco in sorted(unmatched_pairs.keys(), reverse=True):
        for pair in unmatched_pairs[sco]:
            ind = get_num(pair[0])
            if any((student not in students) for student in pair) or (
                need_twos[ind] == 0 and len(pair) == 2
            ):
                continue
            if len(pair) == 2:
                need_twos[ind] -= 1
            paired_result.append(pair)
            for student in pair:
                students.remove(student)

    return paired_result
