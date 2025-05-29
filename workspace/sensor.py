import random


class Sensor:
    def __init__(self, sensor_id, user):
        # sensor_id: 각각의 센서만의 고유의 id
        self.id = sensor_id
        # user: 누구를 대상으로 한 것인지 알려줌
        # 만약 특정 대상이 없다면 ....
        self.user = user

    def input(self):
        # 실제 센서가 없으니 랜덤 데이터를 내보냄
        if self.id == 0:
            return random.randint(1, 10)

    def listen(self):
        while True:
            if random.random() < 0.01:
                pass
