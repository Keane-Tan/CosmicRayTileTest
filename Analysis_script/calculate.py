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

args = parser.parse_args()

# opening root file
_file = rt.TFile.Open(args.inFileName,"READ")

hist_pe_All = rt.TH1F()
hist_pe_Used = rt.TH1F()

# grabbing the histogram from the root file
_file.GetObject("pe",hist_pe_All)
hist_pe_All = hist_pe_All.Clone(hist_pe_All.GetName()+"_")
hist_pe_All.SetDirectory(0)

_file2 = rt.TFile.Open(args.inFileName,"READ")

_file2.GetObject("hist_pe_Used",hist_pe_Used)
hist_pe_Used = hist_pe_Used.Clone(hist_pe_Used.GetName()+"_")
hist_pe_Used.SetDirectory(0)

meanPE = hist_pe_Used.GetMean()
sigma = hist_pe_Used.GetStdDev()
meanErr = hist_pe_Used.GetMeanError()
sigmaErr = hist_pe_Used.GetStdDevError()
meanPETrunc, meanErrTrunc, sigmaTrunc, sigmaErrTrunc = truncMean(hist_pe_Used)

newM = str(meanPE) + "\t" + str(meanErr) + "\t" +str(sigma) + "\t" + str(sigmaErr) + "\t" + str(meanPETrunc) + "\t" + str(meanErrTrunc) + "\t" +str(sigmaTrunc) + "\t" + str(sigmaErrTrunc) + "\t" + "N/A" + "\t" + "N/A" + "\t" + str(int(hist_pe_Used.GetEntries())) + "\t"

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

c1 = rt.TCanvas()
c1.SetLogy()
hist_pe_All.GetXaxis().SetRangeUser(0,200)
hist_pe_All.Draw()
l1 = rt.TLine(0.2*meanPETrunc,0, 0.2*meanPETrunc, hist_pe_Used.GetMaximum())
l2 = rt.TLine(2.0*meanPETrunc,0, 2.0*meanPETrunc, hist_pe_Used.GetMaximum())
l1.Draw("same")
l2.Draw("same")
c1.SaveAs("images/"+args.inFileName[:-5]+"_peTrunc.png")


