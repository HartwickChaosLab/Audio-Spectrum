Audio-Spectrum
==============

python script to take an audio spectrum using Labjack U6

For this to work one needs to install the Labjack drivers and python wrappers at http://labjack.com/support/software

This code has been tested on OSX 10.9 Mavericks, but should work on other platforms as well.

This code should be useful for U3, U6, U9 with only obvious modifications, but has been only tested with the U6-Pro

* For GetSpectrumU6.py the U6 does two things:

  * Out put a DC voltage that drives a voltage controlled oscillator (VCO). A VCO outputs a frequency that is dependent on an DC input voltage.

  * Measure and calculate the rms response of an electret microphone that is attached to AIN0 and AIN1.

* For GetSpectrumUSBMic.py the U6 only drives the VCO. The spectrum is taken using pyaudio found at
  http://people.csail.mit.edu/hubert/pyaudio/

This has been tested with a Dayton Audio UMM-6 calibrated USB microphone.


