import sys
import ROOT as root
import math
import os
import shutil
import time
from os import listdir
from os.path import isfile, isdir, join

import tnpEGM_AutoComm as tnpAuto
root.gROOT.LoadMacro('tnpEGM_Plotting.C')
root.gROOT.SetBatch(1)
from ROOT import tnpEGM_Plotting








#======================================
# + Extract inforamation from the block
#======================================
def GetNtupleList (lines):
	ntupleList = []
	tmpInfoArr = {}
	
	name_isMC = ['DT', 'MC']
	
	doFill  = False
	endFill = False
	
	for line in lines:
		#print ("Line content: {}" . format(line))
		
		
		# + ignore comments
		#-------------------
		if (line . startswith("#")):
			continue
		
		
		# + Check if the lines followed can be inserted into list
		#--------------------------------------------------------
		if (line.find("<ntuple>") != -1):
			doFill = True
			continue
		
		
		# + Check the end of ntuple information
		#--------------------------------------
		if (line.find("</ntuple>") != -1):
			doFill = False
			endFill = True
			pass
		
		
		# + Insert line into the array containing an ntuple info
		#-------------------------------------------------------
		if (doFill):
			tmpLine = line . split (" ")
			tmpInfo = []
			
			for substr in tmpLine:
				if (substr != ''):
					substr = substr . replace ('\n', '')
					substr = substr . replace ('\t', '')
					substr = substr . replace (':', '')
					tmpInfo . append (substr)
					pass
				pass
			
			if (len(tmpInfo) == 2):
				tmpInfoArr[tmpInfo[0]] = tmpInfo[1]
				pass
			else:
				tmpInfoArr[tmpInfo[0]] = ''
				pass
			pass
		
		if (endFill):
			ntupleInfo = {}
			
			isMC = int(tmpInfoArr['isMC'])
			
			dirOutput = "/afs/cern.ch/work/e/egmcom/commissioning_automation/output/"
			dirOutput += "ElectronCommissioning{0:04d}/{1}_{2}/" . format(int(tmpInfoArr['year']), tmpInfoArr['reprocessing'], tmpInfoArr['version'])
			tmpInfoArr['dirOutput'] = dirOutput
			
			fileOutput = "hist_run{0:04d}{1}_{2}.root".format(int(tmpInfoArr['year']), tmpInfoArr['runPeriod'], name_isMC[isMC])
			tmpInfoArr['fileOutput'] = fileOutput
			
			
			for tmpNtuple in tmpInfoArr:
				ntupleInfo[tmpNtuple] = tmpInfoArr[tmpNtuple]
				pass
			
			
			# * Test the result
			'''
			print ("\n * Test:")
			for info in ntupleInfo:
				print (" +++  [ {0:15}:  {1} ]" . format (info, ntupleInfo[info]))
				pass
			'''
			
			ntupleList . append (ntupleInfo)
			endFill = False
			pass
		pass
	
	return ntupleList










