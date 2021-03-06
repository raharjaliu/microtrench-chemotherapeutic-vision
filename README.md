Author: Pandu Raharja

This README is written in markdown format. Use markdown file reader of your choice to optimally read this file offline. I recommend using e.g. Atom with markdown previewer capability (as of version 1.20+: Packages > Markdown Previewer > Toggle Preview).

# I. Introduction

This repository contains the code for the publication:

*A single-cell micro trench platform for automatic monitoring of
cell division and apoptosis after chemotherapeutic drug administration*

by

E.I. Chatzopoulou, P. Raharja-Liu, A. Murschhauser, F. Sekhavati, F. Buggenthin, A. M. Vollmar, C. Marr and J.O. Rädler

# II requirements

- Python 3.5/3.6 with requirements in **Section VII** installed
- Fiji with TrackMate plugin

# III. File structure

There are two types of data set: the synchronized and the unsynchronized data set. For both data set there are numbered positions from 1 to 63 (note that not all positions are used).

 The characters after **#** describes the purpose of a directory and should be ignored. For each position, replace **PP** with two digit position id.

## III.1 Unsynchronized experiment data

For the unsynchronized dataset, the file is structured this way:

```
/PATH-TO-UNSYNCHRONIZED/
- eli-new-unsync-bf-PP/ # data for position PP
- - in-focus/ # in-focus bright field time-lapse data
- - - before/ # time-lapse data before treatment
- - - - bf_in-focusxyPPc1c1.tif # time-lapse file (raw file)
- - - - bf_in-focusxyPPc1c1-mask.tif # trench mask file
- - - after/ # time-lapse data after treatment
- - - - bf_in-focusxyPPc1.tif # time-lapse file (raw file)
- - out-focus/ # out-of-focus bright field time-lapse data
- - - before/
- - - - bfxyPPc1.tif # time-lapse file (raw file)
- - - - out/stacks/ # contains output of time-lapse preprocessing (see Section IV)
- - - after/
- - - - bfxyPPc1.tif # time-lapse file (raw file)
- - - - out/stacks/ # contains output of time-lapse preprocessing (see Section IV)
- - - merged/ # contains concatenated before and after time-lapses
- - - - merged.tif # concatenated time-lapse file (see Section IV)
- - - - out/tracked/ # output of cell recognition and tracking (see Section VI)
```

Depending on the treatment, further structure has to look like following for Vincristine:

```
- - caspase/ # caspase channel time-lapse data
- - - caspasexyPPc1.tif # caspase channel time-lapse data (raw file)
- - - caspasexyPPc1_sub.tif # the position-specific average-substracted caspase channel video (see Section IV)
- - pi/ # PI channel time-lapse data
- - - before/
- - - - pi_in-focusxyPPc1.tif  # caspase channel time-lapse data (raw file)
- - - after/
- - - - pi_in-focusxyPPc1.tif  # caspase channel time-lapse data (raw file)
- - - merged/
- - - - merged.tif # concatenated time-lapse file (see Section IV)
- - - - merged_sub.tif # the position-specific average-substracted caspase channel video (see Section IV)
- - - - merged_sub_adjust.tif # the position-specific average-substracted + brightness and contrast adjusted caspase channel video (see Section IV)
- - - - out_sub_adjust/ # output of cell recognition and tracking (see Section VI)
```

or Daunorubicin:

```
- - caspase/ # caspase channel time-lapse data
- - - caspasexyPPc1.tif # caspase channel time-lapse data (raw file)
- - - caspasexyPPc1_sub.tif # the position-specific average-substracted caspase channel video (see Section IV)
- - - out_sub_adjust/ # output of cell recognition and tracking (see Section VI)
- - pi/ # PI channel time-lapse data
- - - before/
- - - - pi_in-focusxyPPc1.tif  # caspase channel time-lapse data (raw file)
- - - after/
- - - - pi_in-focusxyPPc1.tif  # caspase channel time-lapse data (raw file)
- - - merged/
- - - - merged.tif # concatenated time-lapse file (see Section IV)
- - - - merged_sub.tif # the position-specific average-substracted caspase channel video (see Section IV)
- - - - merged_sub_adjust.tif # the position-specific average-substracted + brightness and contrast adjusted caspase channel video
```

Before starting with analysis, every subdirectories (every row in file structure ending with `/`) and files marked as **(raw file)** have to exist and be placed properly.

## III.2 Synchronized experiment data

For the synchronized dataset, the file is structured this way:

```
/PATH-TO-SYNCHRONIZED/
- eli-new-sync-bf-PP/
- - in-focus/
- - - seq0000xyPPc1.tif # time-lapse file (raw file)
- - - seq0000xyPPc1-mask.tif # trench mask
- - out-focus/
- - - seq0003xyPPc1.tif # time-lapse file (raw file)
- - - out/
- - - - stacks/ # output of time-lapse preprocessing (see Section IV)
- - - - - out-focus_corrected.tif # output of cell recognition and tracking (see Section VI)
- - - - tracks/ # output of cell recognition and tracking (see Section VI)
```

Depending on the treatment, further structure has to look like following for Vincristine:

```
- - caspase/
- - - seq0001xyPPc1.tif # caspase channel time-lapse data (raw file)
- - - seq0001xyPPc1_sub.tif # the position-specific average-substracted caspase channel video
- - pi/
- - - seq0002xy01c1.tif # caspase channel time-lapse data (raw file)
- - - sub.tif # the position-specific average-substracted caspase channel video
- - - sub_adjust.tif # the position-specific average-substracted + brightness and contrast-adjusted caspase channel video
- - - out_sub_adjust/ # output of cell recognition and tracking (see Section VI)
```

