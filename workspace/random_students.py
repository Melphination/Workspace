from connect_db import users
import random
import string

genders = ["M", "F"]
grades = [1, 2, 3]

users.insert_many(
    [
        {
            "gender": random.choice(genders),
            "grade": random.choice(grades),
            "username": "".join(
                random.choices(string.ascii_letters + "_", k=random.randint(8, 12))
            ),
            "summary": {
                "wake_up": f"{random.randint(6, 7):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}",
                "sleep": f"{random.randint(0, 2):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}",
                "early_bird": random.random(),
                "light_off": random.random(),
                "air": f"{random.randint(12, 13):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}",
                #"study": ["00:00:00-01:00:00", "23:00:00-00:00:00"],
            },
        }
        for _ in range(150)
    ]
)
