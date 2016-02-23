##########################################################################################################################################################
##########################################################################################################################################################
### MAIN SWITCHES

ONLYEssentialInfo =False   ## write minimal amount of info on the output file
ReduceInfo        =True    ## write minimal amount of info on the output file
DoMSV             =False   ## include variables for MSV tagger
doSMT             =False   ## include variables for SMT tagger
doRetag           =True   ## perform retagging
doComputeReference=False
JetCollections = [
  ##"AntiKt10LCTopoJets"
  'AntiKt4EMTopoJets',
  'AntiKt4PV0TrackJets',
  'AntiKt3PV0TrackJets',
  'AntiKt2PV0TrackJets',
  #'AntiKt4LCTopoJets',
  ]

#### automatic AF2 switch
#### reading from outside the ReduceInfo

### 0= SLIM, 1=FULL
ContentMode=  vars().get('CONTENT',-1)
if ContentMode!=-1:
  if ContentMode==0: ReduceInfo=True
  if ContentMode==1: ReduceInfo=False
  if ContentMode==2: ONLYEssentialInfo=True

#########################################################################################################################################################
#########################################################################################################################################################
### Define input xAOD and output ntuple file name
import glob
from AthenaCommon.AthenaCommonFlags import jobproperties as jp
#jp.AthenaCommonFlags.EvtMax.set_Value_and_Lock( vars().get('EVTMAX', -1) )
jp.AthenaCommonFlags.EvtMax.set_Value_and_Lock(10)

jp.AthenaCommonFlags.FilesInput = [
  "/afs/cern.ch/work/m/malanfer/public/training/AOD.root"
  ##"/afs/cern.ch/user/v/vdao/mc15_8TeV.110401.PowhegPythia_P2012_ttbar_nonallhad.recon.AOD.e3099_s2578_r7135_tid06628604_00/AOD.06628604._000221.pool.root.1",
  ##"/afs/cern.ch/user/v/vdao/valid1.110401.PowhegPythia_P2012_ttbar_nonallhad.recon.AOD.e3099_s2578_r7058_tid06432679_00/AOD.06432679._000066.pool.root.1",
  ##"/afs/cern.ch/work/v/vdao//xAODs/dataNtuple/Peter/mc15_13TeV.410000.PowhegPythiaEvtGen_P2012_ttbar_hdamp172p5_nonallhad.merge.AOD.e3698_a766_a767_r6264_tid05443510_00/AOD.05443510._000453.pool.root.1",
  ##"/afs/cern.ch/work/v/vdao//xAODs/dataNtuple/Peter/mc15_13TeV.410004.PowhegHerwigppEvtGen_UEEE5_ttbar_hdamp172p5_nonallhad.merge.AOD.e3836_a766_a767_r6264_tid05457978_00/AOD.05457978._000222.pool.root.1",
  ##"/afs/cern.ch/work/v/vdao//xAODs/dataNtuple/Peter/mc15_13TeV.410006.PowhegPythia8EvtGen_A14_ttbar_hdamp172p5_nonallhad.merge.AOD.e3836_a766_a767_r6264_tid05457982_00/AOD.05457982._000217.pool.root.1",
  ##"/afs/cern.ch/work/v/vdao//xAODs/dataNtuple/Peter/mc15_13TeV.410022.Sherpa_CT10_ttbar_SingleLeptonP_MEPS_NLO.merge.AOD.e3959_a766_a780_r6264_tid05960719_00/AOD.05960719._000038.pool.root.1"
  ]

##svcMgr.EventSelector.InputCollections = jp.AthenaCommonFlags.FilesInput()
from PyUtils import AthFile
af = AthFile.fopen( jp.AthenaCommonFlags.FilesInput()[0] )
##svcMgr.EventSelector.InputCollections[0] )

### AF2 or FS
isAF2=False
if af.fileinfos.has_key("evt_type"):
  eventTypeList = af.fileinfos["evt_type"]
  if eventTypeList.__contains__("IS_SIMULATION") :
    simType = af.fileinfos['metadata']['/Simulation/Parameters']['SimulationFlavour']
    if simType  == 'default' :
      print "VALERIO SAYS: THIS IS FS"
    elif simType  == 'atlfast' :
      print "VALERIO SAYS: THIS IS AF2"
      isAF2=True

evtPrintoutInterval = vars().get('EVTPRINT', 5000)
svcMgr += CfgMgr.AthenaEventLoopMgr( EventPrintoutInterval=evtPrintoutInterval )

svcMgr += CfgMgr.THistSvc()
for jet in JetCollections:
  shortJetName=jet.replace("AntiKt","Akt").replace("TopoJets","To").replace("TrackJets","Tr")
  svcMgr.THistSvc.Output += [ shortJetName+" DATAFILE='flav_"+shortJetName+".root' OPT='RECREATE'"]
