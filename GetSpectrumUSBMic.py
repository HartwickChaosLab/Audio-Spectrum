# A script using U6 to drive a voltage controlled 
# oscillator which in turn is driving an audio speaker. The script
# also measures the RMS value of the sound via a USB microwphone.
# Requires downloading drivers and python wrappers at 
# http://labjack.com/support/u3 
# This script has been tested on OSX Mavericks, but should be useable
# on windows and linux. Furhtermore U3 should also work.
# Just change u6s to u3s

# Written by Kevin Schultz
# 


import pyaudio
import wave
import sys


import u6
from time import sleep
from datetime import datetime
import traceback
import numpy as np

from pylab import plot, show, title, xlabel, ylabel, subplot

import scipy as sp

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 1
WAVE_OUTPUT_FILENAME = "output.wav"

if sys.platform == 'darwin':
    CHANNELS = 1

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
# MAX_REQUESTS is the number of packets to be read.

# the number of samples will be MAX_REQUESTS times 48 (packets per request) times 25 (samples per packet).
d = u6.U6()

# Set up U6
d.configU6()

# For applying the proper calibration to readings.
d.getCalibrationData()

# Set the FIO0 to Analog
d.configIO()

def getData():
    frames=np.array([],dtype=float)


    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
       data = stream.read(CHUNK)
       frames.append(data)
       
    return(frames)
    
# setDAC takes a voltage value, converts to 16 bit value, then puts
# outputs voltage to channel 0
def setDAC(Volts):
    bVolts=d.voltageToDACBits(Volts,dacNumber=0,is16Bits=True)
    d.getFeedback(u6.DAC16( 0,  bVolts))
    return


# cycleData creates a table of voltages to output to DAC,
# wait for voltage to settle, and store rms value found at input
# variable rms stores the spectrum and is what is returned

def cycleData(lowV, HighV, numV):
    volts=np.linspace(lowV,HighV,numV)    
    rms=np.array([],dtype=float)
    for i in volts:
        setDAC(i)
        sleep(.2)
        rms=np.append(rms,np.std(getData()))
        
    return (rms)

# getFreq is used to get start and stop frequency of run,
# since we are not driving an oscillator directly, rather we 
# use a freq. gen. that has a VCO setting, so we need to know what
# frequencies are start and stop voltages correspond to
# later we assume this is linear. Of course this depends on the 
# freq. gen. and ought to be tested.
    
def getFreq(y,Fs):
    #print Fs
    n = len(y) # length of the signal
    #print n
    k = np.arange(n)

    T = 1.*n/Fs

    #print T
    frq = k/T # two sides frequency range
    frq = frq[range(n/2)] # one side frequency range
    
    Y = sp.fft(y)*10. # fft computing and normalization

#plotting just for testing purposes. not strictly neccessary
    subplot(3,1,1) 
    plot(k,y)
    xlabel('Time')
    ylabel('Amplitude')
    subplot(3,1,2)
    plot(frq, 2.0/n * np.abs(Y[0:n/2])) 
    
    return frq[np.argmax(Y[1:n/2])]

#Bulk of program. Get Low volts, high volts, and number of "frequency
#steps
LowV = float(raw_input("Low Volts [0]: "))
HighV=float(raw_input("High Volts: "))
numVolts=int(raw_input("Num Volts: "))

# Get low Frequency (see above comments)
setDAC(LowV)
#pause=raw_input("wait")
start_Freq=getFreq(getData(),SCAN_FREQ)

print start_Freq

#Get High Frequency (see above)
setDAC(HighV)
sleep(1)
#pause=raw_input("wait")
end_Freq=getFreq(getData(),SCAN_FREQ)
print end_Freq

#take spectrum
spectrum=cycleData(LowV, HighV, numVolts)

# generate linear frequency space for plotting spectrum (assumption)
freq=np.linspace(start_Freq,end_Freq,numVolts)
subplot(3,1,3)
plot(freq,spectrum)
setDAC(0) # return Freq. Gen. to starting value

#close connection to Labjack If there is an error, be sure to 
#type d.close() into console to get communication to work next time
# you run. Important on Mac.
d.close()  
