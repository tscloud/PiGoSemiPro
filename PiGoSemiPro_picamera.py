#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import picamera
from ButtonControl import ButtonControl
import time, argparse, sys, os

def fileSetup(path):
    """
    look for files previously created and increment
    file name convention: seminnnn.h264
    nnnn = 0001, 0002, etc.
    """
    past_fnames = next(os.walk(path))[2]
    f_nums = []
    for f in past_fnames:
        if f.startswith('semi'):
            f_nums.append(int(f[4:8]))

    if not f_nums:
        now_fname = '/semi0001.h264'
    else:
        now_fname = '/semi%04d.h264' % (max(f_nums)+1, )

    now_fname = path+now_fname
    print 'Current filename: %s' % now_fname

    return now_fname

def main():
    BUTTONSHORTPRESSTICKS = 5
    BUTTONLONGPRESSTICKS = 200
    BUTTONTICKTIME = 0.01
    BUTTONGPIOPIN = 12
    # LEDGPIOPIN = 17

    # camera props
    VIDEOFPS = 5
    VIDEOHEIGHT = 1080
    # VIDEOHEIGHT = 600
    VIDEOWIDTH = 1920
    # VIDEOWIDTH = 800

    # function globals
    #button = None

    #Command line options
    parser = argparse.ArgumentParser(description="PiGoSemiPro")
    parser.add_argument("path", help="The location of the data directory")
    args = parser.parse_args()

    try:
        print "Starting pi powered cam"
        print "Data path - " + args.path

        #create button
        button = ButtonControl(BUTTONGPIOPIN, 0, BUTTONSHORTPRESSTICKS, BUTTONLONGPRESSTICKS, BUTTONTICKTIME)
        button.start()
        print "Button - started controller"

        print "PiGoSemiPro Ready"

        # outfile = fileSetup(args.path)

        #while the button hasnt received a long press (shutdown), keep on looping
        while button.checkLastPressedState() != button.ButtonPressStates.LONGPRESS:

            #has the button been pressed for recording?
            if button.checkLastPressedState() == button.ButtonPressStates.SHORTPRESS:

                #get the last pressed state of the button and reset it
                button.getLastPressedState()

                #start recording
                #create picamera - dont use LED (my fork of picamera supports this)
                with picamera.PiCamera(False) as camera:
                    #setup camera
                    camera.resolution = (VIDEOWIDTH, VIDEOHEIGHT)
                    camera.framerate = VIDEOFPS
                    camera.vflip = True
                    camera.hflip = True
                    camera.video_stabilization = True

                    #start recording
                    camera.start_recording(fileSetup(args.path), inline_headers=False)
                    print "Recording - started pi camera"

                    # wait for the button to be pressed
                    # important: reset button state or camera will start over again
                    while button.getLastPressedState() == button.ButtonPressStates.NOTPRESSED:
                        #wait for a bit
                        time.sleep(0.2)

                    #stop the camera
                    camera.stop_recording()
                    camera.close()
                    #recording has finished
                    print "Recording - stopped"
            else:
                # have not received button press to start <- is this a good time?
                time.sleep(0.2)

    except KeyboardInterrupt:
        print "User Cancelled (Ctrl C)"

    except:
        print "Unexpected error - ", sys.exc_info()[0], sys.exc_info()[1]
        raise

    finally:
        print "Stopping pi powered cam"
        #stop button
        button.stopController()
        button.join()
        print "Button - Stopped controller"
        #cleanup gpio
        GPIO.cleanup()
        print "Stopped"

if __name__ == '__main__':
    main()
