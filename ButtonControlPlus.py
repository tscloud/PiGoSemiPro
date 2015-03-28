#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ButtonControl import ButtonControl

class ButtonControlPlus(ButtonControl):
    """ButtonControl with some constants"""

    def __init__(self, gpioPin):
        BUTTONSHORTPRESSTICKS = 5
        BUTTONLONGPRESSTICKS = 200
        BUTTONTICKTIME = 0.01
        # good to do here?
        BUTTONPRESSEDSTATE = 0

        super(ButtonControlPlus, self).__init__(gpioPin, BUTTONPRESSEDSTATE,
                                               BUTTONSHORTPRESSTICKS, BUTTONLONGPRESSTICKS,
                                               BUTTONTICKTIME)
