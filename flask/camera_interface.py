#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import ConfigParser, time, os
from flask import Flask, render_template
from collections import OrderedDict
app = Flask(__name__)

GPIO.setmode(GPIO.BOARD)

#read config file
config = ConfigParser.RawConfigParser()
### I think this is weird -- have to do this to make the options not convert to lowercase
config.optionxform = str
# hardcoded - not sure how to pass/set config file
config_file = '%s/.config_pigosemipro.cfg' % os.getenv('DAEMONPATH', '..')
print "*** config_file: %s" % config_file
config.read(config_file)

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = OrderedDict()
pins[config.getint('Pins', 'CAMERAOUT')] = {'name' : 'camera button', 'state' : GPIO.HIGH}
pins[config.getint('Pins', 'PLAYEROUT')] = {'name' : 'player button', 'state' : GPIO.HIGH}
# pins[config.getint('Pins', 'PROGRUNNINGLEDOUT')] = {'name' : 'running light', 'state' : GPIO.LOW}

# Set each pin
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, pins[pin]['state'])

# write PID file
pid = str(os.getpid())
f = open('/var/run/flask-pi', 'w')
f.write(pid)
f.close()

def serviceStatus():
    # check status of PiGoSemiPro service
    camStatusCmd = os.popen('service pigosemipro_serv status')
    camStatusMsg = camStatusCmd.read()
    if "failed" in camStatusMsg:
        # service not started
        return "start"
    else:
        return "stop"
    
@app.route("/")
def main():
    # Put the pin dictionary into the template data dictionary:
    templateData = {
        'pins' : pins,
        'startStopBtnMsg' : serviceStatus().capitalize()
        }
    # Pass the template data into the template main_GPIO.html and return it to the user
    return render_template('main_GPIO.html', **templateData)

# The function below is executed when someone requests a URL with the pin number
@app.route("/<changePin>/toggle")
def action(changePin):
    # Convert the pin from the URL into an integer:
    changePin = int(changePin)
    # Get the device name for the pin being changed:
    deviceName = pins[changePin]['name']
    # simulate button press
    # Read the pin and set it to whatever it isn't (that is, toggle it) and then set it back:
    GPIO.output(changePin, not GPIO.input(changePin))
    time.sleep(1.2)
    GPIO.output(changePin, not GPIO.input(changePin))
    message = "Toggled " + deviceName + "."

    # Along with the pin dictionary, put the message into the template data dictionary:
    templateData = {
        'pins' : pins,
        'message' : message,
        'startStopBtnMsg' : serviceStatus().capitalize()
    }

    return render_template('main_GPIO.html', **templateData)

# The function below is executed when someone hits start button
@app.route("/startstop")
def startStopCam():
    #start or stop the cam
    camCmd = os.popen('service pigosemipro_serv %s' % serviceStatus())
    camMsg = camCmd.read()
    
    # wait for service to start/stop
    time.sleep(2)
    
    # Put the message into the template data dictionary, still need to send the pins:
    templateData = {
        'pins' : pins,
        'message' : camMsg,
        'startStopBtnMsg' : serviceStatus().capitalize()
    }
    
    return render_template('main_GPIO.html', **templateData)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8088, debug=True)
