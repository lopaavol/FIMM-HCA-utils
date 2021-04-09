import argparse
import glob
import os
import numpy as np
import pandas as pd
import imageio
from multiprocessing import Pool
from OPUtils import OPUtils
pd.options.mode.chained_assignment = None

class MIP:
    def __init__(self):
        self.inputpat = ""
        self.outputdir = ""
        self.df = None
        self.fnpostfix = ''
        self.utils = OPUtils()

    def readImages(self, df):
        imgs = []
        for i,row in df.iterrows():
            imgs.append(imageio.imread(row['path']))
        return imgs

    def mip(self, df, outpat):
        rcfc = df[['row','col','field','channel']]
        rcfc.drop_duplicates(inplace=True)

        cmds = []
        for i,row in rcfc.iterrows():
            sdf = df[(df['row'] == row['row']) & (df['col'] == row['col']) & (df['field'] == row['field']) & (df['channel'] == row['channel'])]
            outfile = os.path.join(self.outputdir,outpat%(row['row'],row['col'],row['field'],row['channel']))
            cmds.append((self, sdf, outfile))
        pool = Pool(processes=self.utils.par_processes)
        pool.starmap(procsingle, cmds)

    def mipstacks(self, files):
        pool = Pool(processes=self.utils.par_processes)
        outfiles = [os.path.join(self.outputdir, os.path.basename(f)[:os.path.basename(f).rfind('.')]+self.fnpostfix+'.tif') for f in files]
        pool.starmap(procstack, zip(files, outfiles))

    def run(self, inputpat, outputdir, stacks=True):
        self.inputpat = inputpat
        self.outputdir = outputdir
        self.stacks = stacks
        files = glob.glob(self.inputpat)
        if stacks:
            self.mipstacks(files)
        else:
            self.df = self.utils.createFileDataFrame(files)
            self.mip(self.df, self.utils.mippat)


def procstack(f, outfile):
    img = imageio.volread(f)
    mip = img.max(axis=0)
    imageio.imwrite(outfile, mip)

def procsingle(self, sdf, outfile):
    images = self.readImages(sdf)
    imgstack = np.dstack(images)
    mip = imgstack.max(axis=2)
    imageio.imwrite(outfile, mip)

def parseArgs():
    parser = argparse.ArgumentParser(description="Create MIP from Opera Phenix confocal stack.")
    parser.add_argument('inputpat', help="input file pattern e.g. \"*.tif\" or \"*A01*\"")
    parser.add_argument('outputdir', help="output directory")
    parser.add_argument('-s', '--stacks', default=True, action='store_true', help='Take 3D stacks as input')
    args = parser.parse_args()
    return args

def main():
    args = parseArgs()
    mip = MIP()
    mip.run(args.inputpat, args.outputdir, args.stacks)

if __name__ == "__main__":
    main()
