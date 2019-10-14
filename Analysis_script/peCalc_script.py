# pyROOT script to calculate the photoelectron (pe) yeild of a tile/SiPM cosmicRay setup

import numpy as np
import ROOT as rt
import sys, os.path, argparse
from signalFinder import findSignal
rt.gROOT.SetBatch(True)

def truncMean(histo, acc = 0.001, maxIter = 100): 
	# Arie's method, suposedly more reliable than taking the full mean.
	oldMean = histo.GetMean()
	i = 0
	while True:
		# Step 1: calculate the new mean.
		# New mean is the mean of the range [0.2*oldMean, 2.0*oldMean]
		histo.GetXaxis().SetRangeUser(oldMean*0.2, oldMean*2.0)
		newMean = histo.GetMean() 
		histo.GetXaxis().SetRange() # reset the range for the next iteration.
		i += 1
		if i > maxIter: # provide a way for 'endless' loops to be ended
			sys.exit("maximum number of iterations reached for truncated mean")
			return 0
		if abs(oldMean - newMean) < acc: # breakout condition for the truncMean algorithm
			histo.GetXaxis().SetRangeUser(newMean*0.2, newMean*2.0) # set the range again.
			meanPE = histo.GetMean()
			sigma = histo.GetStdDev()
			meanErr = histo.GetMeanError()
			sigmaErr = histo.GetStdDevError()
			print("TruncMean "
					+ str(meanPE) + " "
					+ str(meanErr) + " "
					+ str(sigma) + " "
					+ str(sigmaErr))
			return meanPE, meanErr, sigma, sigmaErr
		else: # if we don't break the loop, continue on with the iterative process
			oldMean = newMean


parser = argparse.ArgumentParser(description="Calculate the photoelectron (p.e.) yield of a cosmicRay data set.")

parser.add_argument('-f','--file', dest='inFileName', action='store', default='test.root', help='The input file\'s name. Full path if not in running directory. .root extension')
parser.add_argument('-s','--startPulse',dest='pulseStart', action='store',type=int, help='The beginning of the pulse in data. Use -d flag to display plot.')
parser.add_argument('-e','--endPulse',dest='pulseEnd', action='store',type=int, help='The end of the pulse in data. Use -d flag to display plot.')
parser.add_argument('-g','--gainScale', dest='gainScale', action='store', default=1, type=float, help='The gain scale. Default = 1')
parser.add_argument('-d','--display', dest='showPlot', action='store_true', default=False, help='Creates image of all pulses overlayed on one another and quits the program.')
parser.add_argument('-peaks', '--peaks', dest='doPEconversionScaleCalculation',action='store_true',default=False, help="Uses the first five peaks in the RAW output to calculate the Volts-to-PE scalar. You may need to inspect and adjust the limits on each PE gaus function.")
parser.add_argument('-A','--AutoPulse', dest='AutoPulse', action='store_true', default=False, help='Auto-detects the beginning of the average pulse. May need adjusting.')
args = parser.parse_args()

inputFile = rt.TFile(args.inFileName, "READ")
# saving only the parts of the root file we're intrested in.
# For later use and easier access
oldtree = inputFile.Get("T")
oldtree.SetBranchStatus("*",0)
oldtree.SetBranchStatus("event",1) # we may not even need this branch...
oldtree.SetBranchStatus("c1",1)
oldtree.SetBranchStatus("c2",1)
oldtree.SetBranchStatus("c3",1)
oldtree.SetBranchStatus("c4",1)

#auto detect what channel data is in
oldtree.Draw('c1>>ch1Hist')
ch1Hist = rt.gDirectory.Get("ch1Hist")
oldtree.Draw('c2>>ch2Hist')
ch2Hist = rt.gDirectory.Get("ch2Hist")
oldtree.Draw('c3>>ch3Hist')
ch3Hist = rt.gDirectory.Get("ch3Hist")
oldtree.Draw('c4>>ch4Hist')
ch4Hist = rt.gDirectory.Get("ch4Hist")
chMeans = [abs(ch1Hist.GetMean()),
			abs(ch2Hist.GetMean()),
			abs(ch3Hist.GetMean()),
			abs(ch4Hist.GetMean())]
