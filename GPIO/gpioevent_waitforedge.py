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
            # if pull down => RISING should be 1st
            GPIO.wait_for_edge(pin_in, GPIO.RISING)
            print '...rising...'
            GPIO.wait_for_edge(pin_in, GPIO.FALLING)
            print '...falling...'

    except KeyboardInterrupt:
        GPIO.cleanup()
        print "\nBye"
        sys.exit()

if __name__ == '__main__':
    main()
