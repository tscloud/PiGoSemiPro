package uk.ac.mdx.cs.jvpi;
 
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
 
import com.pi4j.io.gpio.event.GpioPinListenerDigital;
import com.pi4j.io.gpio.event.GpioPinDigitalStateChangeEvent;
 
public class OnOffStateListener implements GpioPinListenerDigital {
 
	private JvPi jvpi;
 
	private final String height = "720";
	private final String width = "960";
	private final String fps = "15";
	private final String destDir = "/home/pi/capture/";
 
	// Remember to add filename and extension!
	private final String startInstruction = "/usr/bin/raspivid -t 0 -h "+height+ " -w "+width+
			" -o "+destDir;
 
	private final String killInstruction = "killall raspivid";
 
	public OnOffStateListener(JvPi j) {
		this.jvpi = j;
	}
 
	@Override
	public void handleGpioPinDigitalStateChangeEvent(GpioPinDigitalStateChangeEvent event) {
        // display pin state on console
        if (this.jvpi.isCapturing()) {
          System.out.println("Killing raspivid");
          this.jvpi.getRed().low();
          killCapture();
        } else {
          System.out.println("Starting raspivid");
          this.jvpi.getRed().high();
          startCapture();
        }
        this.jvpi.toggleCapture();
 
    }
 
	private void killCapture() {
		executeCommand(this.killInstruction);
	}
 
	private void startCapture() {
		Date date = new Date() ;
		SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd-HH-mm-ss");
		String filename = this.startInstruction + "vid-"+dateFormat.format(date) + ".h264";
		executeCommand(filename);
	}
 
	private void executeCommand(String cmd) {
		Runtime r = Runtime.getRuntime();
		try {
			r.exec(cmd);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
 
 
}