# The channel with the lowest mean is the channel with the data because
# the data is negative.
#dataCh = chMeans.index(min(chMeans))+1 # add one due to python 0 indexing
dataCh = 1
print("data in channel: " + str(dataCh))

# turn off all channels, turn on data channel
oldtree.SetBranchStatus("c1",0)
oldtree.SetBranchStatus("c2",0)
oldtree.SetBranchStatus("c3",0)
oldtree.SetBranchStatus("c4",0)
oldtree.SetBranchStatus('c{}'.format(dataCh),1)
oldtree.SetBranchStatus('t{}'.format(dataCh),1)

if args.showPlot: # plot every event shape ontop of oneanother.
	c = rt.TCanvas('c','c',2000,1000)
	oldtree.Draw("-c{0}:t{0}".format(dataCh))
	c.SaveAs("images/"+args.inFileName[:-5]+".png")
	if not args.AutoPulse:
		sys.exit("Examine the plot and find the pulse edges. Then rerun this script with the correct arguments. (-s [pulseStartBin] -e [pulseEndBin])")

outputFile = rt.TFile(args.inFileName[:-5]+"_analysed.root","RECREATE")
tree = oldtree.CloneTree()
inputFile.Close()
#rename data leaf for easy access later
tree.GetLeaf("c{}".format(dataCh)).SetTitle("data")
tree.GetLeaf("c{}".format(dataCh)).SetName("data")

tree.GetLeaf("t{}".format(dataCh)).SetTitle("time")
tree.GetLeaf("t{}".format(dataCh)).SetName("time")

nEntries = tree.GetEntries()
print("Total Events:" +str(nEntries))

if args.AutoPulse: # recomended
	args.pulseStart, args.pulseEnd = findSignal(tree)

totalEventsOver0p5 = 0 # is signal is 0.5 V, the DSR4 is saturated, and we shoudln't use this point
# this is probably redundant thanks to the trunMean algorithm, but the algorithm was not always used.
# I also used to have a filter on events where the calculated PE was less than 0.5,
# but I removed that after the trunMean algorithm
# i left this one because I figured we might 'hit gold' and get a tile/wrapping combo
# that was fantastic and everything was over 0.5V. ha.
totalBinsOver0p5 = 0

pedestalStart = 99. # the pedestal range is [pulseStart-pedestalStart, pulseStart-pedestalEnd]
pedestalEnd = 30.
deltaPedestal = pedestalStart-pedestalEnd

#sigStart = 60
#sigEnd = 200


pulseDelta  = args.pulseEnd - args.pulseStart
if args.pulseStart < pedestalStart:
	sys.exit("PulseStart has to be greater than {} for the pedestal to work properly. Either re-take the data with a longer delay, or change the pedestal calculation.".format(pedestalStart))

#Values for signal->pe conversion taken from Ping
# 0.96 is Ping's GainScale.
# I wanted to set the default to 1, but not mess up these numbers, so I hardcoded it in.
# these values are depreciated anyway.

#gain_at_1p8V = 8.98e5 * 0.96
#gain_at_3V = 1.7e6 * 0.96 * 0.978543
#gain_at_3V_2050VE = 1.76e6 * 0.96
#conversion_factor_Ping = 1e9/gain_at_3V_2050VE*6.24/50.0/13.0

conversion_factor = 5.39110069975

hist_pe_All = rt.TH1F("pe","Calculated photoelectron count, all events;p.e.;count",100,0,200)
hist_pe_Used = rt.TH1F('hist_pe_Used','Calculated photoelectron count;p.e.;count, no OV',400,0,200)
hist_RAW = rt.TH1F('hist_RAW','Raw Output;ADC/Integrated Voltage;Count',500,-0.2,2)
hist_Ped = rt.TH1F("hist_Ped","Pedestal Output;ADC/Voltage;Count",500,-0.01,1.1)

