#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ThreadedCmd import ThreadedCmd
from ButtonControl import ButtonControl

#subclass of ThreadedCmd that has a ButtonControl
class CommandButton(ThreadedCmd):

    def __init__(self, gpioPin, cmd, cmd_options):

        BUTTONSHORTPRESSTICKS = 5
        BUTTONLONGPRESSTICKS = 200
        BUTTONTICKTIME = 0.01
        # defaulting to pin high <- good to do here?
        #  => pressed state will be low
        BUTTONPRESSEDSTATE = 0

        super(CommandButton, self).__init__(cmd, cmd_options)

        self.button = ButtonControl(gpioPin, BUTTONPRESSEDSTATE,
                                    BUTTONSHORTPRESSTICKS, BUTTONLONGPRESSTICKS,
                                    BUTTONTICKTIME)

        self.button.start()
