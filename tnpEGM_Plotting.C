#include <stdio.h>
#include <iostream>
#include <fstream>

using namespace std;



int colour_fill_DT = 0;
int colour_line_DT = kBlack;
int colour_marker_DT = kBlack;
int colour_fill_MC = kOrange-2;
int colour_line_MC = kOrange-2;
int colour_marker_MC = kOrange+7;


int colour_MCval = kOrange-2;
int colour_MCerr = kOrange+7;
int colour_DTval = kBlack;


float rPad1 = 0.70;
float rPad2 = 0.30;




// + Get axis name
//================
// * Get X axis name
//------------------
TString GetXaxisname (TH1D *hist)
{
	// + Get the histogram title
	//-----------------------
	TString nameXaxis = hist -> GetTitle();
	TString nameHist = hist -> GetName();
	
	printf ("         |- |-- Hist title: %s\n", nameXaxis.Data());
	
	
	// + Turn the title into axis name
	//--------------------------------
	if (nameXaxis.Contains(" (EE)"))   nameXaxis . ReplaceAll (" (EE)", "");
	if (nameXaxis.Contains(" (EB)"))   nameXaxis . ReplaceAll (" (EB)", "");
	if (nameXaxis.Contains("E_{T}") || nameXaxis.Contains("Energy"))   nameXaxis . Append (" [GeV]");
	if (nameXaxis.Contains("solation") && !(nameXaxis.Contains("Rel")) && !(nameXaxis.Contains("rel.")))   nameXaxis . Append (" [GeV]");
	if (nameXaxis.Contains("phi"))   nameXaxis . Append (" [rad]");
	if (nameXaxis.Contains("mass"))
	{
		nameXaxis . Append (" [GeV]");
		nameXaxis . ReplaceAll ("Di-lepton invariant mass", "M_{ee}");
	}
	
	if (nameHist.Contains("el_1overEminus1overP_"))   nameXaxis . ReplaceAll ("1oE - 1oP", "|1/E - 1/p| [GeV^{-1}]");;
	if (nameHist.Contains("el_dPhiIn_"))   nameXaxis . ReplaceAll ("#Delta#eta_", "#Delta#phi_");
	
	return nameXaxis;
}





// + Characterize 1D-distribution
//===============================
void Characterize_Dist1D (TH1 *hist,  int colour_fill,  int style_fill,  int colour_line,  int colour_marker,  int style_marker,  TString nameXaxis)
{
	float ratio = float(rPad1/rPad2);
	
	
	// + Determine the Y-axis title
	//-----------------------------
	TString nameYaxis_width;
	TString nameYaxis_unit;
	TString nameYaxis;
	
	// * Determine the unit
	if (nameXaxis.Contains("[rad]"))   nameYaxis_unit = "rad";
	if (nameXaxis.Contains("[GeV]"))   nameYaxis_unit = "GeV";
	
	// * Determine the width
	float widthXaxis = (hist->GetXaxis()->GetXmax() - hist->GetXaxis()->GetXmin()) / hist->GetNbinsX();
	
	if (widthXaxis >= 0.99)             nameYaxis_width = Form ("%.1f", widthXaxis);
	else if (widthXaxis >= 0.099000)    nameYaxis_width = Form ("%.2f", widthXaxis);
	else if (widthXaxis >= 0.009900)    nameYaxis_width = Form ("%.3f", widthXaxis);
	else if (widthXaxis >= 0.000990)    nameYaxis_width = Form ("%.4f", widthXaxis);
	else if (widthXaxis >= 0.000099)    nameYaxis_width = Form ("%.5f", widthXaxis);
	
	// * Combine the title components
	if ((nameYaxis_unit.Contains("rad")) || (nameYaxis_unit.Contains("GeV")))
		nameYaxis = Form ("Events / %s %s", nameYaxis_width.Data(), nameYaxis_unit.Data());
	else
		nameYaxis = Form ("Events / %s", nameYaxis_width.Data());
	
	if (nameXaxis . Contains("r9"))   hist -> GetXaxis() -> SetRangeUser (0.4, 1.2);
	
	
	hist -> SetTitle       ("");
	hist -> SetFillColor   (colour_fill);
	hist -> SetFillStyle   (style_fill);
	hist -> SetLineColor   (colour_line);
	hist -> SetLineWidth   (1);
	hist -> SetMarkerStyle (style_marker);
	hist -> SetMarkerColor (colour_marker);
	hist -> SetMarkerSize  (0.75);
	
	hist -> GetXaxis() -> SetTitle       (nameXaxis.Data());
	hist -> GetXaxis() -> SetTitleFont   (42);
	hist -> GetXaxis() -> SetTitleSize   (0.0);
	hist -> GetXaxis() -> SetTitleOffset (0.4);
	hist -> GetXaxis() -> SetLabelSize   (0.0);
	hist -> GetXaxis() -> SetLabelOffset (0.004);
	
	hist -> GetYaxis() -> SetTitle       (nameYaxis.Data());
	hist -> GetYaxis() -> SetMaxDigits   (4);
	hist -> GetYaxis() -> SetTitleFont   (42);
	hist -> GetYaxis() -> SetTitleSize   (0.055);
	hist -> GetYaxis() -> SetTitleOffset (0.480*ratio);
	hist -> GetYaxis() -> SetLabelSize   (0.045);
	hist -> GetYaxis() -> SetLabelOffset (0.003);
}





