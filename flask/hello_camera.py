import ConfigParser, time
from flask import Flask, render_template
from collections import OrderedDict
app = Flask(__name__)

#read config file
config = ConfigParser.RawConfigParser()
### I think this is weird -- have to do this to make the options not convert to lowercase
config.optionxform = str
# hardcoded - not sure how to pass/set config file
config.read('..\\.config_pigosemipro.cfg')

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = OrderedDict()
pins[config.getint('Pins', 'CAMERAOUT')] = {'name' : 'camera button', 'state' : 1}
pins[config.getint('Pins', 'PLAYEROUT')] = {'name' : 'player button', 'state' : 1}
pins[config.getint('Pins', 'PROGRUNNINGLEDOUT')] = {'name' : 'running light', 'state' : 0}
print 'pins dict: %s' % pins

@app.route("/")
def main():
    templateData = {
        'pins' : pins
        }
    # Pass the template data into the template main_GPIO.html and return it to the user
    return render_template('main_GPIO.html', **templateData)

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<changePin>/toggle")
def action(changePin):
    # Convert the pin from the URL into an integer:
    changePin = int(changePin)
    # Get the device name for the pin being changed:
    deviceName = pins[changePin]['name']
    # simulate button press
    # Read the pin and set it to whatever it isn't (that is, toggle it) and then set it back:
    time.sleep(0.2)
    message = "Toggled " + deviceName + "."

    # Along with the pin dictionary, put the message into the template data dictionary:
    templateData = {
        'message' : message,
        'pins' : pins
    }

    return render_template('main_GPIO.html', **templateData)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8088, debug=True)