rt.gStyle.SetOptStat("MRen")
if args.pulseStart:
#	nEntriesRange = np.concatenate((np.arange(0,157,1),np.arange(477,1000,1))) # testing timing problem

	for iEvent in range(nEntries):
		eventOver0p5flag = False
		tree.GetEvent(iEvent)
		dataVector = tree.data
		ped = 0 # Calculate the pedestal value
		for pedBin in range(int(args.pulseStart-pedestalStart),int(args.pulseStart-pedestalEnd)):
			ped -= dataVector[pedBin] # minus because signal is negative
		hist_Ped.Fill(ped/(deltaPedestal)*pulseDelta)
		sig = -ped/deltaPedestal*pulseDelta # Calculate the integral of the pulse, corrected for the pedestal 
		# NOTE: ped/deltaPedestal is the average pedestal per bin, and pulseDelta is the  number of bins in the pulse.
		for sigBin in range(args.pulseStart, args.pulseEnd):
			sig -= dataVector[sigBin] # minus because signal is negative
			if -dataVector[sigBin] >= 0.499908: # check to make sure that the event didnt produce a signal greater than 0.5 volts. 
				totalBinsOver0p5 += 1
				eventOver0p5flag = True
		if eventOver0p5flag:
			totalEventsOver0p5 += 1
	
		# Convert integrated pulse into # p.e.
		pe = sig*conversion_factor
		hist_pe_All.Fill(pe)
		hist_RAW.Fill(sig)
		if (not eventOver0p5flag):
			hist_pe_Used.Fill(pe)

	print("Total number of Events (Bins) over voltage: "+str(totalEventsOver0p5)+ " ("+str(totalBinsOver0p5)+")")

if args.doPEconversionScaleCalculation:
	# The limits need to be manually changed. Approximate the mid point between
	# each peak. To do this, run this program once without doPEconversionScaleCalculation
	# and look at the RAW histogram.
	# If the peaks arn't distinct enough, take more data or further
	# seperate the SiPM from the tile.

# Use these when the first peak is at 0 ADC
	startVal = -0.05
	break1 = 0.1
	break2 = 0.27
	break3 = 0.45
	break4 = 0.62
	break5 = 0.79
	endVal = 1.04

	pe1 = rt.TF1("pe1",'gaus',startVal,break1)
	pe1.SetLineColor(rt.kGreen)
	pe2 = rt.TF1("pe2",'gaus',break1,break2)
	pe2.SetLineColor(rt.kGreen)
	pe3 = rt.TF1("pe3",'gaus',break2,break3)
	pe3.SetLineColor(rt.kGreen)
	pe4 = rt.TF1("pe4",'gaus',break3,break4)
	pe4.SetLineColor(rt.kGreen)
	pe5 = rt.TF1("pe5",'gaus',break4,break5)
	pe5.SetLineColor(rt.kGreen)
	pe6 = rt.TF1("pe6",'gaus',break5,endVal)
	pe6.SetLineColor(rt.kGreen)
	
	#total = rt.TF1("fourPeaks","gaus(0)+gaus(3)+gaus(6)+gaus(9)",startVal,endVal)
	total = rt.TF1("sixPeaks","gaus(0)+gaus(3)+gaus(6)+gaus(9)+gaus(12)+gaus(15)",startVal,endVal)
	
	hist_RAW.Fit(pe1,"R")
	hist_RAW.Fit(pe2,"R+")
	hist_RAW.Fit(pe3,"R+")
	hist_RAW.Fit(pe4,"R+")
	hist_RAW.Fit(pe5,"R+")
	hist_RAW.Fit(pe6,"R+")
	
	total.SetParameter(0, pe1.GetParameter(0))
	total.SetParameter(1, pe1.GetParameter(1))
	total.SetParameter(2, pe1.GetParameter(2))
	total.SetParameter(3, pe2.GetParameter(0))
	total.SetParameter(4, pe2.GetParameter(1))
	total.SetParameter(5, pe2.GetParameter(2))
	total.SetParameter(6, pe3.GetParameter(0))
	total.SetParameter(7, pe3.GetParameter(1))
	total.SetParameter(8, pe3.GetParameter(2))
	total.SetParameter(9, pe4.GetParameter(0))
	total.SetParameter(10, pe4.GetParameter(1))
	total.SetParameter(11, pe4.GetParameter(2))
	total.SetParameter(12, pe5.GetParameter(0))
	total.SetParameter(13, pe5.GetParameter(1))
	total.SetParameter(14, pe5.GetParameter(2))
	total.SetParameter(15, pe6.GetParameter(0))
	total.SetParameter(16, pe6.GetParameter(1))
	total.SetParameter(17, pe6.GetParameter(2))
	
	hist_RAW.Fit(total,"R+")

	c1 = rt.TCanvas()
	hist_RAW.GetXaxis().SetRangeUser(0,200)
	hist_RAW.Draw()
	c1.SaveAs("images/"+args.inFileName[:-5]+"_RAW.png")
	
	print("Current Conversion Factor = " +str(conversion_factor))