#svcMgr.THistSvc.Output += ["BTAGSTREAM DATAFILE='flavntuple.root' OPT='RECREATE'"]

##########################################################################################################################################################
##########################################################################################################################################################
### you should normally not need to touch this part

doRecomputePV=False  ## do not touch unless you know what you are doing
if doSMT: doRetag=True
if doComputeReference:
  ReduceInfo   =True
  doRetag      =True
  doRecomputePV=False

##########################################################################################################################################################
##########################################################################################################################################################
### VD: put first all the RecExCommon things, then the B-tagging stuff
if doRecomputePV:
  from InDetRecExample.InDetJobProperties import InDetFlags
  InDetFlags.doVertexFinding.set_Value_and_Lock(True)
  from InDetRecExample.InDetKeys import InDetKeys
  InDetKeys.xAODVertexContainer.StoredValue='PrimaryVerticesValerio'

## from Anthony: needed to compute truth quantities of tracks
from AthenaCommon.DetFlags import DetFlags
DetFlags.BField_setOn()
DetFlags.ID_setOn()
DetFlags.Calo_setOff()
DetFlags.Muon_setOff()
if doSMT: DetFlags.Muon_setOn()

from RecExConfig.RecFlags import rec
rec.doTrigger.set_Value_and_Lock(True)
from RecExConfig.RecAlgsFlags  import recAlgs
recAlgs.doTrigger.set_Value_and_Lock(True)
from TriggerJobOpts.TriggerFlags import TriggerFlags
TriggerFlags.doTriggerConfigOnly.set_Value_and_Lock(True)

from RecExConfig.RecFlags import rec
rec.doESD.set_Value_and_Lock        (False)
rec.doWriteESD.set_Value_and_Lock   (False)
rec.doAOD.set_Value_and_Lock        (False)
rec.doWriteAOD.set_Value_and_Lock   (False)
rec.doWriteTAG.set_Value_and_Lock   (False)
rec.doDPD.set_Value_and_Lock        (False)
rec.doTruth.set_Value_and_Lock      (False)

if af.fileinfos["metadata"]["/TagInfo"]["AtlasRelease"].__contains__("AtlasDerivation"):
    rec.doApplyAODFix.set_Value_and_Lock(False)

include ("RecExCommon/RecExCommon_topOptions.py")

from AthenaCommon.AlgSequence import AlgSequence
algSeq = AlgSequence()

##########################################################################################################################################################
##########################################################################################################################################################
### GEO Business
from AthenaCommon.GlobalFlags import globalflags
print "detDescr from global flags= "+str(globalflags.DetDescrVersion)
from AtlasGeoModel.InDetGMJobProperties import GeometryFlags as geoFlags
print "geoFlags.Run()   = "+geoFlags.Run()
print "geoFlags.isIBL() = "+str(  geoFlags.isIBL() )


##########################################################################################################################################################
##########################################################################################################################################################
### VD: this is if you want to re-tag with another calibration file
from BTagging.BTaggingFlags import BTaggingFlags

#### if the new file is already in the datatbase: simple edit the name
###############BTaggingFlags.CalibrationTag = 'BTagCalibRUN12-08-10'

#### if you want to use your own calibration file use this part below
#BTaggingFlags.CalibrationFromLocalReplica = True
#BTaggingFlags.CalibrationFolderRoot = '/GLOBAL/BTagCalib/'
#BTaggingFlags.CalibrationTag = 'BTagCalibRUN2-test'

# if the calibration for DL1 is to be read in from a local JSON file
BTaggingFlags.DL1 = True
BTaggingFlags.DL1LocalNNConfig = "/afs/cern.ch/work/m/malanfer/public/training/BTagging_DL1_NNconfig.json"

include("RetagFragment.py")
if doRetag:
  from BTagging.BTaggingConfiguration import getConfiguration
  BTagConf = getConfiguration()
  ip3d =BTagConf.getTool("IP3DTag", "BTagTrackToJetAssociator","AntiKt4EMTopo")
  #ip3d.OutputLevel=DEBUG
  ####ip3d.SortingMode="SortZ0D0"
  ####ip3d.NtrkMax=8
  ####ip3d.SignWithSvx=True
  ip3dTrkSel=BTagConf.getTool("IP3DTrackSelector", "BTagTrackToJetAssociator","AntiKt4EMTopo")
  ####ip3dTrkSel.nHitPix=1
  ip3dLH=BTagConf.getTool("IP3DNewLikelihoodTool", "BTagTrackToJetAssociator","AntiKt4EMTopo")
  ip2d  =BTagConf.getTool("IP2DTag", "BTagTrackToJetAssociator","AntiKt4EMTopo")
  ###############################ip2d.SortingMode="SortPt"
  mv2c20 =BTagConf.getTool("MV2c20Tag", "BTagTrackToJetAssociator","AntiKt4EMTopo")
  ###mv2c20.OutputLevel=DEBUG

