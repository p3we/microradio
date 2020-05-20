import sys; sys.path.extend(['lib'])
import logging
import uasyncio as asyncio
from uasyncio import get_event_loop
from radio import device, app


log = logging.getLogger('WEB')
log.setLevel(logging.DEBUG)

class FakeI2C:

    def readfrom_into(self, *args, **kwargs):
        log.info('readfrom_into: %s', args)
        return None

    def readfrom_mem_into(self, *args, **kwargs):
        log.info('readfrom_mem_into: %s', args)
        return None

    def writeto(self, *args, **kwargs):
        log.info('writeto: %s', args)
        return None


loop = asyncio.get_event_loop()
loop.create_task(device.run(FakeI2C()))
app.run("0.0.0.0", 8080)
