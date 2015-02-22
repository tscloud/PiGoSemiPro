#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import picamera
# from ButtonControl import ButtonControl
from ThreadedCmd import ThreadedCmd
from ButtonControlPlus import ButtonControlPlus
from PiCameraButton import PiCameraButton
import time, argparse, sys, os, traceback

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

def buttonLoop(cmd, button):
    """perform a loop around a CommandButton"""
    #get the last pressed state of the button and reset it
    button.getLastPressedState()

    #start the command
    cmd.start()

    # wait for the button to be pressed
    # important: reset button state or camera will start over again
    while button.getLastPressedState() == button.ButtonPressStates.NOTPRESSED:
        #wait for a bit
        time.sleep(0.2)

    #stop the button
    print "Stopping command controller"
    #stop the controller
    cmd.stopController()
    #wait for the tread to finish if it hasn't already
    cmd.join()
    print "cmdButton joined..."

def main():
    # pin number based on GPIO.setmode(GPIO.BOARD)
    CAMERAGPIOPIN = 12
    PLAYERGPIOPIN = 11

    # camera props
    VIDEOFPS = 12
    VIDEOHEIGHT = 400
    VIDEOWIDTH = 600

    #Command line options
    parser = argparse.ArgumentParser(description="PiGoSemiPro")
    parser.add_argument("path", help="The location of the data directory")
    args = parser.parse_args()

    try:
        print "Starting pi powered cam"
        print "Data path - " + args.path

        print "Camera Button - started controller"
        cameraButton = ButtonControlPlus(CAMERAGPIOPIN)
        cameraButton.start()

        #create camera button - PiCameraButton
        # cameraButton = PiCameraButton(CAMERAGPIOPIN, fileSetup(args.path))

        print "Player Button - started controller"
        playerButton = ButtonControlPlus(PLAYERGPIOPIN)
        playerButton.start()

        print "PiGoSemiPro Ready"

        #we are designating the camera button as the botton to kill the app
        #while the button hasnt received a long press (shutdown), keep on looping
        while cameraButton.checkLastPressedState() != cameraButton.ButtonPressStates.LONGPRESS:

            #has the button been pressed for recording?
            if cameraButton.checkLastPressedState() == cameraButton.ButtonPressStates.SHORTPRESS:
                #create camera button ThreadedCmd
                cam_options = "-o %s -t 0 -n -w %s -h %s -fps %s" % \
                            (fileSetup(args.path), VIDEOWIDTH, VIDEOHEIGHT, VIDEOFPS)
                cameraCmd = ThreadedCmd("raspivid", cam_options)
                print "Recording - started pi camera"
                buttonLoop(cameraCmd, cameraButton)

            #has the button been pressed for playing?
            elif playerButton.checkLastPressedState() == playerButton.ButtonPressStates.SHORTPRESS:
                #create player button ThreadedCmd
                player_options = "-o hdmi %s" % fileSetup(args.path)
                playerCmd = ThreadedCmd("omxplayer", player_options)
                print "Playing - started pi player"
                buttonLoop(playerCmd, playerButton)

            else:
                # have not received button press to start <- is this a good time?
                time.sleep(0.2)

    except KeyboardInterrupt:
        print "User Cancelled (Ctrl C)"

    except:
        print "Unexpected error - ", sys.exc_info()[0], sys.exc_info()[1]
        print traceback.format_exc()
        raise

    finally:
        print "Stopping pi powered cam"
        #stop camera button
        try:
            cameraButton.stopController()
            cameraButton.join()
        except:
            print "Unexpected error - ", sys.exc_info()[0], sys.exc_info()[1]
        print "Camera Button - Stopped controller"
        #stop camera button
        try:
            playerButton.stopController()
            playerButton.join()
        except:
            print "Unexpected error - ", sys.exc_info()[0], sys.exc_info()[1]
        print "Player Button - Stopped controller"
        #cleanup gpio
        GPIO.cleanup()
        print "Stopped"

if __name__ == '__main__':
    main()
