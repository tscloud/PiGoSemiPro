#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import sys

GPIO.setmode(GPIO.BOARD)

def main():
    print 'in main()...'

    pin_in = 12
    # GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(pin_in, GPIO.IN)

    try:
        while True:
            GPIO.add_event_detect(pin_in, GPIO.BOTH)  # add both edge detection on a channel
            print 'Hit Enter whenever'
            bb = raw_input()
            if GPIO.event_detected(pin_in):
                print 'Button pressed'

    except KeyboardInterrupt:
        GPIO.cleanup()
        print "\nBye"
        sys.exit()

if __name__ == '__main__':
    main()