#	newCF = (1.0/total.GetParameter(1)+
#			2.0/total.GetParameter(4)+
#			3.0/total.GetParameter(7)+
#			4.0/total.GetParameter(10)+
#			5.0/total.GetParameter(13))/5.0
#			#6.0/total.GetParameter(16))/6.0

	newCF = (1.0/total.GetParameter(4)+
			2.0/total.GetParameter(7)+
			3.0/total.GetParameter(10)+
			4.0/total.GetParameter(13)+
			5.0/total.GetParameter(16))/5.0
			#6.0/total.GetParameter(16))/6.0

	print("New Conversion Factor = " + str(newCF))

	# Open file to save PE Conversion Factors
	cfile_dir = 'Output/ConversionFactors'
	cfile = open(cfile_dir,'r+')
	cf = cfile.readlines()	
	cf.append(str(newCF)+"\n")
	# save and close conversion factor file
	cfile.seek(0) 	# this together with .truncate() allows us to overwrite the OptimalTilePara.txt
	cfile.writelines(cf)
	cfile.truncate()
	cfile.close()


meanPE = hist_pe_Used.GetMean()
sigma = hist_pe_Used.GetStdDev()
meanErr = hist_pe_Used.GetMeanError()
sigmaErr = hist_pe_Used.GetStdDevError()

#	print("# of Events that don't saturate: {} ".format(hist_pe_Used.GetEntries()))
#	print("                    p.e.           err        stdDev            err")
#	print("Full Mean " + str(meanPE) + " " + str(meanErr) + " " +str(sigma) + " " + str(sigmaErr))
meanPETrunc, meanErrTrunc, sigmaTrunc, sigmaErrTrunc = truncMean(hist_pe_Used)
#	print("Pulse Range: " + str(args.pulseStart) + " - " + str(args.pulseEnd))
#	print("F1or Copying into Excel:")
#	print("meanPE meanErr sigma sigmaErr meanPETrunc meanErrTrunc sigmaTrunc sigmaErrTrunc pulseStart pulseEnd usedEvents totalEvents")
#	print(str(meanPE) + " " + str(meanErr) + " " +str(sigma) + " " + str(sigmaErr) + " " + str(meanPETrunc) + " " + str(meanErrTrunc) + " " +str(sigmaTrunc) + " " + str(sigmaErrTrunc) + " " + str(args.pulseStart) + " " + str(args.pulseEnd) + " " + str(int(hist_pe_Used.GetEntries())) + " " + str(nEntries))
newM = str(meanPE) + "\t" + str(meanErr) + "\t" +str(sigma) + "\t" + str(sigmaErr) + "\t" + str(meanPETrunc) + "\t" + str(meanErrTrunc) + "\t" +str(sigmaTrunc) + "\t" + str(sigmaErrTrunc) + "\t" + str(args.pulseStart) + "\t" + str(args.pulseEnd) + "\t" + str(int(hist_pe_Used.GetEntries())) + "\t" + str(nEntries)

c2 = rt.TCanvas()
c2.SetLogy()
hist_pe_All.GetXaxis().SetRangeUser(0,200)
hist_pe_All.Draw()
l1 = rt.TLine(0.2*meanPETrunc,0, 0.2*meanPETrunc, hist_pe_Used.GetMaximum())
l2 = rt.TLine(2.0*meanPETrunc,0, 2.0*meanPETrunc, hist_pe_Used.GetMaximum())
l1.Draw("same")
l2.Draw("same")
c2.SaveAs("images/"+args.inFileName[:-5]+"_peTrunc.png")

outputFile.Write() 	
outputFile.Close()

if not args.doPEconversionScaleCalculation:
	# Open file to save mean values
	mfile_dir = 'Output/meanValues'
	mfile = open(mfile_dir,'r+')
	mf = mfile.readlines()	
	mf.append(str(newM)+"\n")
	# save and close mean values file
	mfile.seek(0) 	# this together with .truncate() allows us to overwrite the OptimalTilePara.txt
	mfile.writelines(mf)
	mfile.truncate()
	mfile.close()

