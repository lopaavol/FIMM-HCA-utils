import argparse
import glob
import os.path
import platform
import subprocess
import shutil
import pandas as pd
from multiprocessing import Pool
from OPUtils import OPUtils
pd.options.mode.chained_assignment = None

outpat = "r%02dc%02df%d.ome.tif"
outpatch = "r%02dc%02df%d-ch%d.ome.tif"
tmppat = "r%02dc%02df%dp%02d.ome.tif"

class ConvertToStack:
    def __init__(self):
        self.inputpat = ""
        self.outputdir = ""
        self.df = None
        self.utils = OPUtils()

    def createStack(self, df, merge=True):
        rcf = df[['row','col','field']]
        rcf.drop_duplicates(inplace=True)
        slices = df[['slice']]
        slices.drop_duplicates(inplace=True)
        channels = df[['channel']]
        channels.drop_duplicates(inplace=True)

        cmds_stack = []
        for i,row in rcf.iterrows():
            if merge:
                outfile = os.path.join(self.outputdir,outpat%(row['row'],row['col'],row['field']))
                cmd_stack = [self.utils.imgcnv, '-o', outfile, '-t', 'ome-tiff', '-geometry', str(len(slices))+',1']
                cmds_merge = []
                for j,sl in slices.iterrows():
                    tmpfile = os.path.join(self.utils.tmpdir,tmppat%(row['row'],row['col'],row['field'],sl['slice']))
                    cmd_channels = [self.utils.imgcnv, '-o', tmpfile, '-t', 'ome-tiff']
                    rcfs = df[(df['row'] == row['row']) & (df['col'] == row['col']) & (df['field'] == row['field']) & (df['slice'] == sl['slice'])]
                    if len(rcfs > 0):
                        cmd_channels.extend(['-i', rcfs.iloc[0]['path']])
                    for k,ch in rcfs.iterrows():
                        if ch.name == rcfs.iloc[0].name: continue
                        cmd_channels.extend(['-c', ch['path']])
                    cmds_merge.append(cmd_channels)
                    cmd_stack.extend(['-i', tmpfile])
                pool = Pool(processes=self.utils.par_processes)
                pool.map(process, cmds_merge)
                cmds_stack.append(cmd_stack)
            else:
                for j,ch in channels.iterrows():
                    outfile = os.path.join(self.outputdir,outpatch%(row['row'],row['col'],row['field'],ch['channel']))
                    cmd_stack = [self.utils.imgcnv, '-o', outfile, '-t', 'ome-tiff', '-geometry', str(len(slices))+',1']
                    for j,sl in slices.iterrows():
                        rcfcs = df[(df['row'] == row['row']) & (df['col'] == row['col']) & (df['field'] == row['field']) & (df['slice'] == sl['slice']) & (df['channel'] == ch['channel'])]
                        cmd_stack.extend(['-i', rcfcs.iloc[0]['path']])
                    cmds_stack.append(cmd_stack)

        pool = Pool(processes=self.utils.par_processes)
        pool.map(process, cmds_stack)

    def run(self, inputpat, outputdir, merge=True):
        self.inputpat = inputpat
        self.outputdir = outputdir
        files = glob.glob(inputpat)
        self.df = self.utils.createFileDataFrame(files)
        self.createStack(self.df, merge)

def process(cmd):
    shellBool = True
    if platform.system() == 'Linux':
        shellBool = False
    subprocess.call(cmd, shell=shellBool)

def parseArgs():
    parser = argparse.ArgumentParser(description="Convert Opera Phenix images to OME-TIFF multi-channel stack.")
    parser.add_argument('inputpat', help="input file pattern e.g. \"*.tif\" or \"*A01*\"")
    parser.add_argument('outputdir', help="output directory")
    parser.add_argument('-m', '--merge', default=True, action='store_true', help="merge channels into same stack")

    args = parser.parse_args()
    return args

def main():
    args = parseArgs()
    cts = ConvertToStack()
    cts.run(args.inputpat, args.outputdir, args.merge)

if __name__ == "__main__":
    main()
