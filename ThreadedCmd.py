import sys
import subprocess
import threading
import time

SOMETHINGCMD = ["omxplayer"]
TIMETOWAITFORABORT = 0.5

#class for controlling the running and shutting down of something (omxplayer for now)
class ThreadedCmd(threading.Thread):

    def __init__(self, filePath, otherOptions=None, cmd=None):
        threading.Thread.__init__(self)

        #setup the cmd
        if cmd:
            self.somethingcmd = cmd
        else:
            self.somethingcmd = SOMETHINGCMD

        #if there are other options, add them
        if otherOptions != None:
            self.somethingcmd = self.somethingcmd + otherOptions
        else:
            #add file path, timeout and preview to options
            self.somethingcmd.append("-o hdmi")
            self.somethingcmd.append(filePath)


        #set state to not running
        self.running = False

    def run(self):
        #run the command
        cmdproc = subprocess.Popen(self.somethingcmd)

        #loop until its set to stopped or it stops
        self.running = True
        while self.running and cmdproc.poll() is None:
            time.sleep(TIMETOWAITFORABORT)
        self.running = False

        #kill process if still running
        if cmdproc.poll() == True:
            cmdproc.kill()

    def stopController(self):
        self.running = False

#test program
if __name__ == '__main__':

    #create command controller
    vidcontrol = ThreadedCmd(None, "-o /home/pi/test.h264 -t 0 -n -w 600 -h 400 -fps 12", "raspivid")
    # vidcontrol = ThreadedCmd("/home/pi/test.h264")

    try:
        print "Starting command controller"
        #start up command controller
        vidcontrol.start()
        #wait for it to finish
        while vidcontrol.isAlive():
            time.sleep(0.5)

    #Ctrl C
    except KeyboardInterrupt:
        print "Cancelled"

    #Error
    except:
        print "Unexpected error:", sys.exc_info()[0]

        raise

    #if it finishes or Ctrl C, shut it down
    finally:
        print "Stopping command controller"
        #stop the controller
        vidcontrol.stopController()
        #wait for the tread to finish if it hasn't already
        vidcontrol.join()

    print "Done"
