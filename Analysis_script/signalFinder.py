import ROOT as rt
import sys, os.path, argparse


# function to find the start (and end) of a signal in a (large) set of samples


def findSignal(tree):
	averageSignal = [0 for x in range(len(tree.data))]
	nEntries = tree.GetEntries()
	for iEvent in range(nEntries):
		tree.GetEvent(iEvent)
		for x in range(len(tree.data)):
			averageSignal[x] -= tree.data[x] #negative because singal is negative
	for x in range(len(averageSignal)):
		averageSignal[x] = averageSignal[x]/float(nEntries)
	#find x value with largest average signal, and start the signal at 20 bins
	# sooner, end the singal 200 bins later. (deltaT of X ns)
	maxBin = averageSignal.index(max(averageSignal))

	c1 = rt.TCanvas()
	hist = rt.TH1F("hist","Average Signal;Time (ns); Signal",1024,0,1024)
	for x in range(len(averageSignal)):
		hist.SetBinContent(x,averageSignal[x])
	hist.Draw()
	c1.SaveAs("averageSignal.png")
	if maxBin - 20 > 0:
		return maxBin-20, maxBin+180
	else:
		sys.exit("Auto-Detect Failed, please manually find signal region")
