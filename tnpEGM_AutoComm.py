# + Usage:
# *python   tnpEGM_commissioningRun2017BUL_DF.py   &> log2017FUL.txt &



import sys
import ROOT
from ROOT import gStyle
from ROOT import gROOT
import math
import os
import re

ROOT.gROOT.SetBatch(True)




###https://swan001.cern.ch/user/shilpi/notebooks/SWAN_projects/df104_HiggsToTwoPhotons.py.nbconvert/df104_HiggsToTwoPhotons.py.nbconvert.ipynb
###Enable multi-threading
#ROOT.EnableImplicitMT()



#gROOT.TH1.AddDirectory(kFalse)



# + Compute the effective area
#=============================
# * Type of area:
#----------------
#   - Neutral hadron:  1
#   - Charged hadron:  2
#   - Photon:          3
#   - Combined:        4
Compute_effArea = """
	double EffArea (int type_iso, double eta)
	{
		double areaToReturn = 0;
		
		int   idxEta = -1;
		float rangeEta[] = {1.000, 1.479, 2.000, 2.200, 2.300, 2.400};
		
		
		double effArea[4][7] =
		{
			{0.0595, 0.0869, 0.0803, 0.0398, 0.0401, 0.0502, 0.0802},
			{0.0234, 0.0222, 0.0072, 0.0157, 0.0170, 0.0153, 0.0140},
			{0.1314, 0.1125, 0.0755, 0.1125, 0.1539, 0.1733, 0.1974},
			{0.1703, 0.1715, 0.1213, 0.1230, 0.1635, 0.1937, 0.2393}
		};
		
		for (int i=0; i<6; i++)
		{
			if (eta<rangeEta[i] && eta>=0)
			{
				idxEta = i;
				break;
			}
		}
		
		if (idxEta==-1 && eta>=0)
		{
			idxEta = 6;
		}
		
		
		areaToReturn = effArea[type_iso][idxEta];
		
		return areaToReturn;
	}"""

ROOT . gInterpreter . Declare (Compute_effArea)




# + Compute the invariant mass
#=============================
Compute_invMass = """
	double ComputeInvariantMass (double pt1, double eta1, double phi1, double pt2, double eta2, double phi2)
	{
		TLorentzVector v1;
		TLorentzVector v2;
		
		v1.SetPtEtaPhiM(pt1, eta1, phi1, 0.511*0.001);
		v2.SetPtEtaPhiM(pt2, eta2, phi2, 0.511*0.001);
		
		TLorentzVector z    = v1 + v2;
		
		double mass    = z.M();
		return mass;
	}"""

ROOT . gInterpreter . Declare (Compute_invMass)




