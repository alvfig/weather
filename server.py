#!/usr/bin/env python


import json
import socketserver
import sys
import time
import RPi.GPIO as GPIO
import Adafruit_DHT as dht


class SingletonDecorator:
    def __init__(self, klass):
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwds):
        if self.instance is None:
            self.instance = self.klass(*args, **kwds)
        return self.instance


@SingletonDecorator
class DhtSensor:
    def __init__(self, pin, interval=2):
        GPIO.setmode(GPIO.BOARD)
        self.sensor = dht.DHT22
        self.pin = pin
        self.interval = interval if 2 <= interval else 2
        self.timestamp = 0
        assert self.interval <= time.time() - self.timestamp
        self.humidity = None
        self.temperature = None
        self.elapsed = None

    def read(self):
        if self.interval <= time.time() - self.timestamp:
            start = time.time()
            humidity, temperature = dht.read(self.sensor, self.pin)
            elapsed = time.time() - start
            if humidity and temperature:
                self.timestamp = time.time()
                self.humidity = humidity
                self.temperature = temperature
                self.elapsed = elapsed
        return self.humidity, self.temperature, self.elapsed, self.timestamp


class MovingAverage:
    def __init__(self, size=25):
        self.size = size
        self.list = []

    def add(self, value):
        self.list.append(value)
        if self.size < len(self.list):
            self.list.pop(0)
        return self.evaluate()

    def evaluate(self):
        if len(self.list) == 0:
            return 0
        return sum(self.list) / len(self.list)


class Weather:
    def __init__(self, sensor):
        self.sensor = sensor
        self.humidity = MovingAverage()
        self.temperature = MovingAverage()
        self.timestamp = time.time()

    def update(self):
        humidity, temperature, elapsed, timestamp = self.sensor.read()
        if humidity and temperature:
            self.humidity.add(humidity)
            self.temperature.add(temperature)
            self.timestamp = timestamp

    def report(self):
        data = {}
        data["humidity"] = self.humidity.evaluate()
        data["temperature"] = self.temperature.evaluate()
        data["timestamp"] = self.timestamp
        return json.dumps(data)


WEATHER = Weather(DhtSensor(18, 30))


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        socket = self.request[1]
        data = WEATHER.report().encode()
        socket.sendto(data, self.client_address)


if __name__ == "__main__":
    serverAddress = ("0.0.0.0", 2020)
    server = socketserver.UDPServer(serverAddress, Handler)
    server.timeout = 5
    while True:
        WEATHER.update()
        server.handle_request()
