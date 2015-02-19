#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ButtonControl import ButtonControl

#for classes that want to have a ButtonControl
class HasButton(object):

    def __init__(self, gpioPin):

        BUTTONSHORTPRESSTICKS = 5
        BUTTONLONGPRESSTICKS = 200
        BUTTONTICKTIME = 0.01
        # defaulting to pin high <- good to do here?
        #  => pressed state will be low
        BUTTONPRESSEDSTATE = 0

        self.button = ButtonControl(gpioPin, BUTTONPRESSEDSTATE,
                                    BUTTONSHORTPRESSTICKS, BUTTONLONGPRESSTICKS,
                                    BUTTONTICKTIME)

        self.button.start()
