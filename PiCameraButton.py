#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from PiCameraControl import PiCameraControl
from HasButton import HasButton

#multiple inheritance - class that has a picamera nad a button
class PiCameraButton(PiCameraControl, HasButton):

    def __init__(self, gpioPin, path="."):
        """use picamera and button"""

        PiCameraControl.__init__(self, path)
        HasButton.__init__(self, gpioPin)
