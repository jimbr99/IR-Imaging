from flask import send_from_directory
import os
dir = os.path.dirname(__file__)
filename = os.path.join(dir, '/dev/shm')
MEDIA_FOLDER = filename

class Camera(object):
    def __init__(self):
 #       file = send_from_directory(MEDIA_FOLDER, 'thermal.jpg', as_attachment=True)
 #       self.frames = [open(f + '.jpg', 'rb').read() for f in [file]]
        self.frames = open(filename + '/' + 'therm.jpg','rb').read()
        
        
    def get_frame(self):
        return self.frames
    