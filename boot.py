# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)
import uos, utime, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
#import webrepl
#webrepl.start()
# configure networking
import network
ap = network.WLAN(network.AP_IF)
ap.active(False)
del ap
sta = network.WLAN(network.STA_IF)
sta.active(False)

try:
    with open('/connect.txt', 'r') as f:
        ssid, passwd = f.read().split(':', 1)
        sta.active(True)
        sta.connect(ssid.strip(), passwd.strip())
        for _ in range(30):
            if sta.isconnected():
                break
            utime.sleep_ms(500)
        else:
            raise RuntimeError('network not connected')
except OSError:
    raise RuntimeError('network not configured')
else:
    print('network address %s' % sta.ifconfig()[0])

gc.collect()