##########################################################################################################################################################
##########################################################################################################################################################
##########################################################################################################################################################
##########################################################################################################################################################
### Additional Tools needed by the dumper
from TrackVertexAssociationTool.TrackVertexAssociationToolConf import CP__TightTrackVertexAssociationTool
ToolSvc+=CP__TightTrackVertexAssociationTool("TightVertexAssocTool",dzSinTheta_cut=3, doPV=True)

from InDetTrackSelectionTool.InDetTrackSelectionToolConf import InDet__InDetTrackSelectionTool
ToolSvc+=InDet__InDetTrackSelectionTool("InDetTrackSelTool", CutLevel="Loose", maxZ0SinTheta=3)

from TrkVertexFitterUtils.TrkVertexFitterUtilsConf import Trk__TrackToVertexIPEstimator
ToolSvc+=Trk__TrackToVertexIPEstimator("trkIPEstimator")

from TrigDecisionTool.TrigDecisionToolConf import Trig__TrigDecisionTool
ToolSvc += Trig__TrigDecisionTool( "TrigDecisionTool" )
from TrigEDMConfig.TriggerEDM import EDMLibraries
ToolSvc.TrigDecisionTool.Navigation.Dlls = EDMLibraries

jvt = CfgMgr.JetVertexTaggerTool('JVT')
ToolSvc += jvt

ToolSvc += CfgMgr.CP__PileupReweightingTool("prw",
                                            OutputLevel = INFO,
                                            UsePeriodConfig= "MC15"
                                            )

##########################################################################################################################################################
##########################################################################################################################################################
##########################################################################################################################################################
##########################################################################################################################################################

### Main Ntuple Dumper Algorithm
for JetCollection in JetCollections:
  shortJetName=JetCollection.replace("AntiKt","Akt").replace("TopoJets","To").replace("TrackJets","Tr")
  alg = CfgMgr.btagIBLAnalysisAlg("BTagDumpAlg_"+JetCollection,
                                  OutputLevel=INFO,
                                  Stream=shortJetName,
                                  InDetTrackSelectionTool   =ToolSvc.InDetTrackSelTool,
                                  TrackVertexAssociationTool=ToolSvc.TightVertexAssocTool,
                                  TrackToVertexIPEstimator  =ToolSvc.trkIPEstimator,
                                  JVTtool=ToolSvc.JVT,
                                  ) #DEBUG
  alg.JetCollectionName = JetCollection
  alg.doSMT = doSMT
  if "AntiKt2PV0TrackJets" in JetCollection or "Truth" in JetCollection:
    alg.JetPtCut = 10.e3
    alg.CleanJets     = False
    alg.CalibrateJets = False
  elif "AntiKt3PV0TrackJets" in JetCollection or "AntiKt4PV0TrackJets" in JetCollection:
    alg.JetPtCut = 7.e3
    alg.CleanJets     = False
    alg.CalibrateJets = False
  else:
    alg.JetPtCut = 20.e3
  alg.doSMT     =doSMT
  alg.ReduceInfo=ReduceInfo
  alg.EssentialInfo=ONLYEssentialInfo
  alg.DoMSV     =DoMSV
  alg.Rel20     =True
  alg.JetCleaningTool.CutLevel= "LooseBad"
  alg.JetCleaningTool.DoUgly  = True
  if not doComputeReference: algSeq += alg

  ###print JetCollection
  calibfile        = "JES_Prerecommendation2015_Feb2015.config"
  collectionForTool="AntiKt4LCTopo"
  calSeg           ="JetArea_Residual_EtaJES"
  if "EM" in JetCollection:
    collectionForTool="AntiKt4EMTopo"
    calibfile  ="JES_MC15Prerecommendation_April2015.config"
    if isAF2: calibfile  ="JES_MC15Prerecommendation_AFII_June2015.config"
    calSeg     ="JetArea_Residual_Origin_EtaJES_GSC"
  print collectionForTool
  ToolSvc += CfgMgr.JetCalibrationTool("BTagDumpAlg_"+JetCollection+"_JCalib",
                                       IsData=False,
                                       ConfigFile=calibfile,
                                       CalibSequence=calSeg,
                                       JetCollection=collectionForTool)


###########################################################################################################################################################################
