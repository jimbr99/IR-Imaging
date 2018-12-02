import time
from base_camera import BaseCamera
from flask import send_from_directory
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(17, GPIO.OUT)



#from os import is_open
dir = os.path.dirname(__file__)
filename = os.path.join(dir, '/dev/shm')
MEDIA_FOLDER = filename + '/' + 'therm.jpg'


class Camera(BaseCamera):
    """An emulated camera implementation that streams a repeated sequence of
    files 1.jpg, 2.jpg and 3.jpg at a rate of one frame per second."""
#    imgs = [open(f + '.jpg', 'rb').read() for f in ['1', '2', '3']]
#    imgs = [open(filename + '/' + 'therm.jpg','rb').read()]
    ofh = open(MEDIA_FOLDER,'rb')

    
    @staticmethod
    def frames():

        status = 0
        while True:
         #   if Camera.ofh:
         #       Camera.ofh.close()
         #   time.sleep(0.100)
            if GPIO.input(5) == 0:
                GPIO.output(17, 0)
                
            if GPIO.input(5) == 1:      
                Camera.ofh = open(MEDIA_FOLDER,'rb')
                frame = Camera.ofh.read()
                Camera.ofh.close()
                GPIO.output(17, 1)
                yield frame
