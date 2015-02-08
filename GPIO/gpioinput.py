#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import sys, time

GPIO.setmode(GPIO.BOARD)

# GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        input_value = GPIO.input(12)
        print 'input_value: %s' % input_value
        time.sleep(2)
        # pull UP
        if input_value == False:
        # pull DOWN
        #if input_value == True:
            print "button pressed"
            # pull UP
            while input_value == False:
            # pull DOWN
            #while input_value == True:
                input_value = GPIO.input(12)

except KeyboardInterrupt:
    GPIO.cleanup()
    print "\nBye"
    sys.exit()
