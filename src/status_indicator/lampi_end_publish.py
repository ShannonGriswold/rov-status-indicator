import time

from paho.mqtt import publish

while True:
    payload = 'true'
    publish.single('/hi', payload, hostname='localhost')
    print(payload)
    time.sleep(3)
    payload = 'false'
    publish.single('/hi', payload, hostname='localhost')
    print(payload)
    time.sleep(3)
