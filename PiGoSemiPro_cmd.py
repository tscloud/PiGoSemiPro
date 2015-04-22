#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import picamera
# from ButtonControl import ButtonControl
from ThreadedCmd import ThreadedCmd
from ButtonControlPlus import ButtonControlPlus
from PiCameraControl import PiCameraControl
import time, argparse, sys, os, traceback, ConfigParser

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

def fileSetupPlay(path, playFiles):
    """
    look for file w/ highest "nnnn" and return
    if file passed in => decrement and return that file
    but 1st check toi see if any file created in the meantime
    file name convention: seminnnn.h264
    nnnn = 0001, 0002, etc.
    """
    now_fname = None

    #we've played a file already...play the next if we can
    if playFiles[0] != None:
        try:
            print 'lastFilePlayed: %s' % playFiles[0]
            print 'nnnn: %s' % playFiles[0][6:10]
            n = int(playFiles[0][6:10])
        except ValueError:
            raise BadFileName(playFiles[0])

        n = n-1

        # recursion - start list from the beginning
        #  do this check everytime to see if there are any new files
        now_fname = fileSetupPlay(path, None)
        print 'highestFile: %s' % now_fname

        if n <= 0: # we played everything => start from beginning
            # raise AllFilesPlayed()
            pass
        else:
            # check to see if there are any new files
            print 'firstFilePlayed: %s' % now_fname
            if now_fname > playFiles[1]:
                now_fname = playFiles[1]

    #this means we're starting fresh
    else:
        n = 0

    #if now_fname set => we're starting at the top and are all set
    if not now_fname:
        past_fnames = next(os.walk(path))[2]
        f_nums = [] # this is the list number parts of the files of interest
        for f in past_fnames:
            if f.startswith('semi'):
                f_nums.append(int(f[4:8]))

        if not f_nums: # no files
            raise NoFilesToPlay()
        elif n == 0: # start from beginning
            now_fname = '/semi%04d.h264' % (max(f_nums))
            first_fname = now_fname
        else: # give me the next
            now_fname = '/semi%04d.h264' % (n)

        now_fname = path+now_fname

    print 'Current play name: %s' % now_fname

    return [now_fname, first_fname]

def buttonLoop(cmd, button, fsCheckFile=None, fsThresh=0):
    """perform a loop around a CommandButton"""
    #get the last pressed state of the button and reset it
    button.getLastPressedState()

    #start the command...
    cmd.start()

    #used for sleeping & fs checking
    sleepTime = 0.2
    sleepsBeforeFSCheck = 20
    fsCheckCnt = 0

    # wait for the button to be pressed
    # should check to see if the thing you are trying to stop is still
    #  running -> don't need to stop a stopped thing
    # important: reset button state or camera will start over again
    while button.getLastPressedState() == button.ButtonPressStates.NOTPRESSED and cmd.isAlive():
        # maybe check filesystem...but not every time
        if fsCheckFile != None and fsCheckCnt == sleepsBeforeFSCheck:
            fsCheckCnt = 0
            if freeSpaceCheck(fsCheckFile, fsThresh):
                break
        else:
            fsCheckCnt += 1
        #wait for a bit
        time.sleep(sleepTime)

    #stop the button
    print "Stopping command controller"
    #stop the controller
    cmd.stopController()
    #wait for the tread to finish if it hasn't already
    cmd.join()
    print "cmdButton joined..."

def freeSpaceCheck(checkFile, thresh):
    """check for filesyatem freespace and possiblly stop things if we're running low"""
    letsQuit = False

    print "checking: %s" % checkFile
    if os.path.isfile(checkFile) or os.path.isdir(checkFile):
        disk = os.statvfs(checkFile)
        totalAvailSpace = float(disk.f_bsize*disk.f_bfree)
        checkSpace = totalAvailSpace/1024/1024
        print "available space: %.2f MBytes" % (checkSpace)

        if thresh != 0 and checkSpace < thresh:
            print "Sorry...no more space"
            letsQuit = True
        else:
            letsQuit = False
    else:
        print "filename given not a file"
        letsQuit = True

    return letsQuit

