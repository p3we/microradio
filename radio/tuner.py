import uasyncio as asyncio
import ujson as json
from array import array


TUNER_I2C_SEQ = 0x10
TUNER_I2C_REG = 0x11
STATE_FILE_NAME = 'state.json'
STATE_BOOT, STATE_TUNING, STATE_SCANNING, STATE_IDLE = range(4)


class Control:
    """Simple helper for RDA5807M control instruction."""

    def __init__(self, reg):
        self.reg = reg

    @property
    def mute(self):
        return (self.reg[0] & 0x40) != 0x40

    @mute.setter
    def mute(self, value):
        self.reg[0] = ((self.reg[0] | 0x40) if not value else (self.reg[0] & 0xbf))

    @property
    def volume(self):
        return (self.reg[7] & 0x0f)

    @volume.setter
    def volume(self, value):
        self.reg[7] = ((self.reg[7] & 0xf0) | (value & 0x0f))

    @property
    def channel(self):
        return (self.reg[2] << 2) | ((self.reg[3] & 0xc0) >> 6)

    @channel.setter
    def channel(self, value):
        self.reg[2:4] = array('B', [value >> 2, ((value << 6) & 0xc0) | (self.reg[3] & 0x3f)])


class Tuner:
    """Single Chip Broadcast FM Radio Tuner - RDA5807M"""

    def __init__(self):
        self.i2c = None
        self.control = array('B', b'\xc0\x03\x00\x00\x04\x00\x88\x8b\x00\x00\x42\xc6')
        self.reg = memoryview(self.control)
        self.ctrl = Control(self.reg)
        self.status = array('B', b'\x00\x00')
        self.state = STATE_BOOT
        try:
            self.load()
        except (OSError, ValueError, KeyError):
            self.save()

    @property
    def mute(self):
        self.i2c.readfrom_mem_into(TUNER_I2C_REG, 0x02, self.reg[0:2])
        return self.ctrl.mute

    @mute.setter
    def mute(self, value):
        self.ctrl.mute = value
        self.i2c.writeto(TUNER_I2C_SEQ, self.reg[0:2])
        self.save()

    @property
    def volume(self):
        self.i2c.readfrom_mem_into(TUNER_I2C_REG, 0x05, self.reg[6:8])
        return self.ctrl.volume

    @volume.setter
    def volume(self, value):
        assert 0 <= value <= 15
        self.ctrl.volume = value
        self.i2c.writeto(TUNER_I2C_SEQ, self.reg[0:8])
        self.save()

    @property
    def frequency(self):
        status = memoryview(self.status)
        return (((status[0] & 0x3) | status[1]) + 870) * 100

    @frequency.setter
    def frequency(self, value):
        assert 87000 <= value <= 108000
        channel = (value - 87000) // 100
        self.tune(channel)
        self.save()

    @property
    def stereo(self):
        status = memoryview(self.status)
        return (status[1] & 0x04) == 0x04

    def tune(self, channel):
        try:
            self.ctrl.channel = channel
            self.reg[3] |= 0x10  # enable tune
            self.i2c.writeto(TUNER_I2C_SEQ, self.reg[0:8])
            self.state = STATE_TUNING
        finally:
            self.reg[3] &= ~0x10  # disable tune

    def scan(self, direction=1):
        assert direction in (0, 1)
        try:
            self.reg[0] = ((self.reg[0] & 0xfc) | ((direction << 1) & 0x02))
            self.reg[0] |= 0x01  # enable seek
            self.i2c.writeto(TUNER_I2C_SEQ, self.reg[0:8])
            self.state = STATE_SCANNING
        finally:
            self.reg[0] &= ~0x01  # disable seek

    def boot(self):
        try:
            self.reg[1] |= 0x02
            self.i2c.writeto(TUNER_I2C_SEQ, self.reg)
            self.state = STATE_IDLE
        finally:
            # reset soft-reset flag after boot
            self.reg[1] &= ~0x02

    def save(self):
        with open(STATE_FILE_NAME, 'w') as f:
            state = {
                'mute': self.ctrl.mute,
                'volume': self.ctrl.volume,
                'channel': self.ctrl.channel,
            }
            json.dump(state, f)

    def load(self):
        with open(STATE_FILE_NAME, 'r') as f:
            state = json.load(f)
            self.ctrl.mute = state['mute']
            self.ctrl.volume = state['volume']
            self.ctrl.channel = state['channel']

    async def run(self, i2c=None):
        self.i2c = i2c or self.i2c
        # send boot configuration to the tuner
        while self.state == STATE_BOOT:
            self.boot()
            self.tune(self.ctrl.channel)
        # track device status
        while self.state != STATE_BOOT:
            self.i2c.readfrom_into(TUNER_I2C_SEQ, self.status)
            if (self.status[0] & 0x40) == 0x40:
                self.state = STATE_IDLE
            await asyncio.sleep_ms(500)


device = Tuner()
