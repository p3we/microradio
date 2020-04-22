import logging
import uasyncio as asyncio
from machine import Pin, I2C
from uasyncio import get_event_loop
from radio import device, app

ifconfig = sta.ifconfig()  # sta is a configured network device
log = logging.getLogger('radio')
log.setLevel(logging.INFO)
loop = asyncio.get_event_loop()
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
loop.create_task(device.run(i2c))
app.run(ifconfig[0], 80)
