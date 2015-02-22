#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import signal
import os
import subprocess
import threading
import time

TIMETOWAITFORABORT = 0.5

#class for controlling the running and shutting down of something (omxplayer for now)
class ThreadedCmd(threading.Thread):

    def __init__(self, cmd=None, otherOptions=None):
        threading.Thread.__init__(self)

        #if there are other options, add them
        self.somethingcmd = None
        if cmd != None:
            self.somethingcmd = "%s %s" % (cmd, otherOptions)
        else:
            raise ValueError("Must specify command")

        #set state to not running
        self.running = False

    def run(self):
        #run the command
        print '###\n%s\n###' % self.somethingcmd
        cmdproc = subprocess.Popen(self.somethingcmd, shell=True,
                                   stdout=subprocess.PIPE, preexec_fn=os.setsid)

        #loop until its set to stopped or it stops
        self.running = True
        while self.running and cmdproc.poll() is None:
            time.sleep(TIMETOWAITFORABORT)
        self.running = False

        #kill process if still running
        print 'ThreadedCmd: about to kill(1)...'
        #if cmdproc.poll() == True:
        #    print 'ThreadedCmd: about to kill(2)...'
        #    cmdproc.kill()
        os.killpg(cmdproc.pid, signal.SIGTERM)

    def stopController(self):
        self.running = False

#test program
if __name__ == '__main__':

    #create command controller
    vidcontrol = ThreadedCmd("raspivid", "-o test.h264 -t 0 -n -w 600 -h 400 -fps 12")
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