# + Loop over the tree
#=====================
#def loopTree (lineFromList):
def CreateHistogram (listInfo, file_pathForPlot, dirCurrent):
	# + Information for input
	#========================
	usephoid = False
	
	treename = 'tnpEleIDs/fitter_tree'
	
	if usephoid:
		treename = 'tnpPhoIDs/fitter_tree'
		pass
	
	name_fileInput  = listInfo['fileInput']
	name_fileOutput = listInfo['fileOutput']
	name_dirOutput  = listInfo['dirOutput']
	isMC            = bool(int(listInfo['isMC']))
	name_filePU     = listInfo['filePU']
	name_treePU     = listInfo['treePU']
	runPeriod       = listInfo['runPeriod']
	luminosity      = float(listInfo['luminosity'])
	
	
	
	
	# + Open input file
	#==================
	print("$ -- Processing file {} ..." . format(name_fileInput))
	
	file_input = ROOT.TFile . Open (name_fileInput)
	tree_input = file_input . Get (treename)
	
	
	if(isMC):
		friendTreeName = name_treePU
		tree_input . AddFriend (friendTreeName, name_filePU)
		pass
	
	dataFrame = ROOT.RDataFrame(tree_input)
	
	#print "PRINTING DATAFRAME"
	#print(dataFrame.GetColumnNames())
	
	
	if isMC:
		print ("$ -----> Is MC, getting weight from %s.totWeight" %(friendTreeName))
		dataFrame = dataFrame.Define ("ev_weight", "%s.totWeight" %(friendTreeName))
		pass
	if not isMC:
		print ("$ -----> Is Data, all weights are set to 1.0")
		dataFrame = dataFrame.Define ("ev_weight", "1.0")
		pass
	
	dataFrame = dataFrame.Define ("neuphoIso", "max (el_neuIso + el_phoIso - EffArea(4, el_sc_abseta) * event_rho.rho,  0.0)") ###0. is imp and not 0 else double vs int complaint
	
	dataFrame = dataFrame.Define ("neu_A", "EffArea(1, el_sc_abseta)")
	dataFrame = dataFrame.Define ("cha_A", "EffArea(2, el_sc_abseta)")
	dataFrame = dataFrame.Define ("pho_A", "EffArea(3, el_sc_abseta)")
	
	dataFrame = dataFrame.Define ("combinedProbeIso", "(neuphoIso+el_chIso)/el_pt")
	
	dataFrame = dataFrame.Define ("el_neuIso_puSub", "max (el_neuIso - neu_A*event_rho.rho,  0.0)")
	dataFrame = dataFrame.Define ("el_phoIso_puSub", "max (el_phoIso - pho_A*event_rho.rho,  0.0)")
	dataFrame = dataFrame.Define ("el_chIso_puSub",  "max (el_chIso - cha_A*event_rho.rho,   0.0)")
	
	dataFrame = dataFrame.Define ("el_relphoIso_puSub", "el_phoIso_puSub/el_pt")
	dataFrame = dataFrame.Define ("el_relneuIso_puSub", "el_neuIso_puSub/el_pt")
	dataFrame = dataFrame.Define ("el_relchIso_puSub",  "el_chIso_puSub/el_pt")
	
	dataFrame = dataFrame.Define ("el_relphoIso", "el_phoIso/el_pt")
	dataFrame = dataFrame.Define ("el_relneuIso", "el_neuIso/el_pt")
	dataFrame = dataFrame.Define ("el_relchIso",  "el_chIso/el_pt")
	
	dataFrame = dataFrame.Define ("sc_pt_p",    "el_sc_e/cosh(el_sc_eta)")
	dataFrame = dataFrame.Define ("scraw_pt_p", "el_sc_rawE/cosh(el_sc_eta)")
	dataFrame = dataFrame.Define ("seed_pt_p",  "el_seed_e/cosh(el_sc_eta)")
	dataFrame = dataFrame.Define ("sc_pt_t",    "tag_sc_e/cosh(tag_sc_eta)")
	
	
	##########################PROBE#########################
	dataFrame = dataFrame.Define ("mass_sc",           "ComputeInvariantMass(sc_pt_p, el_eta, el_phi, sc_pt_t, tag_Ele_eta, tag_Ele_phi)")
	dataFrame = dataFrame.Define ("el_sc_esETorawSC",  "el_sc_esE/el_sc_rawE")
	
	dataFrame         = dataFrame.Filter ("tag_Ele_pt>40  &&  tag_sc_abseta<1.4442  &&  el_et>20  &&  el_sc_abseta<2.5  &&  pair_mass>80  &&  pair_mass<100")
	dataFrameEBIso    = dataFrame.Filter ("el_sc_abseta<=1.479  &&  el_5x5_sieie<0.0105  &&  fabs(el_dEtaIn)<0.00387  &&  fabs(el_dPhiIn)<0.0716  &&  el_hoe<0.05  &&  (fabs(el_dxy))<0.060279  &&  fabs(el_dz)<0.800538")
	dataFrameEBSS     = dataFrame.Filter ("el_sc_abseta <= 1.479 && combinedProbeIso<0.1")
	dataFrameEEIso    = dataFrame.Filter ("el_sc_abseta > 1.566 && el_sc_abseta < 2.5 && el_5x5_sieie < 0.0356 and fabs(el_dEtaIn) < 0.0072 and fabs(el_dPhiIn) < 0.147 and el_hoe  < 0.0414  and fabs(el_dxy) < 0.273 and fabs(el_dz) < 0.885860")
	dataFrameEESS     = dataFrame.Filter ("el_sc_abseta > 1.566 && el_sc_abseta < 2.5 && combinedProbeIso<0.1")
	dataFrameTPEBEBSS = dataFrame.Filter ("tag_sc_abseta <= 1.479 && el_sc_abseta <= 1.479 && combinedProbeIso<0.1")
	dataFrameTPEBEESS = dataFrame.Filter ("tag_sc_abseta <= 1.479 && el_sc_abseta > 1.566 && el_sc_abseta < 2.5 && combinedProbeIso<0.1")
	dataFrameTPEEEBSS = dataFrame.Filter ("el_sc_abseta > 1.566 && tag_sc_abseta<2.5 && el_sc_abseta <= 1.479 && combinedProbeIso<0.1")
	dataFrameTPEEEESS = dataFrame.Filter ("tag_sc_abseta > 1.566 && tag_sc_abseta<2.5 && el_sc_abseta > 1.566 && el_sc_abseta < 2.5 && combinedProbeIso<0.1")
	
	
	###define hists and xaxis
	histList = {}
	xTitle   = {}
	
	###Last argument is for mass pair of EB_EE etc
	print ("$ -- Filling the histograms")
	fillHists (histList, dataFrameEBSS,     "EB",    True,  False) ## which means its for SS
	fillHists (histList, dataFrameEBIso,    "EB",    False, False) ## which means its for Iso
	fillHists (histList, dataFrameEESS,     "EE",    True,  False)
	fillHists (histList, dataFrameEEIso,    "EE",    False, False)
	fillHists (histList, dataFrameTPEBEBSS, "EB_EB", True,  True)
	fillHists (histList, dataFrameTPEBEESS, "EB_EE", True,  True)
	fillHists (histList, dataFrameTPEEEBSS, "EB_EE", True,  True)
	fillHists (histList, dataFrameTPEEEESS, "EE_EE", True,  True)
	
	defineeXtitle (histList, xTitle)
	
	
	
	
	# + Create path fpr output
	#=========================
	if not os.path.exists(name_dirOutput):
		print ("\n$ -- Output directory {0} is missing, now creating ...\n" . format (name_dirOutput))
		os.makedirs (name_dirOutput)
		pass
	else:
		print ("\n$ -- Output directory {0} is available\n" . format (name_dirOutput))
		pass
	
	
	
	
	# + Create output root file
	#==========================
	namefile_isMC = ["DT", "MC"]
	
	print ("$ -- Creating output file: {0}{1} ..." . format (name_dirOutput, name_fileOutput))
	file_output = ROOT.TFile("{0}{1}".format (name_dirOutput, name_fileOutput), "RECREATE")
	
	file_output . cd()
	
	for key in histList:
		histList[key] . Sumw2()
		histList[key] . SetDirectory(0)
		
		histList[key] . Write()
		
		#print ("         |- key: %22s,  integral = %8.1f" %(key, histList[key].Integral()))
		
		pass
	
	file_output . Write()
	file_output . Close()
	
	print ("$ -----> Output file {0}{1} has been saved" . format (name_dirOutput, name_fileOutput))
	
	
	
	
	# + Write to file the name of the output root files
	#==================================================
	print ("$ -----> Output file {0}{1} has been written to file\n" . format (name_dirOutput, name_fileOutput))
	
	file_pathForPlot . write ("run{0}  {1:.2f}  {2}{3}\n" . format (runPeriod, luminosity, name_dirOutput, name_fileOutput))
	
	
	
	
	# + Write to file the name of the variables
	#==========================================
	if (not os.path.isfile("{0}/list_Variable.txt" . format(dirCurrent))):
		print ("$ -- List of variables is not available, being created\n\n")
		file_listVariable = open ("{0}/list_Variable.txt" . format(dirCurrent), "w")
		
		for key in histList:
			file_listVariable . write ("nameVariable: {0}\n" . format(key))
			pass
		
		pass
	else:
		print ("$ -- List of variables is available\n\n")
	
	pass







