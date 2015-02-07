#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import socket
from time import sleep
class HD44780(object):

    def __init__(self, pin_rs=7, pin_e=8, pins_db=[25, 24, 23, 18]):

        self.pin_rs=pin_rs
        self.pin_e=pin_e
        self.pins_db=pins_db

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_e, GPIO.OUT)
        GPIO.setup(self.pin_rs, GPIO.OUT)
        for pin in self.pins_db:
            GPIO.setup(pin, GPIO.OUT)

        self.clear()

    def clear(self):
        """ Blank / Reset LCD """

        self.cmd(0x33) # $33 8-bit mode
        self.cmd(0x32) # $32 8-bit mode
        self.cmd(0x28) # $28 8-bit mode
        self.cmd(0x0C) # $0C 8-bit mode
        self.cmd(0x06) # $06 8-bit mode
        self.cmd(0x01) # $01 8-bit mode

    def cmd(self, bits, char_mode=False):
        """ Send command to LCD """

        sleep(0.001)
        bits=bin(bits)[2:].zfill(8)

        GPIO.output(self.pin_rs, char_mode)

        for pin in self.pins_db:
            GPIO.output(pin, False)

        for i in range(4):
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i], True)

        GPIO.output(self.pin_e, True)
        GPIO.output(self.pin_e, False)

        for pin in self.pins_db:
            GPIO.output(pin, False)

        for i in range(4,8):
            if bits[i] == "1":
                GPIO.output(self.pins_db[::-1][i-4], True)


        GPIO.output(self.pin_e, True)
        GPIO.output(self.pin_e, False)

    def message(self, text):
        """ Send string to LCD. Newline wraps to second line"""

        for char in text:
            if char == '\n':
                self.cmd(0xC0) # next line
            else:
                self.cmd(ord(char),True)

if __name__ == '__main__':

    lcd = HD44780()
    count=0
    sleep(2)
    lcd.clear()
    lcd.message(" Hello Pi\n")
    sleep(5)
    while(1):
        ip_=""
        temp_text=" Semillero ADT"
        new_text=""
        a=0
        while(a<len(temp_text)):
        	new_text=new_text+temp_text[(count+a)%(len(temp_text))]
        	a=a+1
	
    count=count+1
    sleep(0.2)
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("google.com",80))
        ip_=s.getsockname()[0]
        s.close()
    except:
        lcd.clear()
        lcd.message(new_text + "\n" +"NO IP")
    else:
        lcd.clear()
        lcd.message(new_text + "\n"+ip_)