def main():
    """it's the main...duh"""
    #set gpio mode
    GPIO.setmode(GPIO.BOARD)

    #Command line options
    parser = argparse.ArgumentParser(description="PiGoSemiPro")
    parser.add_argument("--path", help="The location of the data directory")
    parser.add_argument("--playstream", action='store_true', help="play stream instead of recording local file")
    parser.add_argument("--noshowLED", action='store_false', help="if specified => do NOT show camera LED")
    args = parser.parse_args()

    #build default dict prior to reading config <-- not currently used
    default_vars = {'FILEPATH':args.path, 'PLAYSTREAM':args.playstream, 'SHOWLED':args.noshowLED}

    #read config file
    config = ConfigParser.RawConfigParser()
    ### I think this is weird -- have to do this to make the options not convert to lowercase
    config.optionxform = str
    config.read('.config_pigosemipro.cfg')

    CAMERAGPIOPIN = config.getint('Pins', 'CAMERAIN')
    PLAYERGPIOPIN = config.getint('Pins', 'PLAYERIN')
    CAMERALEDGPIOPOUT = config.getint('Pins', 'CAMERALEDOUT')

    PROGRUNNINGPOUT = config.getint('Pins', 'PROGRUNNINGLEDOUT')

    VIDEOFPS = config.get('CameraOpts', 'VIDEOFPS')
    VIDEOHEIGHT = config.get('CameraOpts', 'VIDEOHEIGHT')
    VIDEOWIDTH = config.get('CameraOpts', 'VIDEOWIDTH')

    STREAMINGOPTS = config.get('ProcOpts', 'STREAMINGOPTS')
    RECORDINGOPTS = config.get('ProcOpts', 'RECORDINGOPTS')
    STREAMPLAYOPTIONS = config.get('ProcOpts', 'STREAMPLAYOPTIONS')

    # used by player
    playFiles = None

    #are we aiming? => stream
    aiming = True

    # turn on the LED that indicates the prog in running
    GPIO.setup(PROGRUNNINGPOUT, GPIO.OUT)
    GPIO.output(PROGRUNNINGPOUT, GPIO.HIGH)
    print "LED: %i should be %i" % (PROGRUNNINGPOUT, GPIO.HIGH)

    # set camera LED
    # remember - if specified => do NOT show LED
    GPIO.setup(CAMERALEDGPIOPOUT, GPIO.OUT, initial=(args.noshowLED))

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

            #has the --BUTTON-- been pressed for --RECORDING--?
            if cameraButton.checkLastPressedState() == cameraButton.ButtonPressStates.SHORTPRESS:
                #extra arg (maybe) to buttonLoop
                vidFile = None
                if aiming:
                    #create camera ThreadedCmd - streaming
                    cameraCmd = ThreadedCmd("raspivid",
                                            STREAMINGOPTS % (VIDEOWIDTH, VIDEOHEIGHT, VIDEOFPS))
                else:
                    #create camera ThreadedCmd - recording
                    vidFile = fileSetupRec(args.path)
                    #...but don't record if we don't have space
                    if freeSpaceCheck(os.path.dirname(vidFile), config.getint('OtherOpts', 'SPACETHRESH')):
                        #get the last pressed state of the button and reset it
                        cameraButton.getLastPressedState()
                        continue
                    cameraCmd = ThreadedCmd("raspivid",
                                            RECORDINGOPTS % (fileSetupRec(args.path), VIDEOWIDTH, VIDEOHEIGHT, VIDEOFPS))
                    #create camera PiCameraControl
                    #cameraCmd = PiCameraControl(fileSetupRec(args.path))
                print "Recording/camera streaming - started pi camera"
                buttonLoop(cameraCmd, cameraButton, vidFile, config.getint('OtherOpts', 'SPACETHRESH'))
                # toggle
                aiming = 1 - aiming

            #has the --BUTTON-- been pressed for --PLAYING--?
            elif playerButton.checkLastPressedState() == playerButton.ButtonPressStates.SHORTPRESS:
                if args.playstream:
                    #create vnc streamer ThreadedCmd
                    playerCmd = ThreadedCmd("vncr", STREAMPLAYOPTIONS, 5) #hardcoded - 5 retries
                    print "Playing stream: %s - started pi player" % STREAMPLAYOPTIONS
                    buttonLoop(playerCmd, playerButton)
                else:
                    #create player ThreadedCmd
                    try:
                        playFiles = fileSetupPlay(args.path, playFiles)
                        player_options = "-o hdmi %s" % playFiles[0]
                        playerCmd = ThreadedCmd("omxplayer", player_options)
                        print "Playing file: %s - started pi player" % playFiles[0]
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

        # turn off the program running LED
        GPIO.output(PROGRUNNINGPOUT, GPIO.LOW)

        #cleanup gpio
        GPIO.cleanup()
        print "Stopped"

if __name__ == '__main__':
    main()
