#!/usr/bin/env python


import Adafruit_DHT as dht
import RPi.GPIO as GPIO
import time
import sys


GPIO.setmode(GPIO.BOARD)
sensor = dht.DHT22
pin = 18
header = "Umidade  Temperatura"
format = " {:02.2f}%      {:02.2f}°C  {:.4f}s"
humidityList, temperatureList = [], []
count = 0
while True:
    if count % 15 == 0:
        count = 0
        print(header)
    count += 1
    start = time.time()
    humidity, temperature = dht.read_retry(sensor, pin)
    elapsed = time.time() - start
    if humidity and temperature:
        humidityList.append(humidity)
        if 25 < len(humidityList):
            humidityList.pop(0)
        humidity = sum(humidityList) / len(humidityList)
        temperatureList.append(temperature)
        if 25 < len(temperatureList):
            temperatureList.pop(0)
        temperature = sum(temperatureList) / len(temperatureList)
        print(format.format(humidity, temperature, elapsed))
    else:
        print("falha de leitura do sensor", file=sys.stderr)
    time.sleep(5)
