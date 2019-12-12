import uasyncio as asyncio
from machine import Pin, I2C
from .tuner import device
from .views import app

def main():
    i2c = device.i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
    loop = asyncio.get_event_loop()
    loop.create_task(device.run(i2c))
