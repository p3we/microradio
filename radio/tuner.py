import uasyncio as asyncio
from array import array


TUNER_I2C_ADDR = 0x10
STATE_BOOT, STATE_TUNING, STATE_SCANNING, STATE_IDLE = range(4)


class Tuner:

    def __init__(self):
        self.i2c = None
        self.cmd = array('B', b'\xc0\x03\x00\x00\x04\x00\x88\x8b\x00\x00\x42\xc6')
        self.status = array('B', b'\x00\x00')
        self.state = STATE_BOOT

    def bass_bost(self, value):
        cmd = memoryview(self.cmd)
        cmd[0] = ((self.cmd[0] | 0x08) if value else (self.cmd[0] & 0xf7))
        self.i2c.writeto(TUNER_I2C_ADDR, cmd[0:1])

    def volume(self, value):
        assert 0 <= value <= 15
        cmd = memoryview(self.cmd)
        cmd[7] = ((cmd[7] & 0xf0) | (value & 0x0f))
        self.i2c.writeto(TUNER_I2C_ADDR, cmd[0:8])

    def tune(self, value):
        assert 87000 <= value <= 108000
        channel = (value - 87000) // 100
        cmd = memoryview(self.cmd)
        try:
            cmd[2:4] = array('B', [channel >> 2, ((channel << 6) & 0xc0) | (cmd[3] & 0x3f) | 0x10])
            self.i2c.writeto(TUNER_I2C_ADDR, cmd[0:8])
        finally:
            cmd[3] &= ~0x10  # disable tune

    def scan(self, direction=1):
        assert direction in (0, 1)
        cmd = memoryview(self.cmd)
        try:
            cmd[0] = ((cmd[0] & 0xfb) | (0x01 if direction == 0 else 0x03))
            self.i2c.writeto(TUNER_I2C_ADDR, cmd[0:8])
        finally:
            cmd[0] &= ~0x01  # disable seek

    def boot(self):
        try:
            self.cmd[1] |= 0x02
            self.i2c.writeto(TUNER_I2C_ADDR, self.cmd)
            self.state = STATE_IDLE
        finally:
            # reset soft-reset flag after boot
            self.cmd[1] &= ~0x02

    async def run(self, i2c=None):
        self.i2c = i2c or self.i2c
        # send boot configuration to the tuner
        while self.state == STATE_BOOT:
            self.boot()
        # track device status
        while self.state != STATE_BOOT:
            self.i2c.readfrom_into(TUNER_I2C_ADDR, self.status)
            await asyncio.sleep_ms(100)


device = Tuner()
