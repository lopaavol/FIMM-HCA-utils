import argparse
import glob
import os.path
import platform
import subprocess
from multiprocessing import Pool
import imageio
import scipy.stats
import numpy as np
from OPUtils import OPUtils

class Deconvolution:
    def __init__(self):
        self.inputpat = ""
        self.outputdir = ""
        self.psf = None
        self.fnpostfix = '_deconv'
        self.utils = OPUtils()

    def deconvolve(self, files):
        pool = Pool(processes=self.utils.dec_processes)
        selfs = [self for i in range(len(files))]
        outfiles = pool.map(process, zip(selfs, files))
        return outfiles

    def subtractBG(self, files):
        for f in files:
            img = imageio.volread(f)
            mode = scipy.stats.mode(img, axis=None)
            img = img.astype(np.float32)
            img = img - mode.mode
            img[img < 0] = 0
            img = img.astype(np.uint16)
            imageio.volwrite(f, img)

    def run(self, inputpat, outputdir, psf, subtract=True):
        self.inputpat = inputpat
        self.outputdir = outputdir
        self.psf = psf
        files = glob.glob(inputpat)
        outfiles = self.deconvolve(files)
        if subtract:
            self.subtractBG(outfiles)

def process(self, f):
    shellBool = True
    if platform.system() == 'Linux':
        shellBool = False

    cmd_stack = [self.utils.java, self.utils.java_params, '-jar', self.utils.deconvolutionlab, 'Run', '-algorithm', self.utils.dec_algorithm, self.utils.dec_params, '-path', self.outputdir, '-monitor', 'no', '-verbose', 'mute', '-stats', 'no', '-psf', 'file', self.psf]
    basefn = os.path.basename(f)
    outfile = basefn[:basefn.rfind('.')]+self.fnpostfix
    cmd_stack += ['-image', 'file', f]
    cmd_stack += ['-out', 'stack', outfile, 'intact', 'short', 'noshow']
    subprocess.call(cmd_stack, shell=shellBool)
    return os.path.join(self.outputdir,outfile+".tif")

def parseArgs():
    parser = argparse.ArgumentParser(description="Deconvolve Opera Phenix imaged 3D confocal stacks. Run separately for each channel. Uses DeconvolutionLab2 (http://bigwww.epfl.ch/deconvolution/deconvolutionlab2/) library.")
    parser.add_argument('inputpat', help="input file pattern e.g. \"*.tif\" or \"*A01*\"")
    parser.add_argument('outputdir', help="output directory")
    parser.add_argument('psf', help="PSF image file path")
    parser.add_argument('-s', '--subtract', default=True, action='store_true', help="subtract background signal from deconvolved stacks")

    args = parser.parse_args()
    return args

def main():
    args = parseArgs()
    dec = Deconvolution()
    dec.run(args.inputpat, args.outputdir, args.psf, args.subtract)

if __name__ == "__main__":
    main()
