#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import picamera
# from ButtonControl import ButtonControl
from ThreadedCmd import ThreadedCmd
from ButtonControlPlus import ButtonControlPlus
from PiCameraControl import PiCameraControl
import time, argparse, sys, os, traceback

# Custom exceptions - Play
class NoFilesToPlay(NameError):
    def __init__(self):

        # Call the base class constructor with the parameters it needs
        super(NameError, self).__init__()

class AllFilesPlayed(NameError):
    def __init__(self):

        # Call the base class constructor with the parameters it needs
        super(NameError, self).__init__()

class BadFileName(NameError):
    def __init__(self, filename):

        # Call the base class constructor with the parameters it needs
        super(NameError, self).__init__()

        self.filename = filename

def fileSetupRec(path):
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
        now_fname = '/semi%04d.h264' % (max(f_nums)+1)

    now_fname = path+now_fname
    print 'Current rec filename: %s' % now_fname

    return now_fname

def fileSetupPlay(path, lastFilePlayed):
    """
    look for file w/ highest "nnnn" and return
    if file passed in => decrement and return that file
    file name convention: seminnnn.h264
    nnnn = 0001, 0002, etc.
    """
    now_fname = None

    if lastFilePlayed != None:
        try:
            print "lastFilePlayed: %s" % lastFilePlayed
            print "nnnn: %s" % lastFilePlayed[6:10]
            n = int(lastFilePlayed[6:10])
        except ValueError:
            raise BadFileName(lastFilePlayed)

        n = n-1
        if n <= 0:
            # raise AllFilesPlayed()
            # recursion - start list from the beginning
            now_fname = fileSetupPlay(path, None)
    else:
        n = 0

    if not now_fname:
        past_fnames = next(os.walk(path))[2]
        f_nums = []
        for f in past_fnames:
            if f.startswith('semi'):
                f_nums.append(int(f[4:8]))

        if not f_nums:
            raise NoFilesToPlay()
        elif n == 0:
            now_fname = '/semi%04d.h264' % (max(f_nums))
        else:
            now_fname = '/semi%04d.h264' % (n)

        now_fname = path+now_fname

    print 'Current play name: %s' % now_fname

    return now_fname

def buttonLoop(cmd, button):
    """perform a loop around a CommandButton"""
    #get the last pressed state of the button and reset it
    button.getLastPressedState()

    #start the command
    cmd.start()

    # wait for the button to be pressed
    # should check to see if the thing you are trying to stop is still
    #  running -> don't need to stop a stopped thing
    # important: reset button state or camera will start over again
    while (button.getLastPressedState() == button.ButtonPressStates.NOTPRESSED and
           #try isRunning()?
           #cmd.isRunning()
           cmd.isAlive()):
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
    PLAYERGPIOPIN = 18

    # camera props
    VIDEOFPS = 25
    VIDEOHEIGHT = 360
    VIDEOWIDTH = 640
    STREAMINGOPTS = "-o - -t 99999 -hf -w %s -h %s -fps %s|\
cvlcr stream:///dev/stdin --sout \
'#standard{access=http,mux=ts,dst=:8090}' :demux=h264"
    RECORDINGOPTS = "-o %s -t 0 -n -w %s -h %s -fps %s"
    # hardcoded (obviously) - this will have to be externalized
    STREAMPLAYOPTIONS = "http://tscloud-y50:8090"

    #Command line options
    parser = argparse.ArgumentParser(description="PiGoSemiPro")
    parser.add_argument("path", help="The location of the data directory")
    args = parser.parse_args()

    # used by player
    fileToPlay = None

    #are we aiming? => stream
    aiming = True
    #do we want to play a stream?
    playStream = True

    try:
        print "Starting pi powered cam"
        print "Data path - " + args.path

        print "Camera Button - started controller"
        cameraButton = ButtonControlPlus(CAMERAGPIOPIN)
        cameraButton.start()

        print "Player Button - started controller"
        playerButton = ButtonControlPlus(PLAYERGPIOPIN)
        playerButton.start()

        print "PiGoSemiPro Ready"

        #while the button hasnt received a long press (shutdown), keep on looping
        while (cameraButton.checkLastPressedState() != cameraButton.ButtonPressStates.LONGPRESS and
               playerButton.checkLastPressedState() != cameraButton.ButtonPressStates.LONGPRESS):

            #has the button been pressed for recording?
            if cameraButton.checkLastPressedState() == cameraButton.ButtonPressStates.SHORTPRESS:
                if aiming:
                    #create camera ThreadedCmd - streaming
                    cameraCmd = ThreadedCmd("raspivid",
                                            STREAMINGOPTS % (VIDEOWIDTH, VIDEOHEIGHT, VIDEOFPS))
                else:
                    #create camera ThreadedCmd - recording
                    cameraCmd = ThreadedCmd("raspivid",
                                            RECORDINGOPTS % (fileSetupRec(args.path), VIDEOWIDTH, VIDEOHEIGHT, VIDEOFPS))
                    #create camera PiCameraControl
                    #cameraCmd = PiCameraControl(fileSetupRec(args.path))
                print "Recording/camera streaming - started pi camera"
                buttonLoop(cameraCmd, cameraButton)
                aiming = 1 - aiming

            #has the button been pressed for playing?
            elif playerButton.checkLastPressedState() == playerButton.ButtonPressStates.SHORTPRESS:
                if playStream:
                    #create vnc streamer ThreadedCmd
                    playerCmd = ThreadedCmd("vncr", STREAMPLAYOPTIONS, 5) #hardcoded - 5 retries
                    print "Playing stream: %s - started pi player" % STREAMPLAYOPTIONS
                    buttonLoop(playerCmd, playerButton)
                else:
                    #create player ThreadedCmd
                    try:
                        fileToPlay = fileSetupPlay(args.path, fileToPlay)
                        player_options = "-o hdmi %s" % fileToPlay
                        playerCmd = ThreadedCmd("omxplayer", player_options)
                        print "Playing file: %s - started pi player" % fileToPlay
                        buttonLoop(playerCmd, playerButton)
                    except NoFilesToPlay:
                        print "Nothing to play...try recording something"
                        playerButton.getLastPressedState() # reset button state
                    except AllFilesPlayed:
                        print "All files played...try recording some more"
                        playerButton.getLastPressedState() # reset button state
                    except BadFileName as e:
                        print "Bad file name...what are you trying to play? : %s" % e.filename
                        playerButton.getLastPressedState() # reset button state
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
