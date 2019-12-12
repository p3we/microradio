import sys; sys.path.append('lib')
import ulogging as logging
import uasyncio as asyncio
import picoweb
from machine import Pin, I2C
from uasyncio import get_event_loop
from radio import device, app

ifconfig = sta.ifconfig()
log = logging.getLogger('radio')
log.setLevel(logging.WARNING)
loop = asyncio.get_event_loop()
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
loop.create_task(device.run(i2c))
app.run(ifconfig[0], 80, log=log)