# + Fill histograms using RDataFrame
#===================================
def fillHists (histList, dataFrame, reg, forSS, forRegMass):
	print ("$ -----> forSS: {0} and forRegMass: {1}" . format(forSS, forRegMass))
	
	if(forSS and not forRegMass):
		histList['el_sc_eta'] = dataFrame.Histo1D (('el_sc_eta','SC #eta',50,-2.5,2.5), "el_sc_eta","ev_weight")
		# + Probe electron
		#-----------------
		histList['el_sc_phi'] = dataFrame.Histo1D (('el_sc_phi', 'SC #phi', 70, -3.5,  3.5),  "el_sc_phi", "ev_weight")
		histList['el_eta']    = dataFrame.Histo1D (('el_eta',    '#eta',    50, -2.5,  2.5),  "el_eta",    "ev_weight")
		histList['el_phi']    = dataFrame.Histo1D (('el_phi' ,   '#phi',    70, -3.5,  3.5),  "el_phi",    "ev_weight")
		
		# + Tag electron
		#---------------
		histList['tag_sc_phi'] = dataFrame.Histo1D (('tag_sc_phi', 'Tag SC #phi', 70, -3.5,  3.5), "tag_Ele_phi", "ev_weight")
		
		# + Event variables
		#------------------
		histList['event_nPV_wei'] = dataFrame.Histo1D (('event_nPV_wei', '#vertices',  70, 0.0, 70.0),   "event_nPV.mNPV", "ev_weight")
		histList['event_rho']     = dataFrame.Histo1D (('event_rho',     '#rho',      100, 0.0, 50.0),   "event_rho.rho",  "ev_weight")
		histList['event_nPV']     = dataFrame.Histo1D (('event_nPV' ,    '#vertices',  70, 0.0, 70.0),   "event_nPV.mNPV")
		
		pass
	
	
	
	if(forSS and forRegMass):
		histList['pair_mass_%s'%(reg)] = dataFrame.Histo1D (('pair_mass_%s' %(reg), 'Di-lepton invariant mass',60,60,120), "pair_mass", "ev_weight")
		pass
	
	
	
	if (not forSS) and (not forRegMass):
		print ("$ -----> Now doing iso\n")
		
		# + Absolute isolation
		#---------------------
		histList['el_chIso_%s'  %(reg)] = dataFrame.Histo1D (('el_chIso_%s' %(reg),  'Charged isolation', 20, 0, 5), "el_chIso",  "ev_weight")
		histList['el_neuIso_%s' %(reg)] = dataFrame.Histo1D (('el_neuIso_%s' %(reg), 'Neutral isolation', 20, 0, 5), "el_neuIso", "ev_weight")
		histList['el_phoIso_%s' %(reg)] = dataFrame.Histo1D (('el_phoIso_%s' %(reg), 'Photon isolation',  20, 0, 5), "el_phoIso", "ev_weight")
		
		# + Relative isolation
		#---------------------
		histList['el_relchIso_%s' %(reg)]     = dataFrame.Histo1D (('el_relchIso_%s' %(reg),  'Rel. Charged isolation', 60, 0.0, 0.6), "el_relchIso",  "ev_weight")
		histList['el_relneuIso_%s' %(reg)]    = dataFrame.Histo1D (('el_relneuIso_%s' %(reg), 'Rel. Neutral isolation', 60, 0.0, 0.6), "el_relneuIso", "ev_weight")
		histList['el_relphoIso_%s' %(reg)]    = dataFrame.Histo1D (('el_relphoIso_%s' %(reg), 'Rel. Photon isolation',  60, 0.0, 0.6), "el_relphoIso", "ev_weight")
		
		# + PU subtracted isolation
		#--------------------------
		histList['el_chIso_puSub_%s' %(reg)]  = dataFrame.Histo1D (('el_chIso_puSub_%s' %(reg),  'PU subtracted Charged isolation', 20, 0.0, 5.0), "el_chIso_puSub",  "ev_weight")
		histList['el_neuIso_puSub_%s' %(reg)] = dataFrame.Histo1D (('el_neuIso_puSub_%s' %(reg), 'PU subtracted Neutral isolation', 20, 0.0, 5.0), "el_neuIso_puSub", "ev_weight")
		histList['el_phoIso_puSub_%s' %(reg)] = dataFrame.Histo1D (('el_phoIso_puSub_%s' %(reg), 'PU subtracted Photon isolation',  20, 0.0, 5.0), "el_phoIso_puSub", "ev_weight")
		
		
		# + Rel.PU subtracted isolation
		#------------------------------
		histList['el_relchIso_puSub_%s' %(reg)]  = dataFrame.Histo1D (('el_relchIso_puSub_%s' %(reg),  'Rel. PU subtracted Charged isolation', 20, 0.0, 5.0), "el_relchIso_puSub",  "ev_weight")
		histList['el_relneuIso_puSub_%s' %(reg)] = dataFrame.Histo1D (('el_relneuIso_puSub_%s' %(reg), 'Rel. PU subtracted Neutral isolation', 20, 0.0, 5.0), "el_relneuIso_puSub", "ev_weight")
		histList['el_relphoIso_puSub_%s' %(reg)] = dataFrame.Histo1D (('el_relphoIso_puSub_%s' %(reg), 'Rel. PU subtracted Photon isolation',  20, 0.0, 5.0), "el_relphoIso_puSub", "ev_weight")
		
		#histList['el_ecalIso_%s' %(reg)]      = dataFrame.Histo1D (('el_ecalIso_%s' %(reg),'ECAL Isolation',20,0,5),"el_ecalIso","ev_weight")
		#histList['el_ecalIso_%s' %(reg)].Sumw2()
		pass
	
	if(forSS and not forRegMass):
		nbins = 35
		xmin  = 0.005
		xmax  = 0.012
		
		if reg == 'EE':
			nbins = 40
			xmin  = 0.015
			xmax  = 0.035
			pass
		
		
		# + Shower-shape variables
		#-------------------------
		histList['el_sieie_%s' %(reg)]     = dataFrame.Histo1D (('el_sieie_%s' %(reg),     '#sigma(i#etai#eta)', nbins, xmin, xmax),     "el_sieie","ev_weight")
		histList['el_r9_%s' %(reg)]        = dataFrame.Histo1D (('el_r9_%s' %(reg),        '#r9', 110, 0.00, 1.50),                      "el_r9","ev_weight")
		histList['el_r9_upto1_%s' %(reg)]  = dataFrame.Histo1D (('el_r9_upto1_%s' %(reg),  '#r9', 110, 0.40, 1.00),                      "el_r9","ev_weight")
		histList['el_5x5_sieie_%s' %(reg)] = dataFrame.Histo1D (('el_5x5_sieie_%s' %(reg), '5x5 #sigma(i#etai#eta)', nbins, xmin, xmax), "el_5x5_sieie","ev_weight")
		
		# + Electrons (both tag and probe)
		#---------------------------------
		histList['el_sc_phi_%s' %(reg)] = dataFrame.Histo1D (('el_sc_phi_%s' %(reg),'SC #phi',70,-3.5,3.5), "el_sc_phi","ev_weight")
		histList['tag_sc_phi_%s' %(reg)] = dataFrame.Histo1D (('tag_sc_phi_%s' %(reg),'tag SC #phi',70,-3.5,3.5), "tag_Ele_phi","ev_weight")
		histList['el_dEtaIn_%s' %(reg)] = dataFrame.Histo1D (('el_dEtaIn_%s' %(reg),'#Delta#eta_{in}',50,-0.04,0.04), "el_dEtaIn","ev_weight")
		histList['el_dPhiIn_%s' %(reg)] = dataFrame.Histo1D (('el_dPhiIn_%s' %(reg),'#Delta#eta_{in}',50,-0.2,0.2), "el_dPhiIn","ev_weight")
		#histList['el_et_%s' %(reg)] = dataFrame.Histo1D (('el_et_%s' %(reg),'E_{T}',50,0,100)
		histList['el_et_%s' %(reg)] = dataFrame.Histo1D (('el_et_%s' %(reg),'E_{T}',50,20,100), "el_et","ev_weight")
		#histList['pair_mass_%s' %(reg)] = dataFrame.Histo1D (('pair_mass_%s' %(reg),'Di-lepton invariant mass',40,80,100)
		histList['pair_mass_%s' %(reg)] = dataFrame.Histo1D (('pair_mass_%s' %(reg),'Di-lepton invariant mass',60,60,120), "pair_mass","ev_weight")
		histList['mass_sc_%s' %(reg)] = dataFrame.Histo1D (('mass_sc_%s' %(reg),'Di-lepton invariant mass using SC energy',60,60,120), "mass_sc","ev_weight")
		histList['el_hoe_%s' %(reg)] = dataFrame.Histo1D (('el_hoe_%s' %(reg),'H/E',20,0.,0.2), "el_hoe","ev_weight")
		histList['el_mHits_%s' %(reg)] = dataFrame.Histo1D (('el_mHits_%s' %(reg),'missing hits',4,0.,4),"el_mHits","ev_weight")
		histList['el_5x5_r9_%s' %(reg)] = dataFrame.Histo1D (('el_5x5_r9_%s' %(reg),'r9 (5x5)',110,0.0,1.5), "el_5x5_r9","ev_weight")
		histList['el_5x5_r9_upto1_%s' %(reg)] = dataFrame.Histo1D (('el_5x5_r9_upto1_%s' %(reg),'r9 (5x5)',110,0.4,1.), "el_5x5_r9","ev_weight")
		histList['el_etaW_%s' %(reg)] = dataFrame.Histo1D (('el_etaW_%s' %(reg),'#eta width',50,0.,0.05), "el_etaW","ev_weight")
		histList['el_phiW_%s' %(reg)] = dataFrame.Histo1D (('el_phiW_%s' %(reg),'#phi width',50,0.,0.5), "el_phiW","ev_weight")
		histList['el_fbrem_%s' %(reg)] = dataFrame.Histo1D (('el_fbrem_%s' %(reg),'#fBrem',25,0.,1), "el_fbrem","ev_weight")
		histList['el_sc_esE_%s' %(reg)] = dataFrame.Histo1D (('el_sc_esE_%s' %(reg),'preshower Energy',40,0.,40), "el_sc_esE","ev_weight")
		#histList['el_sc_esETorawSC_%s' %(reg)] = dataFrame.Histo1D (('el_sc_esETorawSC_%s' %(reg),'preshower Energy/rawSC',100,0.,0.35)
		histList['el_sc_esETorawSC_%s' %(reg)] = dataFrame.Histo1D (('el_sc_esETorawSC_%s' %(reg),'preshower Energy/rawSC',30,0.,0.30),"el_sc_esETorawSC","ev_weight")
		histList['el_sc_e_%s' %(reg)] = dataFrame.Histo1D (('el_sc_e_%s' %(reg),'SC Energy',50,0.,250), "el_sc_e","ev_weight")
		histList['el_sc_rawE_%s' %(reg)] = dataFrame.Histo1D (('el_sc_rawE_%s' %(reg),'SC Raw Energy',50,0.,250), "el_sc_e","ev_weight")
		histList['el_chisq_%s' %(reg)] = dataFrame.Histo1D (('el_chisq_%s' %(reg),'#chi^{2}',50,0.,200), "el_gsfchi2","ev_weight")
		histList['el_dxy_%s' %(reg)] = dataFrame.Histo1D (('el_dxy_%s' %(reg),'dxy',40,-0.1,0.1), "el_dxy","ev_weight")
		histList['el_dz_%s' %(reg)] = dataFrame.Histo1D (('el_dz_%s' %(reg),'dz',40,-0.1,0.1), "el_dz","ev_weight")
		histList['el_nonTrigMVA80X_%s' %(reg)] = dataFrame.Histo1D (('el_nonTrigMVA80X_%s' %(reg),'nonTrigMVA80X',50,-1,1), "el_nonTrigMVA80X","ev_weight")
		histList['el_eoverp_wES_%s' %(reg)] = dataFrame.Histo1D (('el_eoverp_wES_%s' %(reg),'el_eoverp_wES',20,0.,1.6), "el_eoverp_wES","ev_weight")
		
		pass
	pass






