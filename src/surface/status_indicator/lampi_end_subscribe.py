from paho.mqtt import subscribe  # noqa: INP001

while True:
    msg = subscribe.simple('hiMqtt', hostname='localhost')
    print('lampi_end:')
    # print(f'{msg.topic} Pi Connected: {msg.payload[4]} Ardusub Connected {msg.payload[5]} Armed {msg.payload[6]}')

    pi_connected = bool(msg.payload[4])

    ardusub_connected = bool(msg.payload[5])

    armed = bool(msg.payload[6])

    print(f'{msg.topic} Pi Connected: {pi_connected} Ardusub Connected {ardusub_connected} Armed {armed}')