from tinyweb import webserver
from tinyweb.server import HTTPException
from radio.tuner import device

app = webserver()


@app.resource('/status', method='GET')
def status(params):
    status = {
        'state': device.state,
        'volume': device.volume,
        'frequency': device.frequency,
        'stereo': device.stereo,
        'mute': device.mute
    }
    return (status, 200)


@app.resource('/mute', method='PUT')
def mute(params):
    try:
        device.mute = int(params.get('value'))
    except ValueError:
        raise HTTPException(400)
    return ('', 202)


@app.resource('/volume', method='PUT')
def volume(params):
    try:
        device.volume = int(params.get('value'))
    except ValueError:
        raise HTTPException(400)
    return ('', 202)


@app.resource('/tune', method='PUT')
def tune(params):
    try:
        device.frequency = int(params.get('value'))
    except ValueError:
        raise HTTPException(400)
    return ('', 202)


@app.resource('/scan', method='POST')
def scan(params):
    try:
        device.scan(int(params.get('value')))
    except ValueError:
        raise HTTPException(400)
    return ('', 202)