# + Set title for the histograms
#===============================
def defineeXtitle (histList, xTitle):
	region = ['EB','EE']
	
	for reg in region:
		xTitle['el_chIso_%s' %(reg)] = 'Charged Hadron Isolation [GeV] (%s)' %(reg)
		xTitle['el_chIso_puSub_%s' %(reg)] = 'Charged Hadron Isolation [GeV] (%s)' %(reg)
		xTitle['el_relchIso_%s' %(reg)] = 'Rel. Charged Hadron Isolation (%s)' %(reg)
		
		xTitle['el_sieie_%s' %(reg)] = '#sigma_{i#eta i#eta} (%s)' %(reg)
		xTitle['el_r9_%s' %(reg)] = 'r9 (%s)' %(reg)
		xTitle['el_r9_upto1_%s' %(reg)] = 'r9 (%s)' %(reg)
		xTitle['el_ecalIso_%s' %(reg)] = 'ECAL Isolation [GeV] (%s)' %(reg)
		xTitle['el_5x5_sieie_%s' %(reg)] = '#sigma_{i#eta i#eta} (5x5) (%s)' %(reg)
		xTitle['el_neuIso_%s' %(reg)] = 'Neutral Hadron Isolation [GeV] (%s)' %(reg)
		xTitle['el_phoIso_%s' %(reg)] = 'Photon Isolation [GeV] (%s)' %(reg)
		
		xTitle['el_neuIso_puSub_%s' %(reg)] = 'Neutral Hadron Isolation [GeV] (%s)' %(reg)
		xTitle['el_phoIso_puSub_%s' %(reg)] = 'Photon Isolation [GeV] (%s)' %(reg)
		xTitle['el_relneuIso_%s' %(reg)] = 'Rel. Neutral Hadron Isolation (%s)' %(reg)
		xTitle['el_relphoIso_%s' %(reg)] = 'Rel. Photon Isolation (%s)' %(reg)
		
		xTitle['el_dEtaIn_%s' %(reg)] = '#Delta#eta_{in} (%s)' %(reg)
		xTitle['el_dPhiIn_%s' %(reg)] = '#Delta#phi_{in} (%s)' %(reg)
		xTitle['el_et_%s' %(reg)] = 'Probe E_{T} [GeV] (%s)' %(reg)
		xTitle['pair_mass_%s' %(reg)] = 'M_{ee} [GeV] (%s)' %(reg)
		xTitle['mass_sc_%s' %(reg)] = 'M_{ee} {SC energy} [GeV] (%s)' %(reg)
		xTitle['el_eoverp_wES_%s' %(reg)] = 'el_eoverp_wES (%s)' %(reg)
		
		xTitle['el_hoe_%s' %(reg)] = 'H/E (%s)' %(reg)
		#xTitle['el_hoe_SCgt55_%s' %(reg)] = 'H/E (%s)' %(reg)
		
		xTitle['el_mHits_%s' %(reg)] = 'Missing hits (%s)' %(reg)
		xTitle['el_5x5_r9_%s' %(reg)] = 'r9 (5x5) (%s)' %(reg)
		xTitle['el_5x5_r9_upto1_%s' %(reg)] = 'r9 (5x5) (%s)' %(reg)
		xTitle['el_etaW_%s' %(reg)] = '#eta SC width (%s)' %(reg)
		xTitle['el_phiW_%s' %(reg)] = '#phi SC width (%s)' %(reg)
		xTitle['el_fbrem_%s' %(reg)] = 'fBrem (%s)' %(reg)
		xTitle['el_sc_esE_%s' %(reg)] = 'Preshower Energy [GeV] (%s)' %(reg)
		
		xTitle['el_sc_esETorawSC_%s' %(reg)] = 'Preshower Energy/raw SC (%s)' %(reg)
		
		xTitle['el_sc_e_%s' %(reg)] = 'SC Energy [GeV] (%s)' %(reg)
		xTitle['el_sc_rawE_%s' %(reg)] = 'SC Raw Energy [GeV] (%s)' %(reg)
		xTitle['el_chisq_%s' %(reg)] = '#chi^{2} (%s)' %(reg)
		xTitle['el_dxy_%s' %(reg)] = 'dxy [mm] (%s)' %(reg)
		xTitle['el_dz_%s' %(reg)] = 'dz [mm] (%s)' %(reg)
		xTitle['el_nonTrigMVA80X_%s' %(reg)] = 'Non-triggering MVA (80X) (%s)' %(reg)
		xTitle['el_sc_phi_%s' %(reg)] = 'Probe #phi_{sc} (%s)' %(reg)
		xTitle['tag_sc_phi_%s' %(reg)] = 'Tag #phi_{sc} (%s)' %(reg)
		
		xTitle['el_relchIso_puSub_%s' %(reg)] = 'Rel. Charged Hadron Isolation [GeV] (%s)' %(reg)
		xTitle['el_relphoIso_puSub_%s' %(reg)] = 'Rel. Photon Isolation [GeV] (%s)' %(reg)
		xTitle['el_relneuIso_puSub_%s' %(reg)] = 'Rel. Neutral Hadron Isolation [GeV] (%s)' %(reg)
		xTitle['el_relphoIso_puSub_ForTotEv_%s' %(reg)] = 'Rel. Photon Isolation [GeV] (%s)' %(reg)
	
	
	xTitle['pair_mass_EB_EB'] = 'M_{ee} [GeV] (EB-EB)'
	xTitle['pair_mass_EB_EE'] = 'M_{ee} [GeV] (EB-EE)'
	xTitle['pair_mass_EE_EE'] = 'M_{ee} [GeV] (EE-EE)'
	
	xTitle['el_sc_eta'] = 'Probe #eta_{sc}'
	xTitle['el_sc_phi'] = 'Probe #phi_{sc}'
	xTitle['el_eta'] = '#eta'
	xTitle['el_phi'] = '#phi'
	xTitle['tag_sc_phi'] = 'Tag #phi_{sc}'
	xTitle['event_nPV'] = '#vertices'
	xTitle['event_nPV_wei'] = '#vertices'
	xTitle['event_rho'] = '#rho'
	
	pass




######end of the function  
