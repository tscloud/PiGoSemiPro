#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import picamera

class CameraControl(object):

    def __init__(self):

        self.VIDEOFPS = 25
        self.VIDEOWIDTH = 1296
        self.VIDEOHEIGHT = 730

    def startcam(self):

        with picamera.PiCamera() as camera:

            #setup camera
            camera.resolution = (self.VIDEOWIDTH, self.VIDEOHEIGHT)
            camera.framerate = self.VIDEOFPS
            camera.vflip = True
            camera.hflip = True
            camera.video_stabilization = True

            #start recording
            print "Recording - started pi camera"
            camera.start_recording("vid2.h264", inline_headers=False)
            print "about to wait..."
            camera.wait_recording(10)
            camera.stop_recording()

if __name__ == '__main__':
    CameraControl().startcam()
