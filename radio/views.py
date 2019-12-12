import picoweb
from radio.tuner import device

app = picoweb.WebApp('radio')


@app.route('/status')
def status(req, resp):
    await picoweb.jsonify(resp, {
        'state': device.state,
        'volume': device.volume,
        'frequency': device.frequency,
        'stereo': device.stereo,
        'mute': device.mute
    })



@app.route('/mute')
def mute(req, resp):
    await req.read_form_data()
    device.mute = int(req.form.get('value', '0'))
    await picoweb.start_response(resp, 'text/plain', '202')


@app.route('/volume')
def volume(req, resp):
    await req.read_form_data()
    device.volume = int(req.form.get('value', '0'))
    await picoweb.start_response(resp, 'text/plain', '202')


@app.route('/tune')
def tune(req, resp):
    await req.read_form_data()
    device.tune(int(req.form.get('value', '87000')))
    await picoweb.start_response(resp, 'text/plain', '202')


@app.route('/scan')
def scan(req, resp):
    await req.read_form_data()
    device.scan(int(req.form.get('value', '1')))
    await picoweb.start_response(resp, 'text/plain', '202')
