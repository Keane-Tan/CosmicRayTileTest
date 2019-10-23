# CosmicRayTileTest

## How to use
1. Create a folder called radTiles in the same directory as the Analysis_script folder and inside radTiles,create another folder with the name of the tile being measured, and save all the root files of the measurements of that tile in the newly created folder.
2. cd into the newly created folder (radTiles/[tile name]).
3. Make sure gedit is closed and run
```
python ../../Analysis_script/run_script.py
```
4. As the code is running, you will be asked if the Gaussian fits to the Count vs ADC voltage plot look good. If not, enter "n", and you will be given a chance to change the range for each Gaussian fit. When the peCalc_script.py is open, look for lines like
```
	startVal = -0.05
	break1 = 0.1
	break2 = 0.27
	break3 = 0.45
	break4 = 0.7
	break5 = 0.9
	endVal = 1.1
 ```
Change the values there.
After saving and closing the peCalc_script.py file, the code will continue running, and you will be asked the same question until you are satisfied with the fit.
5. Find the mean values in the Output/meanValues file. In the file, you will see rows and columns of values that are ready to be copied and pasted into a spreadsheet. The columns mean:
meanPE	meanErr	sigma	sigmaErr	meanPETrunc	meanErrTrunc	sigmaTrunc	sigmaErrTrunc	pulseStart	pulseEnd usedEvents	totalEvents


## Introduction
These scripts were written mainly to calculate the truncated mean light yield of each scintillator tile. The light yield is measured using cosmic ray muons at Lab 6 and recorded by DRS4. The DRS4 records the data in a .dat file, which is converted into .root with a program in the Lab 6 computer. Since cosmic ray muon strikes the SiPM in the set up only ~600 times in 24 hours, we usually try to acquire about 600 muon events to get enough statistics. Unfortunately, the SiPM's performance depends on the temperature in the surrounding, and over the course of 24 hours, temperature fluctuates significantly. So, we usually do an LED calibration, and then perform a 4-hour run. The LED calibration helps us convert from ADC voltage to PE peak number. This conversion can be affected by temperature fluctuation, since it is related to the SiPM's performance. However, 4 hours should hopefully be short enough that the temperature does not fluctuate too widly within the time period. In any case, taking 6 4-hour runs and doing an LED calibration before each run is certainly better than taking one 24-hour run with only one LED calibration done at the beginning of the 24 hours. 

### Optimizing Script Use
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

### Brief Explanation of Each Script
1. run_script.py - it works exactly like a bash script. It creates/deletes folders and files and runs other scripts in the correct sequence, minimizing manual work from user.
2. peCalc_script.py - it calculates the ADC voltage to PE number conversion factor and all the important results such as truncated PE mean etc. It is used on the LED calibration files and the tile measurement files. All the conversion factors for different runs are saved in Output/ConversionFactors.
3. calculate.py - after running over all the LED calibration and tile measurement files, run_script.py will combine all the analysed tile measurement files into a single file via the ROOT function "hadd", effectively adding up all the statistics from different runs. calculate.py then calculates all the important results from the combined file.
