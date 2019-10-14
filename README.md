# CosmicRayTileTest

## How to use
1. Create a folder called radTiles and inside radTiles,create another folder with the name of the tile being measured, and save all the root files of the measurements of that tile in the newly created folder.
2. cd into the newly created folder (radTiles/[tile name]).
3. Make sure gedit is closed and run
```
python ../../Analysis_script/run_script.py
```
4. As the code is running, you will be asked if the Gaussian fits to the Count vs ADC voltage plot look good. If not, enter "n", and you will be given a chance to change the range for each Gaussian fit. After saving and closing the peCalc_script.py file, the code will continue running, and you will be asked the same question until you are satisfied with the fit.
5. Find the mean values in the Output/meanValues file.

## Introduction
These scripts were written mainly to calculate the truncated mean light yield of each scintillator tile. The light yield is measured using cosmic ray muons at Lab 6 and recorded by DRS4. The DRS4 records the data in a .dat file, which is converted into .root with a program in the Lab 6 computer. Since cosmic ray muon strikes the SiPM in the set up only ~600 times in 24 hours, we usually try to acquire about 600 muon events to get enough statistics. Unfortunately, the SiPM's performance depends on the temperature in the surrounding, and over the course of 24 hours, temperature fluctuates significantly. So, we usually do an LED calibration, and then perform a 4-hour run. The LED calibration helps us convert from ADC voltage to PE peak number. This conversion can be affected by temperature fluctuation, since it is related to the SiPM's performance. However, 4 hours should hopefully be short enough that the temperature does not fluctuate too widly within the time period. In any case, taking 6 4-hour runs and doing an LED calibration before each run is certainly better than taking one 24-hour run with only one LED calibration done at the beginning of the 24 hours. 

To optimize the use of the scripts in this repository, you should do the following:
1. Save the LED calibration files and the tile measurement files in the same folder. The folder should be named after the tile.
2. The LED calibration files should be named as follows:
```
LED_calib[run number]_[date]_vsrc5460
```
[run number] is simply the run number, which goes from 1 to 6 for one tile. An example would be LED_calib3_10232019_vsrc5460. When you start doing an LED calibration for a different tile, [run number] should start from 1 again.
3. The tile measurement files should be named as follows:
```
[number]_[scintillator]_[date]_c[run number]_vsc5460_seal
```
A_EJ200_10232019_c6_vsc5460_seal is an example. Information such as [number] and [scintillator] is provided by Arie.

Note, these scripts were written to handle any number of runs. So if you want to increase the statistics, you can always perform more 4-hour runs. To minimize the temperature effect, you can also perform shorter runs such as 1-hour or 2-hour runs. Just make sure the run number for the LED calibration file is the same the run number of the tile measurement file. 

See https://twiki.cern.ch/twiki/bin/view/Sandbox/URHGCALSOTCosmicRay for detail on the setup and how to measure a tile.
