package uk.ac.mdx.cs.jvpi;
 
import com.pi4j.io.gpio.GpioController;
import com.pi4j.io.gpio.GpioFactory;
import com.pi4j.io.gpio.GpioPinDigitalInput;
import com.pi4j.io.gpio.GpioPinDigitalOutput;
import com.pi4j.io.gpio.Pin;
import com.pi4j.io.gpio.PinPullResistance;
import com.pi4j.io.gpio.RaspiPin;
import com.pi4j.io.gpio.event.GpioPinDigitalStateChangeEvent;
import com.pi4j.io.gpio.event.GpioPinListenerDigital;
 
public class JvPi {
 
	// This is the controller.
	private GpioController gpio;
 
	// The current pin mapping
	private static final Pin redPin =  RaspiPin.GPIO_01;
	private static final Pin greenPin = RaspiPin.GPIO_02;
	private static final Pin switchPin = RaspiPin.GPIO_14;
 
	// The pins to which we attach LEDs
	private GpioPinDigitalOutput red,green;
 
	// this is going to be an input PULL_UP, see below.
	private GpioPinDigitalInput onOffSwitch;
 
	// set to true when capturing
	private boolean capturing;
 
	// Main method
	public JvPi() {
		this.gpio = GpioFactory.getInstance();
		this.red = gpio.provisionDigitalOutputPin(redPin);
		this.green = gpio.provisionDigitalOutputPin(greenPin);
		this.onOffSwitch = gpio.provisionDigitalInputPin(switchPin, PinPullResistance.PULL_UP);
 
		// The listener takes care of turning on and off the camera and the red LED	
		onOffSwitch.addListener(new OnOffStateListener(this));
	}
 
	public boolean isCapturing() {
		return this.capturing;
	}
 
	public void toggleCapture() {
		this.capturing = !this.capturing;
	}
 
	public GpioPinDigitalOutput getRed() {
		return this.red;
	}
 
	public GpioPinDigitalOutput getGreen() {
		return this.green;
	}
 
	public static void main(String[] args) {
		JvPi jvpi = new JvPi();
		jvpi.getGreen().high();
		System.out.println("System started");
		while (true) {
			try {
				Thread.sleep(1000);
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}
 
}