from flask import Flask
from flask import render_template
from flask import send_from_directory
from flask import url_for
from flask import Response
from faker import Faker 
import time 
import os 
from gps3 import gps3
import sqlite3
from pulsesensor import Pulsesensor
import settings
from threading import Thread
from time import sleep
import RPi.GPIO as GPIO
from camera import Camera

# external image directory (in RAM drive)
#MEDIA_FOLDER = os.path.realpath('/dev/shm')
dir = os.path.dirname(__file__)
filename = os.path.join(dir, '/dev/shm')
MEDIA_FOLDER = filename

# file vars
global oldFile


# added for marker operation
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
GPIO.output(4, GPIO.HIGH)
GPIO.setup(5, GPIO.In)

# input_gpio5 = GPIO.Input(5)

# connect to data base file
dbconnect = sqlite3.connect("ssdb.db");
# access columns by name
dbconnect.row_factory = sqlite3.Row;
# create cursor object
cursor = dbconnect.cursor();

# set gps baud rate
os.system("sudo  stty -F /dev/ttyUSB0 9600")
# set up gps socket and data stream
gps_socket = gps3.GPSDSocket()
data_stream = gps3.DataStream()
gps_socket.connect()
gps_socket.watch()
oldFile = 0

# loop until gps data has TPV object; needs timeout
for new_data in gps_socket:
   if new_data:
      data_stream.unpack(new_data)
      print('Altitude = ',data_stream.TPV['alt'])
      print('Latitude = ',data_stream.TPV['lat'])
      print('Longitude = ',data_stream.TPV['lon'])
      if new_data.find("TPV") != -1:
         print('Found')
         break
print("OOOOOOOOOOOOOOOOOKKKKKKKKKKKKKKKKKKKK")

settings.init()
#settings.gList.insert(0, 0)
p = Pulsesensor()

fake = Faker()      

app = Flask(__name__)

@app.route("/")
def index():
    time_utc = 0
    lat = 0
    lon = 0
    alt = 0
    # mark start and break out if no GPS data for 1 second
    time_started = time.time()
    # return template to browser;
    # meta command in index causes browser to repeat GET every 4 sec.
    for new_data in gps_socket:       
     if type(new_data) is str:        
      if new_data.find("TPV") != -1:
        data_stream.unpack(new_data)
        time_utc = data_stream.TPV['time']
        lat = data_stream.TPV['lat']
        lon = data_stream.TPV['lon']
        alt = data_stream.TPV['alt']
        break # exit for loop if GPS data present
     if time.time() > time_started + 1:
        break # exit for loop after 2 seconds
      
    
    bpm = settings.gList[0]
    tmp = settings.gList[1]
    ts = tmp * (3300.0 / 1024.0)
    Temp_C = (ts - 100.0) / 10.0 - 40.0
    Temp_F = (Temp_C * 9.0 / 5.0) + 32
    dict = {'Time': str(time_utc), 'Latitude': (lat),
            'Longitude': str(lon), 'Altitude': str(alt),
            'Physiologic': ("%3.2f" % bpm), 'Temperature': ("%3.2f C / %3.2f F" % (Temp_C, Temp_F))
           }
#    p.stopAsyncBPM()
#    print(str(p.BPM))
    
    print("%3.2f" % bpm)
    response = render_template("index.html", value=dict) #value=dict
    GPIO.output(4, GPIO.LOW)
    sleep(0.005)
    GPIO.output(4, GPIO.HIGH)
    print(filename + '/' + 'therm.jpg')
    return response
 #   return ("hello world")


@app.route('/dev/shm/<path:filename>')
def download_file(filename):
#    fileStat = os.path.getmtime('/dev/shm/therm.jpg')
#    if oldFile < fileStat:
#        global oldFile
#        oldFile = fileStat
#        return send_from_directory(MEDIA_FOLDER, filename, as_attachment=True)
    while True:
#        frame = send_from_directory(MEDIA_FOLDER, filename, as_attachment=True)
        return send_from_directory(MEDIA_FOLDER, filename, as_attachment=True)
#        yield(b'--frame\r\n'
#              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


    

def gen(camera):
    """Video streaming generator function."""
    
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'content-Type: image/jpg\r\n\r\n' + frame + b'r\n')
 
@app.route("/video_feed")
def video_feed():
  #  f = send_from_directory(MEDIA_FOLDER, 'thermal.jpg', as_attachment=True)
#    return Response(gen(Camera()),
#                    mimetype='multipart/x-mixed-replace; boundary=frame')
    return filename + '/' + 'therm.jpg' 

@app.route("/favicon.ico")
def favicon():
    return(url_for('static',filename='favicon.ico'))

p.startAsyncBPM()



if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

