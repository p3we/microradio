import picoweb
import ujson as json
from ubinascii import hexlify
from .tuner import device

app = picoweb.WebApp('api')


@app.route('/status')
def status(req, resp):
    await picoweb.jsonify(resp, {
        'state': device.state,
        'status': hexlify(device.status),
    })


@app.route('/volume')
def volume(req, resp):
    await req.read_form_data()
    device.volume(int(req.form.get('value', '0')))
    await picoweb.jsonify(resp, {})

@app.route('/tune')
def tune(req, resp):
    await req.read_form_data()
    device.tune(int(req.form.get('value', '87000')))
    await picoweb.jsonify(resp, {})


@app.route('/scan')
def scan(req, resp):
    await req.read_form_data()
    device.tune(int(req.form.get('value', '1')))
    await picoweb.jsonify(resp, {})