// + Characterize Ratio
//=====================
void Characterize_Rate1D (TH1 *hist,  int colour_fill,  int style_fill,  int colour_line,  int colour_marker,  int style_marker,  TString nameXaxis)
{
	float ratio = float(rPad1/rPad2);
	
	
	hist -> SetTitle       ("");
	hist -> SetFillColor   (colour_fill);
	hist -> SetFillStyle   (style_fill);
	hist -> SetLineColor   (colour_line);
	hist -> SetLineWidth   (1);
	hist -> SetMarkerStyle (style_marker);
	hist -> SetMarkerColor (colour_marker);
	hist -> SetMarkerSize  (0.75);
	
	//printf (" ---> Axis name: %s\n", nameXaxis.Data());
	hist -> GetXaxis() -> SetTitle       (nameXaxis.Data());
	hist -> GetXaxis() -> SetTitleFont   (42);
	hist -> GetXaxis() -> SetTitleSize   (0.055*ratio);
	hist -> GetXaxis() -> SetTitleOffset (0.900);
	hist -> GetXaxis() -> SetLabelSize   (0.045*ratio);
	hist -> GetXaxis() -> SetLabelOffset (0.007*ratio);
	
	hist -> GetYaxis() -> SetTitle       ("Data/MC");
	hist -> GetYaxis() -> SetTitleFont   (42);
	hist -> GetYaxis() -> SetTitleSize   (0.055*ratio);
	hist -> GetYaxis() -> SetTitleOffset (0.480);
	hist -> GetYaxis() -> SetLabelSize   (0.045*ratio);
	hist -> GetYaxis() -> SetLabelOffset (0.003*ratio);
	hist -> GetYaxis() -> SetNdivisions  (505);
	hist -> GetYaxis() -> SetRangeUser   (-0.20, 2.20);
}