#================
# + Main function
#================
if __name__ == "__main__":
	# + Create and start a clock here
	#================================
	start_time = time.time()
	
	
	#path_toCheck = "/home/longhoa/ROOT_Work/Task_AutoEGCom/Test/Input/"
	path_toCheck = "/afs/cern.ch/work/e/egmcom/ntuple_production/output/"
	print ("$ Path to check is: {}\n" . format(path_toCheck))
	
	
	
	# + Find the listing files in the directory
	#==========================================
	list_fromPath = []
	print ("$ Preparation: Collecting list of inputs ...")
	
	for obj_file in listdir(path_toCheck):
		if isfile(join (path_toCheck, obj_file)) and obj_file.startswith("ntupleList"):
			name_fromPath = obj_file . replace ("\n", "")
			list_fromPath . append (name_fromPath)
			pass
		pass
	
	print ("$ -- List obtained\n\n")
	
	
	
	# + Check if the list has been used
	#==================================
	print ("$ Preparation: Checking existing lists ...")
	
	#name_listToIgnore = "/home/longhoa/ROOT_Work/Task_AutoEGCom/Test/Input/listToIgnore_01.txt"
	name_listToIgnore = "listToIgnore_01.txt"
	
	# + Create an empty list to store the lists  of files
	#----------------------------------------------------
	# * Lists the will be ignored
	list_fromFile = []
	
	# * Lists to be executed
	list_toExe = []
	
	# * Boolean variable to create the ignore list
	doCreateIgnoreList = False
	
	# + Start checking
	#-----------------
	if os.path.isfile(join(path_toCheck, name_listToIgnore)):
		file_listIgnore = open (join(path_toCheck, name_listToIgnore), "r")
		lines_fromFile = file_listIgnore . readlines()
		
		
		
		for iline in lines_fromFile:
			line = iline . replace ("\n", "")
			
			if (line!="") and (line!="\n"):
				list_fromFile . append (line)
				pass
			pass
		
		count = 0;
		
		for name_fromPath in list_fromPath:
			print ("$ -- form path: %s" %(name_fromPath))
			doFill = True
			
			for name_fromFile in list_fromFile:
				print ("$ --->  from file: %s" %(name_fromFile))
				
				if (name_fromFile == (name_fromPath)):
					doFill = False
					count += 1
					pass
				pass
			
			if (doFill):
				list_toExe . append (name_fromPath)
				pass
			pass
		
		file_listIgnore . close()
		
		print ("$ -- There are {} file to ignore\n" . format(count))
		pass
	else:
		print ("$ -- Ignore list does not exist\n")
		doCreateIgnoreList = True
		for name_fromPath in list_fromPath:
			list_toExe . append (name_fromPath)
			pass
		pass
	
	
	# + Print out the list of file to process
	#----------------------------------------
	if (len(list_toExe) > 0):
		print ("$ -- List of file to process:\n")
		for file_toExe in list_toExe:
			print ("$ -->-- %s" . format(file_toExe))
			pass
		print ("\n")
		pass
	else:
		print ("$ -- No file to process.\n\n")
		pass
	
	
	
	
	
	
	# + Process the ntuples
	#======================
	dirCurrent = os . getcwd()
	
	
	if (len(list_toExe) > 0):
		print ("$ Mainstep 1: Processing the ntuple ... ")
		
		file_pathForPlot = open ("{}/list_pathHistRoot.txt".format(dirCurrent), "w")
		file_pathForPlot . write ("List of output root file:\n")
		
		
		print ("$ -- List of output files: {}/list_pathHistRoot.txt created\n" . format(dirCurrent))
		
		listHistOutput = []
		
		
		#print ("The file name is:")
		for name_toExe in list_toExe:
			file_listInput = open (join(path_toCheck, name_toExe), "r")
			
			lines_fromFile = file_listInput . readlines()
			listntuple     = GetNtupleList (lines_fromFile)
			
			
			
			# + Creating histograms
			#----------------------
			for ntuple in listntuple:
				if os.path.isfile(join(ntuple['dirOutput'], ntuple['fileOutput'])):
					print ("$ -----> Histogram root file is available at:")
					print ("         |- {}/{}" . format(ntuple['dirOutput'], ntuple['fileOutput']))
					print ("         |- Please check the input list for already processed ntuple\n")
					pass
				else:
					tnpAuto . CreateHistogram (ntuple, file_pathForPlot, dirCurrent)
					pass
				pass
			
			
			# + Creating list of output directories
			#--------------------------------------
			index = 0
			
			for ntuple in listntuple:
				if index == 0:
					listHistOutput . append (ntuple['dirOutput'])
					pass
				
				index += 1
				pass
			
			for ntuple in listntuple:
				doFill = False
				nIdentical = 0
				
				for histOut in listHistOutput:
					if ntuple['dirOutput'] == histOut:
						nIdentical += 1
						pass
					pass
				
				if nIdentical == 0:
					listHistOutput . append (ntuple['dirOutput'])
					pass
				pass
			
			
			# + Close input list
			#-------------------
			file_listInput . close()
			pass
		
		# + Close output list
		#--------------------
		file_pathForPlot . close ()
		
		
		# + Making plots
		#---------------
		print ("$ Mainstep 2: Making plots ...")
		
		for histOut in listHistOutput:
			tnpEGM_Plotting (dirCurrent, histOut)
			pass
		
		pass
	else:
		print ("$ Mainstep 1: Processing the ntuple => Skipped\n\n")
		print ("$ Mainstep 2: Making plots => Skipped\n\n")
		pass
	
	
	
	print("$ * It takes {0:.3f} seconds ---" . format (time.time() - start_time))
	
	
	
	
	# + Update the ignore list
	#=========================
	number = 1
	
	if doCreateIgnoreList:
		file_listIgnore = open (join(path_toCheck, name_listToIgnore), "w")
		for name_toExe in list_toExe:
			file_listIgnore . write ("{0}\n" . format (name_toExe))
			number += 1
			pass
		pass
	else:
		file_listIgnore = open (join(path_toCheck, name_listToIgnore), "a")
		for name_toExe in list_toExe:
			file_listIgnore . write ("{0}\n" . format (name_toExe))
			number += 1
			pass
		pass
	
	
	
	
	# + Copy plots to web-page
	#=========================
	print ("$ Mainstep 3: Copy plots to web-page. Checking file availability ...\n")
	dir_src  = "/afs/cern.ch/work/e/egmcom/commissioning_automation/output/"
	dir_dest = "/eos/user/e/egmcom/www/commissioning/"
	
	
	for myDir1 in listdir(dir_src):
		# + 1st layer of loop:
		#---------------------
		#   Check if the dirs for year exist. If not, copy.
		if not myDir1.startswith("ElectronCommissioning"):
			continue
		
		pathSrc1  = "{}{}" . format(dir_src, myDir1)
		pathDest1 = "{}{}" . format(dir_dest, myDir1)
		
		if not isdir (pathDest1):
			print ("$ -- {} is missing, copying ...\n" . format(pathDest1))
			shutil . copytree (pathSrc1, pathDest1)
			pass
		else:
			print ("$ -- {} is available, checking sub-content ...\n" . format(pathDest1))
			for myDir2 in listdir(pathSrc1):
				# + 2nd layer of loop:
				#---------------------
				#   Check if the sub dirs for purpose exist. If not, copy.
				pathSrc2  = "{}/{}" . format(pathSrc1,  myDir2)
				pathDest2 = "{}/{}" . format(pathDest1, myDir2)
				
				if not isdir (pathDest2):
					print ("$ -->-- {} is missing, copying ...\n" . format(pathDest2))
					shutil . copytree (pathSrc2, pathDest2)
					pass
				else:
					print ("$ -->-- {} is available, checking sub-content ...\n" . format(pathDest2))
					
					countMissingRoot = 0
					countCopiedRoot = 0
					
					for myDir3 in listdir(pathSrc2):
						# + 3rd layer of loop:
						#---------------------
						#   Check if the dirs for plots exist. If not, copy.
						pathSrc3  = "{}/{}" . format(pathSrc2,  myDir3)
						pathDest3 = "{}/{}" . format(pathDest2, myDir3)
						
						if myDir3.endswith (".root") and not isfile(pathDest3):
							countMissingRoot += 1
							shutil . copy (pathSrc3, pathDest3)
							countCopiedRoot += 1
							pass
						
						if not isdir(pathDest3) and myDir3.startswith("Plot"):
							print ("$ -->-->-- {} is missing, copying ...\n" . format(pathDest3))
							shutil . copytree (pathSrc3, pathDest3)
							pass
						elif isdir(pathSrc3) and not isdir(pathDest3):
							print ("$ -->-->-- {} is available, checking sub-content ...\n" . format(pathDest3))
							
							countMissingPlot = 0
							countCopiedPlot = 0
							
							for myDir4 in listdir(pathSrc3):
								# + 4th layer of loop:
								#---------------------
								#   Check if the plots exist. If not, copy.
								pathSrc4  = "{}/{}" . format(pathSrc3,   myDir4)
								pathDest4 = "{}/{}" . format(pathDest3,  myDir4)
								
								if not isfile(pathDest4):
									if isfile(pathSrc4):
										countMissingPlot += 1
										shutil . copy (pathSrc4, pathDest4)
										countCopiedPlot += 1
										pass
									pass
								pass
							
							if (countMissingPlot > 0):
								print ("$ -->-->-->-- {} missing plot, {} were copied ...\n" . format(countMissingPlot, countCopiedPlot))
							
							pass
						pass
					
					if (countMissingRoot > 0):
						print ("$ -->-->-- {} missing root file, {} were copied ...\n" . format(countMissingRoot, countCopiedRoot))
						pass
					
					pass
				pass
			pass
		pass
	
	
	
	
	
	
	
	# + Remove temporary list
	#========================
	if os.path.exists("{}/{}" . format(dirCurrent, "list_pathHistRoot.txt")):
		os . remove ("{}/{}" . format(dirCurrent, "list_pathHistRoot.txt"))
		pass
	if os.path.exists("{}/{}" . format(dirCurrent, "list_Variable.txt")):
		os . remove ("{}/{}" . format(dirCurrent, "list_Variable.txt"))
		pass
	
	
	
	pass
