#!/usr/bin/python

import datetime as dt
import json
import socket as skt

host = skt.gethostbyname('localhost')
# host = skt.gethostbyname('192.168.0.100')
port = 2020
server = (host, port)
timestamp = 0
headerCount = 0
sock = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
try:
    sock.settimeout(10)

    while True:
        try:
            sock.sendto(b'x', server)
            data, address = sock.recvfrom(1024)
            if address != server:
                print(f'Dados inesperados de {address}')
                continue
        except skt.timeout:
            continue
        data = json.loads(data.decode())
        if data['timestamp'] != timestamp:
            timestamp = data['timestamp']
            humidity = data['humidity']
            temperature = data['temperature']
            hour = dt.datetime.fromtimestamp(timestamp).time()
            hour = hour.isoformat(timespec='seconds')
            if headerCount % 15 == 0:
                headerCount = 0
                print(' Leitura  Umidade  Temperatura')
            headerCount += 1
            fstring = \
                f'{hour}     {humidity:02.0f} %      {temperature:02.1f} °C'
            print(fstring)

except KeyboardInterrupt:
    pass
finally:
    sock.close()
