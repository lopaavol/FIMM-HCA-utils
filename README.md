# OPutils
Python utils to process imaging data collected with Opera Phenix at FIMM High Content Imaging and Analysis (FIMM-HCA) unit.

## Modules
ConvertToStack.py, Deconvolution.py, FindFocalPlane.py and MIP.py are the processing modules which can be executed either from the command line (check the arguments from the source code) or used in object-oriented fashion as is done in the main pipeline script runOperaPhenix.py.
- ConvertToStack.py: Creates multi-channel 3D OME-TIFF stacks from 2D images using imgcnv.
- Deconvolution.py: Runs deconvolution of 3D stacks using [DeconvolutionLab2](http://bigwww.epfl.ch/deconvolution/deconvolutionlab2/) library.
- FindFocalPlane.py: Finds and extracts the most sharp focal plane from 3D stack.
- MIP.py: Creates maximum intensity projections of each 3D stack.
- OPUtils.py: Support class used in various processing classes.
- configuration.cfg: Includes necessary parameters for different processing steps, paths to libraries and file path patterns.
- runOperaPhenix.py: Main script to run image preprocessing pipeline. The script is executed without arguments.

## Requirements
The package requires Python3.5 or newer, and some basic libraries such as numpy, scipy, pandas and imageio. Deconvolution requires [DeconvolutionLab2](http://bigwww.epfl.ch/deconvolution/deconvolutionlab2/) library and converting 2D images to 3D multi-channel stack requires imgcnv.
