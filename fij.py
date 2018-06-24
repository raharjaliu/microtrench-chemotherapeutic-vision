# Java imports
from java.lang import System
from java.io import File

#Imagej imports
from ij import IJ, ImagePlus, ImageStack, WindowManager

#pr: Z project
from ij.plugin import ZProjector

#pr: concatenator
from ij.plugin import Concatenator

import ij.io.OpenDialog as OpenDialog
import ij.plugin.ContrastEnhancer as ContrastEnhancer
import ij.plugin.Duplicator as Duplicator
import ij.plugin.ImageCalculator as ImageCalculator
import ij.gui.GenericDialog as Dialog

#Fiji imports
import fiji.plugin.trackmate.Settings as Settings
import fiji.plugin.trackmate.Model as Model
import fiji.plugin.trackmate.SelectionModel as SelectionModel
import fiji.plugin.trackmate.TrackMate as TrackMate
import fiji.plugin.trackmate.Logger as Logger
import fiji.plugin.trackmate.detection.DetectorKeys as DetectorKeys
import fiji.plugin.trackmate.detection.LogDetectorFactory as LogDetectorFactory
import fiji.plugin.trackmate.tracking.sparselap.SparseLAPTrackerFactory as SparseLAPTrackerFactory
import fiji.plugin.trackmate.tracking.LAPUtils as LAPUtils
import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
import fiji.plugin.trackmate.features.FeatureAnalyzer as FeatureAnalyzer
import fiji.plugin.trackmate.features.spot.SpotContrastAndSNRAnalyzerFactory as SpotContrastAndSNRAnalyzerFactory
import fiji.plugin.trackmate.action.ExportStatsToIJAction as ExportStatsToIJAction
import fiji.plugin.trackmate.io.TmXmlReader as TmXmlReader
import fiji.plugin.trackmate.action.ExportTracksToXML as ExportTracksToXML
import fiji.plugin.trackmate.io.TmXmlWriter as TmXmlWriter
import fiji.plugin.trackmate.features.ModelFeatureUpdater as ModelFeatureUpdater

import fiji.plugin.trackmate.features.SpotFeatureCalculator as SpotFeatureCalculator
import fiji.plugin.trackmate.features.spot.SpotContrastAndSNRAnalyzer as SpotContrastAndSNRAnalyzer
import fiji.plugin.trackmate.features.spot.SpotIntensityAnalyzerFactory as SpotIntensityAnalyzerFactory
import fiji.plugin.trackmate.features.spot.SpotMorphologyAnalyzerFactory as SpotMorphologyAnalyzerFactory
import fiji.plugin.trackmate.features.spot.SpotRadiusEstimatorFactory as SpotRadiusEstimatorFactory

import fiji.plugin.trackmate.features.edges.EdgeTargetAnalyzer as EdgeTargetAnalyzer
import fiji.plugin.trackmate.features.edges.EdgeTimeLocationAnalyzer as EdgeTimeLocationAnalyzer
import fiji.plugin.trackmate.features.edges.EdgeVelocityAnalyzer as EdgeVelocityAnalyzer

import fiji.plugin.trackmate.features.track.TrackSpeedStatisticsAnalyzer as TrackSpeedStatisticsAnalyzer
import fiji.plugin.trackmate.features.track.TrackDurationAnalyzer as TrackDurationAnalyzer
import fiji.plugin.trackmate.features.track.TrackIndexAnalyzer as TrackIndexAnalyzer
import fiji.plugin.trackmate.features.track.TrackBranchingAnalyzer as TrackBranchingAnalyzer
import fiji.plugin.trackmate.features.track.TrackLocationAnalyzer as TrackLocationAnalyzer
import fiji.plugin.trackmate.features.track.TrackSpotQualityFeatureAnalyzer as TrackSpotQualityFeatureAnalyzer

import fiji.plugin.trackmate.util.TMUtils as TMUtils

import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
import fiji.plugin.trackmate.io.TmXmlWriter as TmXmlWriter


import fiji.plugin.trackmate.visualization.PerTrackFeatureColorGenerator as PerTrackFeatureColorGenerator

#Python imports
import sys
import os

separator = '\\'

def listFiles(fdir):
	flist = os.listdir(fdir)
	print(flist)
	for ffile in flist:
		# if file is a folder, step into it
		IJ.log("undecided: " + ffile);
		if (os.path.isdir(fdir + ffile) and not ("Pos" in ffile)) :
			IJ.log("Folder: "+ ffile)
			listFiles(fdir + ffile + separator)

			#pr
			return None
			
		# else if file is a tif, open it and try to process it
		#elif ffile.endswith(".tif") or ffile.endswith(".nd2"):
		elif  (os.path.isdir(fdir + ffile) and ("Pos" in ffile)):
			IJ.log("File: "+ fdir + separator+ ffile)
			filepath = fdir + separator + ffile;
			filepath = filepath.replace(separator,separator + separator);

			# pr
			return startTracking(filepath,fdir,ffile)
		else:
			return None


