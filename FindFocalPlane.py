import argparse
import glob
import shutil
import numpy as np
import pandas as pd
from skimage import io
from OPUtils import OPUtils
pd.options.mode.chained_assignment = None

def sumFunc(img):
    return np.sum(img, axis=(0,1))

class FindFocalPlane:
    def __init__(self):
        self.inputpat = ""
        self.outputdir = ""
        self.channel = 1
        self.df = None
        self.utils = OPUtils()

    def copyBestPlane(self, df):
        outdf = df[df['best'] == True]
        for i,row in outdf.iterrows():
            try:
                shutil.copy(row['path'],self.outputdir)
            except:
                print("Could not copy file",row['path'])

    def readImages(self, df):
        imgs = []
        for i,row in df.iterrows():
            imgs.append(io.imread(row['path']))
        return imgs

    def findBestPlane(self, df):
        rcfc = df[['row','col','field']]
        rcfc.drop_duplicates(inplace=True)

        for i,row in rcfc.iterrows():
            sdf = df[(df['row'] == row['row']) & (df['col'] == row['col']) & (df['field'] == row['field']) & (df['channel'] == self.channel)]
            images = self.readImages(sdf)
            bp = list(map(sumFunc,images))
            maxind = bp.index(max(bp))
            df.loc[(df['row'] == row['row']) & (df['col'] == row['col']) & (df['field'] == row['field']) & (df['slice'] == sdf.iloc[maxind]['slice']),'best'] = True
            df.at[sdf.iloc[maxind].name,'best'] = True

        return df

    def run(self, inputpat, outputdir, channel = 1):
        self.inputpat = inputpat
        self.outputdir = outputdir
        self.channel = channel
        files = glob.glob(self.inputpat)
        self.df = self.utils.createFileDataFrame(files)
        self.df['best'] = pd.Series([False for x in range(len(self.df['path']))], index=self.df.index)
        self.df = self.findBestPlane(self.df)
        self.copyBestPlane(self.df)


def parseArgs():
    parser = argparse.ArgumentParser(description="Select the best focal plane from Opera Phenix confocal stack.")
    parser.add_argument('inputpat', help="input file pattern e.g. \"*.tif\" or \"*A01*\"")
    parser.add_argument('outputdir', help="output directory")
    parser.add_argument('-channel', type=int, default=1, help="channel used to find the best focal plane (default: 1)")
    args = parser.parse_args()
    return args

def main():
    args = parseArgs()
    ffp = FindFocalPlane()
    ffp.run(args.inputpat, args.outputdir, args.channel)

if __name__ == "__main__":
    main()
