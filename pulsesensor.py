# extended from https://github.com/WorldFamousElectronics/PulseSensor_Amped_Arduino

import RPi.GPIO as GPIO
import time
import threading
from MCP3008 import MCP3008
import settings
import sys

class Pulsesensor:
    def __init__(self, channel = 0, bus = 0, device = 1):
        self.channel = channel
        self.BPM = 0
        self.adc = MCP3008(bus, device)
        # added for marker operation
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup(4, GPIO.OUT)
       
    def getBPMLoop(self):
        # init variables
        rate = [0] * 10         # array to hold last 10 IBI values
        sampleCounter = 0       # used to determine pulse timing
        lastBeatTime = 0        # used to find IBI
        P = 512                 # used to find peak in pulse wave, seeded
        T = 512                 # used to find trough in pulse wave, seeded
        thresh = 512            # used to find instant moment of heart beat, seeded
        amp = 100               # used to hold amplitude of pulse waveform, seeded
        firstBeat = True        # used to seed rate array so we startup with reasonable BPM
        secondBeat = False      # used to seed rate array so we startup with reasonable BPM
        bpm = 0
        IBI = 600               # int that holds the time interval between beats! Must be seeded!
        Pulse = False           # "True" when User's live heartbeat is detected. "False" when not a "live beat". 
        lastTime = int(time.time()*1000)
    #    lastBeatTime = lastTime
        print("Start loop")
        while not self.thread.stopped:
          currentTime = int(time.time()*1000)
          
          if(currentTime > lastTime):              
            Signal = self.adc.read(self.channel)
            sampleCounter += currentTime - lastTime
            lastTime = currentTime           
            N = sampleCounter  - lastBeatTime
      
            # simulate data JB
      #      if ((N) < 1000 or (N) > 1020): # and pulse == False:
      #          Signal = 100
      #      else:
       #         Signal = 800
                              
            # find the peak and trough of the pulse wave
            if Signal < thresh and N > (IBI/5.0)*3:     # avoid dichrotic noise by waiting 3/5 of last IBI
                if Signal < T:                          # T is the trough
                    T = Signal                          # keep track of lowest point in pulse wave 

            if Signal > thresh and Signal > P:
                P = Signal
            
            # signal surges up in value every time there is a pulse
            if N > 250:                                 # avoid high frequency noise
                if (Signal > (thresh+16)) and Pulse == False and N > (IBI/5.0)*3:
                    Pulse = True                        # set the Pulse flag when we think there is a pulse
                   # GPIO.output(4, GPIO.HIGH)
                    IBI = sampleCounter - lastBeatTime  # measure time between beats in mS
                    #print("signal=%d tresh=%d N=%d" % (Signal,thresh, N))
                    lastBeatTime = sampleCounter        # keep track of time for next pulse


                    if secondBeat:                      # if this is the second beat, if secondBeat == TRUE
                        secondBeat = False;             # clear secondBeat flag               
                        firstBeat = True;

                    if firstBeat:                       # if it's the first time we found a beat, if firstBeat == TRUE
                        firstBeat = False;              # clear firstBeat flag
                        secondBeat = True;              # set the second beat flag
                        
                    # keep a running total of the last 10 IBI values  
                    rate[:-1] = rate[1:]                # shift data in the rate array
                    rate[-1] = IBI                      # add the latest IBI to the rate array
                    runningTotal= sum(rate)            # add upp oldest IBI values
                    runningTotal /= len(rate)           # average the IBI values        
                    v = 60000/runningTotal              # how many beats can fit into a minute? that's BP
                    settings.gList.insert(0,v)
                    t = self.adc.read(1)
                    settings.gList.insert(1,t)
                    
            if Signal < thresh and Pulse == True:       # when the values are going down, the beat is over
                Pulse = False                           # reset the Pulse flag so we can do it again
                amp= P - T                             # get amplitude of the pulse wave
                thresh = amp/2 + T                      # set thresh at 50% of the amplitude
                P = thresh                              # reset these for next time
                T = thresh

            if N > 2500:                                # if 2.5 seconds go by without a beat
                print("N=%d" % N)
                thresh = 512                            # set thresh default
                P = 512                                 # set P default 512
                T = 512                                 # set T default 512
                lastBeatTime = sampleCounter           # bring the lastBeatTime up to date        
                lastTime = 0
                lastTime = currentTime
                N = 0
                firstBeat = True                        # set these to avoid noise
                secondBeat = False
                v = 0                                   #
                settings.gList.insert(0,v)
                t = self.adc.read(1)
                settings.gList.insert(1,t)
 
            #GPIO.output(4, GPIO.LOW)
            time.sleep(0.02)
            
        
    # Start getBPMLoop routine which saves the BPM in its variable
    def startAsyncBPM(self):
        self.thread = threading.Thread(target=self.getBPMLoop)
        self.thread.stopped = False
        self.thread.start()
        print("Start thread")
        return
        
    # Stop the routine
    def stopAsyncBPM(self):
        self.thread.stopped = True
        self.BPM = 0
        return