// + Plots production
//===================
void CreatePlot (TH1D *histDT,   TH1D *histMC,   TH1D *histMCErr,   TH1D *histRatioDT,   TH1D *histRatioMC,   double lumi,   TString runPeriod,   TString dir_Output)
{
	for (int isLog=0; isLog<2; isLog++)
	{
		TString nameScale[2] = {"Linear", "Log"};
		
		printf ("         |- Making %s scale plots\n", nameScale[isLog].Data());
		TCanvas *canvas = new TCanvas ("canvas", "", 600, 600);
		
		// * Distribution part
		printf ("         |- |-- Drawing observable distribution ...\n");
		canvas -> cd();
		TPad *pad1 = new TPad ("pad1", "", 0.0, 0.3, 1.0, 1.0);
		pad1 -> SetLeftMargin   (0.13);
		pad1 -> SetRightMargin  (0.05);
		pad1 -> SetTopMargin    (0.08);
		pad1 -> SetBottomMargin (0.02);
		pad1 -> SetTicks        (1, 1);
		pad1 -> SetLogy         (isLog);
		pad1 -> Draw ();
		pad1 -> cd();
		
		float maxHeight = max (histDT->GetMaximum(),  histMC->GetMaximum());
		float minHeight = min (histDT->GetMinimum(1), histMC->GetMinimum(1));
		float multipleFactor;
		
		TString nameObject = histDT -> GetName();
		
		if (nameObject.Contains("phi"))
		{
			multipleFactor = (isLog) ? pow(10, 0.5*(log10(maxHeight)-log10(minHeight))) : 1.8;
		}
		else
		{
			multipleFactor = (isLog) ? pow(10, 0.5*(log10(maxHeight)-log10(minHeight))) : 1.5;
		}
		
		histDT -> SetMaximum (maxHeight*multipleFactor);
		histMC -> SetMaximum (maxHeight*multipleFactor);
		
		histMC    -> Draw ("hist");
		histMCErr -> Draw ("same e2");
		histDT    -> Draw ("ep same");
		
		TLegend *legend = new TLegend (0.62, 0.71, 0.91, 0.89);
		legend -> SetTextFont (42);
		legend -> SetTextSize (0.055);
		legend -> SetFillColorAlpha (0, 0.5);
		legend -> SetLineColorAlpha (0, 0.5);
		legend -> AddEntry (histDT, "Data", "ep");
		legend -> AddEntry (histMC, "Z #rightarrow ee (MC)", "f");
		legend -> AddEntry (histMCErr, "Norm.Unc.", "f");
		legend -> Draw ("same");
		
		TLatex *texLogo = new TLatex();
		texLogo -> SetNDC();
		texLogo -> SetTextFont (42);
		texLogo -> SetTextSize (0.07);
		texLogo -> DrawLatex (0.18, 0.82, "#bf{CMS}");
		
		float lumiByRun = 5.879;
		TLatex *texLumi = new TLatex();
		texLumi -> SetNDC();
		texLumi -> SetTextFont  (42);
		texLumi -> SetTextSize  (0.055);
		texLumi -> SetTextAlign (31);
		texLumi -> DrawLatex (0.96, 0.935, Form("%.1f fb^{-1} (13 TeV) 2016", lumi));
		
		TLatex *texRegion = new TLatex();
		texRegion -> SetNDC();
		texRegion -> SetTextFont  (42);
		texRegion -> SetTextSize  (0.055);
		texRegion -> SetTextAlign (13);
		if (nameObject.Contains("_EE") || nameObject.Contains("_EB_EE"))   texRegion -> DrawLatex (0.63, 0.70, "Endcap");
		else if (nameObject.Contains("_EB") || nameObject.Contains("_EB_EB"))   texRegion -> DrawLatex (0.63, 0.70, "Barrel");
		
		
		// * Ratio part
		printf ("         |- |-- Drawing ratio ...\n");
		canvas -> cd();
		TPad *pad2 = new TPad ("pad2", "", 0.0, 0.0, 1.0, 0.3);
		pad2 -> SetLeftMargin   (0.13);
		pad2 -> SetRightMargin  (0.05);
		pad2 -> SetTopMargin    (0.01);
		pad2 -> SetBottomMargin (0.30);
		pad2 -> SetTicks        (1, 1);
		pad2 -> SetGrid         (0, 1);
		pad2 -> Draw ();
		pad2 -> cd();
		
		histRatioMC -> Draw ("e2");
		histRatioDT -> Draw ("ep same");
		
		pad2 -> Update();
		
		
		
		// + Save canvas to file
		//----------------------
		TString nameDirOut = Form ("%s/PlotPaperstyle_%s/", dir_Output.Data(), nameScale[isLog].Data());
		TString nameFileOut  = Form ("%s_%s", runPeriod.Data(), nameObject.Data());
		
		system (Form("mkdir -p  %s", nameDirOut.Data()));
		
		canvas -> SaveAs (Form ("%s%s.pdf", nameDirOut.Data(), nameFileOut.Data()));
		canvas -> SaveAs (Form ("%s%s.png", nameDirOut.Data(), nameFileOut.Data()));
		canvas -> SaveAs (Form ("%s%s.C",   nameDirOut.Data(), nameFileOut.Data()));
		
		
		
		// + Delete the canvas to prevent memory leak
		//-------------------------------------------
		delete canvas;
		
		printf ("         |- |-- Plot saved\n");
	}
}










