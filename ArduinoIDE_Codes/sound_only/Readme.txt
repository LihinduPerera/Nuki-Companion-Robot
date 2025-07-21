To get Bluetooth sound input to the esp32 to MAX98357A, latest bluetooth
drivers and latest esp 32 board drivers not supports each other.

step 1: go to Sketch > Include Library > add .zip Library
        and install the ESP32A2DPmain.zip
step 2: after that go to Documents > Arduno > libraries > ESP32-A2DP
        and paste the src.zip file and extract it (this src is DIY by me on 10th july in 2025 - ESP boardSoftware 3.2.1)

**Remember to connect sd to external power's "+" side connect and also you must connect esp32's gnd to external power's "-" side to sink up the sound correctly!!