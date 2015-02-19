#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import threading, time

# class for managing the Button
# Thx Martin O'Hanlon
class ButtonControl(threading.Thread):

    class ButtonPressStates():
        """only used to determine last pressed state"""
        NOTPRESSED = 0
        SHORTPRESS = 1
        LONGPRESS = 2

    def __init__(self, gpioPin, pressedState, shortPressTicks, longPressTicks, tickTime):
        #setup threading
        threading.Thread.__init__(self)
        #persist data
        self.gpioPin = gpioPin
        self.pressedState = pressedState
        self.shortPressTicks = shortPressTicks
        self.longPressTicks = longPressTicks
        self.tickTime = tickTime

        if pressedState == 0:
            pull_value = GPIO.PUD_UP
        else:
            pull_value = GPIO.PUD_DOWN
        GPIO.setup(self.gpioPin, GPIO.IN, pull_up_down=pull_value)
        
        #button properties
        self.running = False
        self.lastPressedState = None

    def get(self):
        return GPIO.input(self.gpioPin)

    def pressed(self):
        #Returns a boolean representing whether the button is pressed
        buttonPressed = False
        # if gpio input is equal to the pressed state
        if GPIO.input(self.gpioPin) == self.pressedState:
            buttonPressed = True
        return buttonPressed

    def run(self):
        #start the button control
        print 'start the button control'
        self.running = True
        self.lastPressedState = self.ButtonPressStates.NOTPRESSED

        # if the button is pressed when the class starts, wait till it is released
        print 'initial button state (1): %i' % self.get()
        while self.pressed():
            print 'button is pressed when the class starts, wait till it is released'
            time.sleep(self.tickTime)

        # while the control is running
        while self.running:
            # wait for the button to be pressed
            print 'wait for the button to be pressed'
            print 'initial button state (2): %i' % self.get()
            # Use GPIO.wait_for_edge(channel, GPIO.FALLING) here? <= NO
            # need to poll to check if we ot the stop command
            while self.pressed() == False and self.running:
                time.sleep(self.tickTime)

            print 'button pressed'
            ticks = 0
            # wait for the button to be released
            # Use GPIO.wait_for_edge(channel, GPIO.RISING) here? <= NO
            # need to poll to check if we ot the stop command
            while self.pressed() == True and self.running:
                ticks += 1
                time.sleep(self.tickTime)

            print 'button released'
            #was it press a short or long time
            if ticks > self.shortPressTicks and ticks < self.longPressTicks:
                self.lastPressedState = self.ButtonPressStates.SHORTPRESS
            if ticks > self.longPressTicks:
                self.lastPressedState = self.ButtonPressStates.LONGPRESS

            #wait in between button presses
            time.sleep(0.5)

    def checkLastPressedState(self):
        """gets the last pressed state but doesnt reset it"""
        return self.lastPressedState

    def getLastPressedState(self):
        """gets the last pressed state and resets it"""
        theLastPressedState = self.lastPressedState
        self.lastPressedState = self.ButtonPressStates.NOTPRESSED
        return theLastPressedState

    def stopController(self):
        """stop the thread by setting flag that will be checked"""
        self.running = False
