# *MPRAGE<sub>like</sub>: a novel approach to generate T1w images from Multi-Contrast Gradient Echo images for brain segmentation* 

---

## Overview

This repository contains the code required to produce MPRAGE*like* images directly from Multi-Parameter Mapping (MPM) or Variable Flip Angle (VFA) images without the need to calculate quantitative maps. 

This technique can become particularly interesting for long neuroimaging protocols with a MPM protocol and where scan time can become particularly long. The MPRAGE*like* images have shown promising results in typical neuroimaging analysis tasks like automatic brain segmentation where high similarity was observed with actual MPRAGE images [see accepted publication in Magnetic Resonance In Medicine from *Fortin 
M.-A. et al.*, 2025]. 

---

## How does it work?

Simply put, the MPRAGE*like* approach employs and combines the multi-contrast aspect of MPM/VFA protocols which include a T1w contrast image in addition of a PDw and/or MTw additionally. By calculating the ratio of such contrasts, an enhanced 'pseudo' T1w image is created which exhibits a strong 
resemblance with an acquired T1w MPRAGE image (see figure below). 

![Figure to show an example MPRAGElike image](fig-for-repo.png)

---

## Installation

1. Clone this repository.
2. Create a virtual environment (i.e., with pip or conda) and install the required packages, which are provided in the *requirements.txt* file in this repository.

   - E.g., with conda:
   ```
   conda create --name env_name python=3.9
   ```
   ```
   conda activate env_name 
   ```
   ```
   pip install -r requirements.txt
   ```
3. If everything is properly installed, you should be able to see the help function outputs by typing ```python get_mpragelike.py --help``` in the folder where the installation was made.  

---

## How to use it?

```
python get_mprage-like.py --path2img /PATH/TO/NIFTI/FOLDER --echo 1 --reg 100 --subid TEST-00 --contrast 'all' -- path2save PATH/TO/RESULTS/FOLDER 
```

where: 

- `--path2img` is the path to the folder containing the MPM/VFA images. A certain hierarchy is expected: 1) All different contrasts should be inside the same folder. 2) All contrasts should have an identifier as part of their filenames like 't1' or 'T1' for the T1w images. 3) All images should be 
  in the Nifti format (.nii or .nii.gz).
- `--echo` is an integer defining the echo number (TE) to use from the images in the folder. The script expects a "_eX" naming for multi-TE like it is used by most DICOM to NIfTI converters. If single TE data is used without a "_eX" in the filename, do not specify this flag. (default: 1)
- `--reg` is the regularization term for background noise removal of the MPRAGElike image. Can have more than one lambda value. If you only have one lambda value, you can directly type the value. If >1 lambda, please  type a list of integers (e.g., [0, 100, 200, 300]). A default value of 
  100 is set for lambda, but the most optimal lambda value can be different for different images or scalings. (default: 100)
- `--subid` is the subject identifier. Can be any combination of strings and/or numbers. 
- `--contrast` is a flag to select which MPRAGElike equation to use (i.e., contrasts to use). Set this flag to 'all' to use T1w, PDw and MTw. 'PD' to use the T1w and PDw images only. 'MT' to use the T1w and MTw images only.  Only one value can be set. (default: 'all')
- `--path2save` is the path where the MPRAGElike image created will be saved. A 'mprage-like' subfolder will be created in the specified path. (default: Current working directory (pwd))

---

## Input images requirements:

#### Convention for images

  1) Images need to be in the NIfTI format (.nii or .nii.gz). DICOM format is not supported. Any DICOM to NIfTI converter should do the trick, but the *dcm2niix* tool (https://github.com/rordenlab/dcm2niix) has been tested for this work and is widely used in the neuroimaging community. 
  2) The NIfTI files of the different contrasts/images to be used by the ```get_mprage-like.py``` script are expected to be inside the same folder. Otherwise, the script won't be able to find and identify them properly.
  3) The different contrasts should be identified/tagged with their corresponding contrast names. For instance, the T1w images should have 't1' or 'T1' as part of their filenames. The same applies to PDw and MTw (i.e., 'pd'/'PD' and 'mt'/'MT' in their filenames).
  4) If multi-echo images ought to be used, they should have a 'eX' as part of their filenames (X being an integer corresponding to the echo number). For single echo images, no need to specify the echo number as part of the filename.
  5) The images used in the related publication had a value range ranging from 0 to 4095. If that is not the case for your data, the optimal value for the regularization parameter (&lambda;) might be different from the one used in the publication, and we recommend finding a value better suited for your dataset.

#### Coregistration

- Since different images are combined to calculate the MPRAGElike image, the images should be registered together. Considering the different contrasts of MPM (or VFA) acquisitions are acquired rapidly one after the other in the 
  same session, motion between the contrasts should be quite minimal and a simple rigid registration should be more than enough to correct for differences. Coregistration of the images is **not** part of this repository. 

---

## External softwares used in the related publication:

- As part of the analysis pipeline described in the related publication, several external softwares that were **not** developed as part of this work (and that also require additional python libraries than the ones provided in the *requirements.txt* here or other downloads) were used. It's important to mention that these external softwares are **not** required to compute MPRAGE*like* images, only to reproduce the complete analysis pipeline from the publication.
  Therefore, in order to help users interested in recreating the same pipeline as the one described in the paper, we have decided to share all external softwares used with their respective functionality in the pipeline: 


1) **hMRI toolbox**:

   - **Description**: A toolbox for quantitative MRI and in vivo histology using MRI (hMRI) embedded in the Statistical Parametric Mapping (SPM: https://www.fil.ion.ucl.ac.uk/spm/) framework in MATLAB.
   - **Usage**: Coregistration of MPM images and creation of quantitative maps.
   - **hMRI version used**: v0.6.1 (https://github.com/hMRI-group/hMRI-toolbox/releases/tag/v0.3.0)

2) **N4 bias field correction**:

   - **Description**: The N4 bias field correction algorithm is a popular method for correcting low frequency intensity non-uniformity present in MRI image known as bias field. In this work, the N4 algorithm part of the ANTsPy python library was used (https://antspy.readthedocs.io/en/latest/utils.html) 
   - **Usage**: Correct MR images from receive bias inhomogeneities before segmentation.
   - **ANTsPy version used**: 0.4.2 (https://pypi.org/project/antspyx/)

3) **FastSurferVINN**:

   - **Description**: *FastSurferVINN* is a submodule of *FastSurfer* (https://github.com/Deep-MI/FastSurfer), a neuroimaging software designed for the automatic segmentation and reconstruction of the cerebral cortex and subcortical structures at native sub-millimeter resolution of brain MR images.
   - **Usage**: Automatic brain segmentation at native sub-millimeter resolution of T1w and 'pseudo' T1w images
   - **FastSurfer version used**: Docker container of version 2.3.0 (https://github.com/Deep-MI/FastSurfer/releases/tag/v2.3.0) with the `--seg_only` flag running on GPU. 

---

## Citation/Contact

This code is under Apache 2.0 licensing.
If you use it in a publication, please cite the following paper:

**This repository contains the code related to an accepted manuscript to Magnetic Resonance in Medicine to be published soon.**

If you have any question regarding the usage of this code or any suggestions to improve it, you can contact us at: marc.a.fortin@ntnu.no