or Daunorubicin:

```
- - caspase/
- - - seq0001xyPPc1.tif # caspase channel time-lapse data (raw file)
- - - seq0001xyPPc1_sub.tif # the position-specific average-substracted caspase channel video
- - - out_sub_adjust/ # output of cell recognition and tracking (see Section VI)
- - pi/
- - - seq0002xy01c1.tif # caspase channel time-lapse data (raw file)
- - - sub.tif # the position-specific average-substracted caspase channel video
- - - sub_adjust.tif # the position-specific average-substracted + brightness and contrast-adjusted caspase channel video
```


Before starting with analysis, every subdirectories (every row in file structure ending with `/`) and files marked as **(raw file)** have to exist and be placed properly.

# IV. `fij.py`

The Jython pre-processing script `fij.py`is used to pre-process the image. This will produce:
* pre-processed out-of-focus time-lapse (unsynchronized: `out-focus/merged/merged.tif`, synchronized: `out-focus/out/stacks/out-focus_corrected.tif`)
* pre-processed PI time-lapse (unsynchronized: `pi/merged/merged-sub.tif`, synchronized: `pi/sub.tif`)
* pre-processed Caspase time-lapse (unsynchronized: `caspase/caspasexyPPc1_sub.tif`, synchronized: `caspase/seq0001xyPPc1_sub.tif`)

## IV.1 Program parameters

Program parameters are enclosed with `## PROGRAM PARAMETERS START ##` and `## PROGRAM PARAMETERS END ##`:

* `POSITIONS`: list of positions to pre-process (e.g. `[1, 2, 3]`).
* `unsynchronized`: `True` for unsynhronized mode, `False` for synchronized.
* `target_dir_pattern_unsynchronized`: patterns for location of files. E.g. if the path to unsynchronized is `D:/path/to/unsynchronized/`, write `D:\\path\\to\\unsynchronized\\eli-new-unsync-bf-%s` (for MacOS and Linux, write the path as is with the end pattern `eli-new-unsync-bf-%s` kept).
* `target_dir_pattern_synchronized`: similar as above.

## IV.2 Running `fij.py`

In Fiji, go to `File > Open`, select `fij.py` and run.

# V. Trenches mask

For each position, a mask can be created by adjusting contrast and brightness (in Fiji, `Image > Adjust > Brightness/Contrast`). The TIF image `sample-mask.tif` shows an example of good mask.

# VI. Cells recognition and tracking

This is done with TrackMate. To do that, in Fiji, load a time-lapse and `Plugins > Tracking > TrackMate`.

Following tracks are needed:
* Pre-processed out-of-focus time-lapse, based on `out-focus/merged/merged.tif`(unsynchronized) or `out-focus/out/stacks`(synchronized)

And, depending on treatment, EITHER:
* Pre-processed PI time-lapse (Vincristine), based on `pi/sub_adjust.tif` (unsynchronized) or `pi/merged/merged_sub.tif` (synchronized),

OR
* Pre-processed Caspase time-lapse (Daunorubicin), based on `caspase/caspasexyPPc1_sub.tif` (unsynchronized) or `caspase/seq0001xyPPc1_sub.tif` (synchronized).

## VI.1 Tracking parameters

Following tracking parameters are needed:

### VI.1.1 Out-of-focus cell detection and tracking

* Pixel width: 0.647 inch
* Pixel height: 0.647 inch
* Voxel depth: 1 inch
* Time interval: 1800 seconds
* Cell detection:
 - Method: downsample LoG
 - Estimated blob diameter: 15 inches
 - Threshold: 0.0
 - Downsampling factor: 2
 - Initial threshold: set to cells number < 100k
 - Later threshold set optimally
* Cell tracking:
 - Method: LAP Tracker
 - Frame to frame linking: 15 pixels
 - Track segment gap closing: 20 pixels + 4 frames
 - Track segment splitting: 25 pixels
 - No track segment merging

Gathere information stored in `out-focus/merged/out/tracked/` or `out-focus/out/tracked/` (synchronized):
* All spots statistics
* Branch analysis
* Links to tracks statistics
* Spots in tracks statistics
* Track statistics

### VI.1.1 PI or caspase cell detection and tracking

* Pixel width: 0.647 inch
* Pixel height: 0.647 inch
* Voxel depth: 1 inch
* Time interval: 1800 seconds
* Cell detection:
 - Method: downsample LoG
 - Estimated blob diameter: 30 inches
 - Threshold: 0.0
 - Downsampling factor: 2
 - Initial threshold: set to cells number < 500k
 - Later threshold set optimally
* Cell tracking:
 - Method: LAP Tracker
 - Frame to frame linking: 30 pixels
 - Track segment gap closing: 35 pixels + 2 frames
 - No track segment splitting
 - No track segment merging

Tracking information to be saved are the same as out-of-focus time-lapse.

For unsynchronized experiment, save in `pi/merged/out_sub_adjust/` (Vincrisitine) or `caspase/out_sub_adjust/`. For unsynchronized experiment, save in `pi/merged/out_sub_adjust/` (Vincrisitine) or `caspase/out_sub_adjust/`.

# VII. Data fusion

The jupyter notebooks `global_analysis-syn.ipynb` and `global_analysis-unsyn.ipynb` provide the suites for data fusion and exploration. The only parameter user needs to adjust is `PATH_TO_DATA` within the notebook. Following python libraries (besides the jupyter notebook requirements) are needed:

`sklearn`
`scipy`
`numpy`
`cv2`
`xmltodict`
`pandas`
`tiffcapture`
`tifffile`
`matplotlib`
