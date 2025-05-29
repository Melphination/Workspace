from sensor import Sensor
import threading

# 사용할 센서의 고유 id를 담은 리스트
# 1: 창문의 닫힘 여부 센서, 2: 불 꺼짐 여부 센서
ids = [1, 2, 3, 4, 5]
# 사용할 센서의 Sensor를 담은 리스트
"""sensors = [Sensor(i) for i in ids]
# 각각의 센서로부터 데이터를 동시에 받기 위한 thread를 담은 리스트
threads = [threading.Thread(sensor.listen) for sensor in sensors]

for thread in threads:
    thread.start()
"""