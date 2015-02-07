#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import sys

GPIO.setmode(GPIO.BOARD)

# times button was pressed

def callback_rising(channel):
    print '...RISING callback called'

def callback_falling(channel):
    print '...FALLING callback called'

def callback_both(channel):
    print '...BOTH callback called'

def main():
    print 'in main()...'

    pin_in = 12
    # GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(pin_in, GPIO.IN)

    try:
        keep_going = True
        GPIO.add_event_detect(pin_in, GPIO.RISING, callback=callback_rising, bouncetime=300)  # add rising edge detection on a channel
        while keep_going == True:
            # GPIO.add_event_callback(pin_in, callback_falling)
            # GPIO.add_event_callback(pin_in, callback_both)
            print 'Hit Enter whenever'
            bb = raw_input()
            keep_going = False

    except KeyboardInterrupt:
        print "Cntl-C?"

    finally:
        GPIO.cleanup()
        print "\nBye"

if __name__ == '__main__':
    main()
