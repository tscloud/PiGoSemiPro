#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import picamera

#for classes that want to have a ButtonControl
class PiCameraControl(object):

    def __init__(self, path="."):
        """use picamera API"""
        self.path = path
        # camera props
        self.VIDEOFPS = 12
        self.VIDEOHEIGHT = 400
        self.VIDEOWIDTH = 600

        self.camera = picamera.PiCamera(False)
        #setup camera
        self.camera.resolution = (self.VIDEOWIDTH, self.VIDEOHEIGHT)
        self.camera.framerate = self.VIDEOFPS
        self.camera.vflip = True
        self.camera.hflip = True
        self.camera.video_stabilization = True

    def start(self):
        """start recording"""
        self.camera.start_recording(self.path, inline_headers=False)
        print "Recording - started pi camera"

    def stopController(self):
        """stop the camera"""
        self.camera.stop_recording()
        self.camera.close()
        #recording has finished
        print "Recording - stopped"

    def running(self):
        """check to see if camera running - needed for interface completeness"""
        # is there a comparable method in picamera?
        return True

    def join(self):
        """we're no a thread but - needed for interface completeness"""
        return