// + Main function
//================
void tnpEGM_Plotting (string dirGetInfo,   string dirOutput)
{
	gStyle -> SetOptStat (0);
	TH1::AddDirectory(kFALSE);
	
	
	
	// + Get the list of histograms' name and output
	//----------------------------------------------
	TString dir_GetInfo       = Form ("%s", dirGetInfo.data());
	TString name_histOutput   = Form("%s/list_pathHistRoot.txt", dirGetInfo.data());
	TString name_listVariable = Form("%s/list_Variable.txt", dirGetInfo.data());
	
	TString dir_Output = Form ("%s", dirOutput.data());
	
	vector<TString>  list_variable;
	vector<TString>  list_histOutput;
	vector<TString>  list_runDT;
	vector<TString>  list_runMC;
	vector<double>   list_lumiDT;
	vector<double>   list_lumiMC;
	list_variable   . clear();
	list_histOutput . clear();
	list_runDT      . clear();
	list_runMC      . clear();
	list_lumiDT     . clear();
	list_lumiMC     . clear();
	
	std::ifstream  file_histOutout   (name_histOutput.Data());
	std::ifstream  file_listVariable (name_listVariable.Data());
	
	string   line_fromFile;
	TString  line_convert;
	TString  line_fileName;
	TString  line_runPeriod;
	TString  line_lumi;
	TObjArray  *line_components;
	
	// * Get histograms' root file
	printf ("$ -- Getting list of root files from %s ...\n", name_histOutput.Data());
	printf ("$ ------> The output for checking is:\n");
	printf ("          |- %s\n", dir_Output.Data());
	
	while (!file_histOutout.eof())
	{
		std::getline (file_histOutout, line_fromFile);
		if (file_histOutout.eof())   break;
		
		line_convert = Form ("%s", line_fromFile.data());
		line_convert . ReplaceAll ("\n", "");
		
		line_components = line_convert . Tokenize (": ");
		line_runPeriod = ((TObjString*)line_components->At(0)) -> String();
		line_lumi      = ((TObjString*)line_components->At(1)) -> String();
		line_fileName  = ((TObjString*)line_components->At(2)) -> String();
		
		if (!line_fileName . Contains(dir_Output.Data()))   continue;
		
		if (line_convert . Contains ("DT"))
		{
			list_runDT . push_back(line_runPeriod);
			list_lumiDT . push_back (line_lumi.Atof());
		}
		else if (line_convert . Contains ("MC"))
		{
			list_runMC . push_back(line_runPeriod);
			list_lumiMC . push_back (line_lumi.Atof());
		}
		
		list_histOutput . push_back (line_fileName);
		printf ("          |- |-- %s\n", line_fileName.Data());
	}
	
	printf ("$ -----> List of root files obtained\n\n");
	
	
	// * Get histograms' name
	printf ("$ -- Getting list of variables from %s ...\n", name_listVariable.Data());
	
	while (!file_listVariable.eof())
	{
		std::getline (file_listVariable, line_fromFile);
		if (file_listVariable.eof())   break;
		
		line_convert = Form ("%s", line_fromFile.data());
		line_convert . ReplaceAll ("\n", "");
		line_convert . ReplaceAll ("nameVariable:", "");
		line_convert . ReplaceAll (" ", "");
		
		list_variable . push_back (line_convert);
	}
	
	printf ("$ -----> List of variables obtained\n\n");
	
	
	
	
	// + Go through the list of variables
	//-----------------------------------
	unsigned int nVars = list_variable . size();
	
	printf ("$ -- Sub-task 1: Collecting histograms and making plots ...\n");
	
	for (unsigned int ivar=0; ivar<nVars; ivar++)
	{
		// + Create vectors of histograms
		//-------------------------------
		vector<TH1D*>  vec_histOutDT;
		vector<TH1D*>  vec_histOutMC;
		vector<TH1D*>  vec_histOutMCErr;
		vector<TH1D*>  vec_histRatioDT;
		vector<TH1D*>  vec_histRatioMC;
		vec_histOutDT    . clear();
		vec_histOutMC    . clear();
		vec_histOutMCErr . clear();
		vec_histRatioDT  . clear();
		vec_histRatioMC  . clear();
		
		
		
		// + Vectors containing integral for scaling
		//------------------------------------------
		vector<double>  vec_intDT;
		vector<double>  vec_intMC;
		vec_intDT . clear();
		vec_intMC . clear();
		
		
		
		
		// + Go through the files, read the desired histogram
		//---------------------------------------------------
		unsigned int nFiles = list_histOutput . size();
		
		printf ("$ -----> Collecting the histograms of [ %s ] from %d output ...\n", list_variable[ivar].Data(), nFiles);
		
		for (unsigned int ifile=0; ifile<nFiles; ifile++)
		{
			TFile *file_input = new TFile (list_histOutput[ifile].Data(), "read");
			TH1D *hist_fromFile = (TH1D*)file_input -> Get (list_variable[ivar].Data());
			
			double integral = (hist_fromFile) ? hist_fromFile->Integral() : 0;
			
			TString nameXaxis = GetXaxisname (hist_fromFile);
			
			printf ("         |- Opening file %s\n", list_histOutput[ifile].Data());
			
			
			if (list_histOutput[ifile] . Contains("DT"))
			{
				printf ("         |- |-- DT histogram integral: %f\n", integral);
				Characterize_Dist1D (hist_fromFile, int(kBlack),    1001, int(kBlack),    int(kBlack),    20, nameXaxis);
				vec_histOutDT . push_back (hist_fromFile);
				
				vec_intDT . push_back (integral);
			}
			else if (list_histOutput[ifile] . Contains("MC"))
			{
				printf ("         |- |-- MC histogram integral: %f\n", integral);
				TH1D *hist_clone = (TH1D*)hist_fromFile -> Clone();
				
				Characterize_Dist1D (hist_fromFile, int(kOrange-4), 1001, int(kOrange-4), int(kOrange-4), 1,  nameXaxis);
				Characterize_Dist1D (hist_clone,    int(kOrange+7), 3144, int(kOrange+7), int(kOrange+7), 1,  nameXaxis);
				
				vec_histOutMC    . push_back (hist_fromFile);
				vec_histOutMCErr . push_back (hist_clone);
				
				vec_intMC . push_back (integral);
			}
		}
		
		printf ("         |- Histograms collected\n");
		
		
		
		// + Scale the MC histograms
		//--------------------------
		unsigned int nRunsDT = list_runDT . size();
		unsigned int nRunsMC = list_runMC . size();
		//double tmp1 = vec_intDT[0];
		//double tmp2 = vec_intMC[0];
		unsigned int tmp1 = vec_intDT.size();
		unsigned int tmp2 = vec_intMC.size();
		
		printf ("         |- |-- there are %d DT-run and %d MC-run\n", nRunsDT, nRunsMC);
		printf ("         |- |-- there are %d DT-integral and %d MC-integral\n", tmp1, tmp2);
		
		int countProblem = 0;
		
		for (unsigned int i=0; i<nRunsDT; i++)
		{
			for (unsigned int j=0; j<nRunsMC; j++)
			{
				if (list_runDT[i] . Contains(list_runMC[j].Data()))
				{
					if (vec_intDT[i]!=0 && vec_intMC[j]!=0)
					{
						double scale = vec_intDT[i] / vec_intMC[j];
						vec_histOutMC[j]    -> Scale (scale);
						vec_histOutMCErr[j] -> Scale (scale);
					}
					else
					{
						countProblem ++;
					}
					break;
				}
			}
		}
		
		
		
		
		// + Check error, if error-free, combine histograms
		//-------------------------------------------------
		if (countProblem>0 || nRunsDT!=nRunsMC)
		{
			printf ("$ -----> !!! Error, there are %d problem\n\n", countProblem);
			continue;
		}
		else if (nRunsDT > 1)
		{
			printf ("$ -----> Combining histograms ... \n");
			
			// * For data
			TH1D    *hist_combineDT = (TH1D*)vec_histOutDT[0] -> Clone();
			TString runCombinedDT = "combined";
			double  lumiDT = 0.0;
			
			for (unsigned int i=1; i<vec_histOutDT.size(); i++)
			{
				hist_combineDT -> Add (vec_histOutDT[i]);
				lumiDT += list_lumiDT[i];
			}
			
			vec_histOutDT . push_back (hist_combineDT);
			list_runDT    . push_back (runCombinedDT);
			list_lumiDT   . push_back (lumiDT);
			
			// * For MC
			TH1D *hist_combineMC    = (TH1D*)vec_histOutMC[0]    -> Clone();
			TH1D *hist_combineMCErr = (TH1D*)vec_histOutMCErr[0] -> Clone();
			TString runCombinedMC = "combined";
			double  lumiMC = 0.0;
			
			for (unsigned int i=1; i<vec_histOutMC.size(); i++)
			{
				hist_combineMC    -> Add (vec_histOutMC[i]);
				hist_combineMCErr -> Add (vec_histOutMCErr[i]);
				lumiMC += list_lumiMC[i];
			}
			
			vec_histOutMC    . push_back (hist_combineMC);
			vec_histOutMCErr . push_back (hist_combineMCErr);
			list_runMC       . push_back (runCombinedMC);
			list_lumiMC      . push_back (lumiMC);
			
			printf ("         |- Histograms combined\n");
		}
		
		nRunsDT = list_runDT . size();
		nRunsMC = list_runMC . size();
		
		
		
		
		
		
		// + Create the histograms for ratio
		//----------------------------------
		printf ("$ -----> Creating ratio histograms ... \n");
		
		for (unsigned int i=0; i<nRunsDT; i++)
		{
			for (unsigned int j=0; j<nRunsMC; j++)
			{
				if (list_runDT[i] . Contains(list_runMC[j].Data()))
				{
					// * Data/MC ratio
					TH1D *histRatioDT = (TH1D*)vec_histOutDT[i] -> Clone();
					histRatioDT -> Divide (vec_histOutMC[j]);
					
					// * MC error bar
					TH1D *histRatioMC = (TH1D*)vec_histOutMC[j] -> Clone();
					
					for (int i=0; i<histRatioMC->GetNbinsX(); i++)
					{
						float binError = (vec_histOutMC[j]->GetBinContent(i+1) != 0) ? vec_histOutMC[j]->GetBinError(i+1) / vec_histOutMC[j]->GetBinContent(i+1) : 0.0;
						histRatioMC -> SetBinError   (i+1, binError);
						histRatioMC -> SetBinContent (i+1, 1);
					}
					
					TString nameXaxis = GetXaxisname (histRatioDT);
					
					// * Charaterize histograms
					Characterize_Rate1D (histRatioDT, int(kBlack),    1001, int(kBlack),    int(kBlack),    20, nameXaxis);
					Characterize_Rate1D (histRatioMC, int(kOrange+7), 3144, int(kOrange+7), int(kOrange+7), 1,  nameXaxis);
					
					vec_histRatioDT . push_back (histRatioDT);
					vec_histRatioMC . push_back (histRatioMC);
					
					break;
				}
			}
		}
		
		printf ("         |- Ratio histograms created\n");
		
		
		
		
		
		// + Draw the histograms
		//----------------------
		unsigned int nRatioDT = vec_histRatioDT . size();
		unsigned int nRatioMC = vec_histRatioMC . size();
		
		if (nRatioDT!=vec_histOutDT.size() || nRatioMC!=vec_histOutMC.size())
		{
			printf ("         |- !!! ERROR: There are more ratio than actual histograms\n");
			break;
		}
		else
		{
			printf ("$ -----> Start making plots ...\n");
		}
		
		
		for (unsigned int i=0; i<nRunsDT; i++)
		{
			for (unsigned int j=0; j<nRunsMC; j++)
			{
				if (list_runDT[i] . Contains(list_runMC[j].Data()))
				{
					CreatePlot (vec_histOutDT[i], vec_histOutMC[j], vec_histOutMCErr[j], vec_histRatioDT[i], vec_histRatioMC[i], list_lumiDT[i], list_runDT[i], dir_Output);
				}
			}
		}
		
		
		
		// + Remove the last components in the vector of runs
		//---------------------------------------------------
		printf ("$ -----> Remove the combined run from the runPeriod-vectors\n\n");
		if (nRunsDT > 1)
		{
			list_runDT . pop_back();
		}
		
		if (nRunsMC > 1)
		{
			list_runMC . pop_back();
		}
		
		printf ("\n");
	}
}