def startTracking(filepath,fdir,ffile, filename):	
	outpath = fdir
	troutpath = fdir + separator + ffile + separator + "tracked" + separator
	stackoutpath = fdir + separator + ffile + separator + "stacks" + separator

	pixwidth = 0.647
	interval_sec = 600 #pr
	if "141006" in fdir:
		interval_sec = 600
	elif "141117" in fdir:
		interval_sec = 300
	elif "141215" in fdir:
		interval_sec = 300	
	
	if not os.path.isdir(outpath):
		os.mkdir(outpath)
	if not os.path.isdir(troutpath):
		os.mkdir(troutpath)
	if not os.path.isdir(stackoutpath):
		os.mkdir(stackoutpath)

	print 'filepath: ', filepath #pr
	print 'fdir: ', fdir #pr
	print 'ffile: ', ffile #pr
	IJ.run("Image Sequence...", "open=" + filepath + " file=" + filename + " sort"); #pr
	#IJ.run("Image Sequence...", "open=" + filepath + " file=molm sort"); #pr
	imp = WindowManager.getCurrentImage();
	imptitle = imp.getTitle();
	nframes = imp.getNSlices();
	IJ.run(imp, "Properties...", "channels=1 slices=1 frames="+ str(nframes) +" unit=inch pixel_width="+ str(pixwidth) +" pixel_height="+ str(pixwidth) +" voxel_depth=1.0000 frame=["+ str(interval_sec) +" sec]");
	
	IJ.run(imp,"Duplicate...","title="+imptitle+"_dup duplicate")
	imp_dup = WindowManager.getImage(imptitle+"_dup")
	IJ.run(imp_dup, "Gaussian Blur...", "sigma=50 stack");
	
	ic = ImageCalculator();
	imp_corr = ic.run("Divide create 32-bit stack", imp, imp_dup);
	imp_corr.setTitle(imptitle+"_corrected")
	imp_corr.show()
	imp.changes = False
	imp.close();
	imp_dup.changes = False
	imp_dup.close();
	
	IJ.run(imp_corr, "8-bit", "");
	IJ.run(imp_corr, "Normalize Local Contrast", "block_radius_x=100 block_radius_y=100 standard_deviations=1 stretch stack");
	IJ.saveAs(imp_corr, "Tiff", stackoutpath+separator+imptitle+"_corrected.tif");
	
	IJ.run(imp_corr,"Duplicate...","title="+imptitle+"_bg duplicate")
	imp_bg = WindowManager.getImage(imptitle+"_bg")
	
	#Prefs.blackBackground = True;
	IJ.setAutoThreshold(imp_bg, "MinError dark");
	IJ.run(imp_bg, "Convert to Mask", "stack");
	IJ.run(imp_bg, "Analyze Particles...", "size=10000-Infinity show=Masks stack");
	imp_bg.changes = False
	imp_bg.close();

	imp_bgmask = WindowManager.getImage("Mask of " + imptitle + "_bg")
	
	ic = ImageCalculator();
	imp_corr_wobg = ic.run("Subtract create stack", imp_corr, imp_bgmask);
	imp_corr_wobg.setTitle(imptitle+"_corrected_womask")
	imp_corr_wobg.show()

	IJ.saveAs(imp_corr_wobg, "Tiff", stackoutpath+separator+imptitle+"_corrected_womask.tif"); #pr

	# pr: substract average frames
	zp = ZProjector(imp_corr_wobg)
	zp.setMethod(ZProjector.AVG_METHOD)
	zp.doProjection()
	zpimp = zp.getProjection()
	zpimp.show()
	imp_corr_wobg_sub = ImageCalculator().run("Subtract create stack", imp_corr_wobg, zpimp)
	imp_corr_wobg_sub.show()
	#imp_corr_wobg.changes = False
	#imp_corr_wobg.close()
	# pr: subtract average frames (END)
	
	IJ.saveAs(imp_corr_wobg_sub, "Tiff", stackoutpath+separator+imptitle+"_corrected_womask_substracted.tif"); #pr
	IJ.saveAs(zpimp, "Tiff", stackoutpath+separator+imptitle+"_corrected_womask_avg.tif"); #commented out: pr
	#IJ.saveAs(imp_corr_wobg, "Tiff", stackoutpath+separator+imptitle+"_corrected_womask.tif");
	IJ.saveAs(imp_bgmask, "Tiff", stackoutpath+separator+imptitle+"_bgmask.tif");

	print(stackoutpath+separator+imptitle+"_corrected_womask_substracted.tif")
	print(stackoutpath+separator+imptitle+"_corrected_womask_avg.tif")
	print(stackoutpath+separator+imptitle+"_bgmask.tif")

	imp_corr.changes = False
	imp_corr.close()
	imp_bgmask.changes = False
	imp_bgmask.close()

	imp_corr_wobg.changes = False
	imp_corr_wobg.close()
	#imp_corr_wobg_sub.changes = False
	#imp_corr_wobg_sub.close()
	zpimp.changes = False
	zpimp.close()

	#IJ.log(System.getProperty("os.name"))
	#IJ.log(fdir)

	return imp_corr_wobg_sub

