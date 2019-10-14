import os
import glob

# Creating a folder to store important images
if os.path.exists("images"):
	os.system("rm -r images")
os.system("mkdir images")

# Creating a folder to store important output values
if os.path.exists("Output"):
	os.system("rm -r Output")
os.system("mkdir Output")

# Creating a file to store the conversion factors
if os.path.exists("Output/ConversionFactors"):
	os.system("rm Output/ConversionFactors")
os.system("touch Output/ConversionFactors")

# Creating a file to store the mean values
if os.path.exists("Output/meanValues"):
	os.system("rm Output/meanValues")

os.system("touch Output/meanValues")


# list all the LED calibration files
fil = glob.glob("LED_calib*0.root")
fil.sort()
print fil

# Calculate and save all the coversion factors
for iL in fil:
	os.system("python ../../Analysis_script/peCalc_script.py -f "+ iL +" -A -d --peaks")
	os.system("eog images/" + iL[:-5]+"_RAW.png")

	chgaus = raw_input("Are you satisfied with the fit? y/n : ")
	while chgaus == "n":
		# get rid of the wrong conversion factor
		convf = open('Output/ConversionFactors','r+')
		convfac = convf.readlines()
		convfac.pop()
		convf.seek(0) 	
		convf.writelines(convfac)
		convf.truncate()
		convf.close()

		# changing the fit parameters for the gaussian fit in peCalc_script.py
		os.system("eog images/" + iL[:-5]+"_RAW.png & gedit ../../Analysis_script/peCalc_script.py")
		os.system("python ../../Analysis_script/peCalc_script.py -f "+ iL +" -A -d --peaks")
		os.system("eog images/" + iL[:-5]+"_RAW.png")
		chgaus = raw_input("Are you satisfied with the fit? y/n : ")

# list all files that are not LED calibration
allf = glob.glob("*.root")
clf = []

for fi in range(len(allf)):
    if "LED" in allf[fi] or "analysed" in allf[fi]:
            clf.append(allf[fi])
            
for ij in clf:
    allf.remove(ij)

allf.sort()

for fn in allf:
	if "c1" in fn:
		cutoff = fn.find("_c1")
		haf = fn[:cutoff] + ".root" # name of the output file of hadd

if haf in allf:
    allf.remove(haf)
    
allf.sort()

# Open the ConversionFactors file and peCalc_script.py to change the conversion factors
conf = open('Output/ConversionFactors','r+')
confac = conf.readlines()

# Calculate and save all the important results such as truncated mean PE
for ik in range(len(allf)):

	# changing the conversion factor in peCalc_script.py
	scfile = open('../../Analysis_script/peCalc_script.py','r+')
	sc1 = scfile.readlines()

	conval = confac[ik]
	
	cfcode = "conversion_factor = "
	for si in range(len(sc1)):
		if cfcode in sc1[si]:
			sc1[si] = cfcode + conval

	scfile.seek(0)
	scfile.writelines(sc1)
	scfile.truncate()
	scfile.close()

	# calculating and saving the mean values
	os.system("python ../../Analysis_script/peCalc_script.py -f "+ allf[ik] +" -A -d")

# hadd all the individual results
hcom = "hadd -f " + haf + " "
for im in range(len(allf)):
	hcom = hcom + allf[im][:-5] + "_analysed.root "

os.system(hcom)
os.system("python ../../Analysis_script/calculate.py -f "+ haf)

