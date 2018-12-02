#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response
from flask import stream_with_context
from flask import url_for
import time 
import os 
from gps3 import gps3
from pulsesensor import Pulsesensor
import settings
from threading import Thread
from threading import Timer
from time import sleep
import RPi.GPIO as GPIO
from camera import Camera
from reptimer import RepeatedTimer
#from flask_socketio import SocketIO
#from flask_sse import sse


gcounter = 0

def incit():
    global gcounter
    gcounter = gcounter+1
    return gcounter

def testcount():    
    print ("Testing %d" % incit())


rt = RepeatedTimer(1, testcount)
print ("Passed")

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


app = Flask(__name__)
# added
#app.config['SECRET_KEY'] = 'secret!'
#socketio = SocketIO(app)
#app.config["REDIS_URL"] = "REDIS://localhost"
#app.register_blueprint(sse, url_prefix='/stream')



@app.route('/')
def index():
    """Video streaming home page."""
    
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
    return response
    
#    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def get_data():
    while True:
        if new_data.find("TPV") != -1:
            time_utc = data_stream.TPV['time']
        bpm = settings.gList[0]
        tmp = settings.gList[1]
        ts = tmp * (3300.0 / 1024.0)
        Temp_C = (ts - 100.0) / 10.0 - 40.0
        Temp_F = (Temp_C * 9.0 / 5.0) + 32
        dict = {'Time': str(time_utc), 'Latitude': (lat),
                'Longitude': str(lon), 'Altitude': str(alt),
                'Physiologic': ("%3.2f" % bpm), 'Temperature': ("%3.2f C / %3.2f F" % (Temp_C, Temp_F))
               }
        value = dict
    yield value

#@app.route('/hello')
#def publish_hello():
#    sse.publish({"message": "Hello!"}, type='greeting')
#    return "Message sent!"

@app.route('/value')
def value():
    while True:
        yield get_data()
        
@app.route('/stream')
def streamed_response():
    def generate():
            yield 'Hello '
            yield request.args['name']
            yield '!'
    return Response(stream_with_context(generate()))

@app.route('/event_stream')
def stream():
    def event_stream():
        while True:
            time.sleep(0.1)
            yield 'data: %s\n\n' % 'hola mundo'
    return Response(event_stream(), mimetype="text/event-stream")


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(1)
    return rv

@app.route('/data')
def data():
    def generate():
        for i in xrange(50):
            sleep(0.1)
            print("TESTING...")
            yield i
        #return Response(generate(), mimetype='text/plain')
    return Response(stream_template('index.html', data=generate()))
                       
  
if __name__ == '__main__':
    debug = True
    app.run(host='0.0.0.0', threaded=True)
#    socketio.run(app)
