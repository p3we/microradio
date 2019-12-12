import uasyncio as asyncio
from array import array


TUNER_I2C_SEQ = 0x10
TUNER_I2C_REG = 0x11
STATE_BOOT, STATE_TUNING, STATE_SCANNING, STATE_IDLE = range(4)


class Tuner:

    def __init__(self):
        self.i2c = None
        self.cmd = array('B', b'\xc0\x03\x00\x00\x04\x00\x88\x8b\x00\x00\x42\xc6')
        self.status = array('B', b'\x00\x00')
        self.state = STATE_BOOT

    @property
    def mute(self):
        cmd = memoryview(self.cmd)
        self.i2c.readfrom_mem_into(TUNER_I2C_REG, 0x02, cmd[0:2])
        return (cmd[0] & 0x40) != 0x40

    @mute.setter
    def mute(self, value):
        cmd = memoryview(self.cmd)
        cmd[0] = ((cmd[0] | 0x40) if not value else (cmd[0] & 0xbf))
        self.i2c.writeto(TUNER_I2C_SEQ, cmd[0:2])

    @property
    def volume(self):
        cmd = memoryview(self.cmd)
        self.i2c.readfrom_mem_into(TUNER_I2C_REG, 0x05, cmd[6:8])
        return (cmd[7] & 0x0f)

    @volume.setter
    def volume(self, value):
        assert 0 <= value <= 15
        cmd = memoryview(self.cmd)
        cmd[7] = ((cmd[7] & 0xf0) | (value & 0x0f))
        self.i2c.writeto(TUNER_I2C_SEQ, cmd[0:8])

    @property
    def frequency(self):
        status = memoryview(self.status)
        return (((status[0] & 0x3) | status[1]) + 870) * 100

    @property
    def stereo(self):
        status = memoryview(self.status)
        return (status[1] & 0x04) == 0x04

    def tune(self, value):
        assert 87000 <= value <= 108000
        channel = (value - 87000) // 100
        cmd = memoryview(self.cmd)
        try:
            cmd[2:4] = array('B', [channel >> 2, ((channel << 6) & 0xc0) | (cmd[3] & 0x3f) | 0x10])
            self.i2c.writeto(TUNER_I2C_SEQ, cmd[0:8])
            self.state = STATE_TUNING
        finally:
            cmd[3] &= ~0x10  # disable tune

    def scan(self, direction=1):
        assert direction in (0, 1)
        cmd = memoryview(self.cmd)
        try:
            cmd[0] = ((cmd[0] & 0xfb) | (0x01 if direction == 0 else 0x03))
            self.i2c.writeto(TUNER_I2C_SEQ, cmd[0:8])
            self.state = STATE_SCANNING
        finally:
            cmd[0] &= ~0x01  # disable seek

    def boot(self):
        try:
            self.cmd[1] |= 0x02
            self.i2c.writeto(TUNER_I2C_SEQ, self.cmd)
            self.state = STATE_IDLE
        finally:
            # reset soft-reset flag after boot
            self.cmd[1] &= ~0x02

    async def run(self, i2c=None):
        self.i2c = i2c or self.i2c
        # send boot configuration to the tuner
        while self.state == STATE_BOOT:
            self.boot()
            self.tune(105400)
        # track device status
        while self.state != STATE_BOOT:
            self.i2c.readfrom_into(TUNER_I2C_SEQ, self.status)
            if (self.status[0] & 0x40) == 0x40:
                self.state = STATE_IDLE
            await asyncio.sleep_ms(500)


device = Tuner()