def preprocess(path, out='out', filename='*'):
	return startTracking(path, path, out, filename)

def concatenate_files(f1, f2, path):
	# note that concatenate closes passed windows!
	ct = Concatenator()
	merged = ct.run(f1, f2)
	IJ.saveAs(merged, "Tiff", path);

def process_caspase_signal(path_signal, path_imp, path_imp_out):

	path_imp = path_signal + path_imp
	imp = IJ.openImage(path_imp)
	imp.show()

	zp = ZProjector(imp)
	zp.setMethod(ZProjector.AVG_METHOD)
	zp.doProjection()
	zpimp = zp.getProjection()

	imp_sub = ImageCalculator().run("Subtract create stack", imp, zpimp)
	imp_sub.show()
	IJ.saveAs(imp_sub, "Tiff", path_signal + path_imp_out)

	imp.changes = False
	imp.close()
	imp_sub.changes = False
	imp_sub.close()

def process_pi_signal(path, position, unsynchronized=True):

	if unsynchronized:
		path_signal = path + "\\pi"
		path_signal_before = path_signal + "\\before"
		path_signal_after = path_signal + "\\after"
		path_signal_merged = path_signal + "\\merged"
		path_imp_before = path_signal_before + "\\pi_in-focusxy%sc1.tif" % position
		path_imp_after = path_signal_after + "\\pixy%sc1.tif" % position
		path_imp_merged = path_signal_merged + "\\merged.tif"
		path_imp_merged_sub = path_signal_merged + "\\merged_sub.tif"

		imp1 = IJ.openImage(path_imp_before)
		imp1.show()
		imp2 = IJ.openImage(path_imp_after)
		imp2.show()

		zp1 = ZProjector(imp1)
		zp1.setMethod(ZProjector.AVG_METHOD)
		zp1.doProjection()
		zpimp1 = zp1.getProjection()

		zp2 = ZProjector(imp2)
		zp2.setMethod(ZProjector.AVG_METHOD)
		zp2.doProjection()
		zpimp2 = zp2.getProjection()

		imp_sub1 = ImageCalculator().run("Subtract create stack", imp1, zpimp1)
		imp_sub1.show()

		imp_sub2 = ImageCalculator().run("Subtract create stack", imp2, zpimp2)
		imp_sub2.show()

		concatenate_files(imp1, imp2, path_imp_merged)
		concatenate_files(imp_sub1, imp_sub2, path_imp_merged_sub)

	else:
		path_signal = path + "\\pi\\seq0002xy%sc1.tif" % position
		path_sub = path + "\\pi\\sub.tif"

		imp = IJ.openImage(path_signal)
		imp.show()

		zp = ZProjector(imp)
		zp.setMethod(ZProjector.AVG_METHOD)
		zp.doProjection()
		zpimp = zp.getProjection()

		imp_sub = ImageCalculator().run("Subtract create stack", imp, zpimp)
		imp_sub.show()

		IJ.saveAs(imp_sub, "Tiff", path_sub)

		imp.changes = False
		imp.close()
		zpimp.changes = False
		zpimp.close()
		imp_sub.changes = False
		imp_sub.close()		

## PROGRAM PARAMETERS START ##

POSITIONS = [40]
unsynchronized = True
target_dir_pattern_unsynchronized = 'D:\\path\\to\\unsynchronized\\eli-new-unsync-bf-%s'
target_dir_pattern_synchronized = 'D:\\path\\to\\synchronized\\eli-new-unsync-bf-%s'

## PROGRAM PARAMETERS END ##

for POSITION in POSITIONS:

	if POSITION < 10:
		pos = "0%d" % POSITION
	else:
		pos = "%d" % POSITION
	
	print("Pre-processing position %s" % pos)

	if unsynchronized:
		target_dir = target_dir_pattern_unsynchronized % pos
	else:
		target_dir = target_dir_pattern_synchronized % pos

	# processing out-focus
	if unsynchronized:
		before = preprocess(target_dir + '\\out-focus\\before', out='out', filename='*')
		after = preprocess(target_dir + '\\out-focus\\after', out='out', filename='*')
		concatenate_files(before, after, target_dir + '\\out-focus\\merged\\merged.tif')
	else:
		preprocess(target_dir + '\\out-focus', out='out', filename='*').close()

	# processing caspase
	if unsynchronized:
		path_signal = target_dir + "\\caspase"
		path_imp ="\\caspasexy%sc1.tif" % pos
		path_imp_out = "\\caspasexy%sc1_sub.tif" % pos
	else:
		path_signal = target_dir + "\\caspase"
		path_imp ="\\seq0001xy%sc1.tif" % pos
		path_imp_out = "\\seq0001xy%sc1_sub.tif" % pos
	
	process_caspase_signal(path_signal, path_imp, path_imp_out)	

	# processing pi signal
	process_pi_signal(target_dir, pos, unsynchronized=unsynchronized)

	System.gc();