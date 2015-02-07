#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import sys, time

class GpioEvent(object):

    def __init__(self):

        GPIO.setmode(GPIO.BOARD)

        self.pin_in = 12
        GPIO.setup(self.pin_in, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.pin_out1 = 11
        GPIO.setup(self.pin_out1, GPIO.OUT)

        self.pin_out2 = 13
        GPIO.setup(self.pin_out2, GPIO.OUT)

        self.chan_list_out = (self.pin_out1, self.pin_out2)

    def callback_rising(self, channel):

        print '...RISING callback called from channel %s' % channel
        if not GPIO.input(self.pin_out1):
            if not GPIO.input(self.pin_out2):
                GPIO.output(self.pin_out2, True)
            else:
                GPIO.output(self.pin_out1, True)
        elif not GPIO.input(self.pin_out2):
            GPIO.output(self.pin_out2, True)
        else:
            GPIO.output(self.pin_out1, False)
            GPIO.output(self.pin_out2, False)

    def callback_flash(self, channel):

        if GPIO.input(self.pin_out1) and GPIO.input(self.pin_out2):
            for x in xrange(1,10):
                GPIO.output(self.pin_out1, False)
                time.sleep(.2)
                GPIO.output(self.pin_out2, False)
                time.sleep(.2)
                GPIO.output(self.pin_out1, True)
                time.sleep(.2)
                GPIO.output(self.pin_out2, True)

    def classmain(self):
        print 'in main()...'

        try:
            GPIO.add_event_detect(self.pin_in, GPIO.RISING, callback=self.callback_rising, bouncetime=300)
            GPIO.add_event_callback(self.pin_in, self.callback_flash)
            while True:
                # GPIO.add_event_callback(pin_in, callback_falling)
                # GPIO.add_event_callback(pin_in, callback_both)
                print 'Hit Enter whenever'
                raw_input()
                break

        except KeyboardInterrupt:
            print "Cntl-C?"

        finally:
            GPIO.cleanup()
            print "\nBye"

if __name__ == '__main__':
    GpioEvent().classmain()
