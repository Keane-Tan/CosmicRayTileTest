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
