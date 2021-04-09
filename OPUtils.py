import os
import re
import configparser
import pandas as pd

class OPUtils:
    def __init__(self, cfg="configuration.cfg"):
        config = self.readConfig(cfg)
        self.imgcnv = config.get("Path", "imgcnv")
        self.deconvolutionlab = config.get("Path", "deconvolutionlab")
        self.tmpdir = config.get("Path", "tempdir")
        if not os.path.exists(self.tmpdir):
            os.makedirs(self.tmpdir)
        self.java = config.get("Java", "java")
        self.java_params = config.get("Java", "params")
        self.pat = config.get("Pattern", "oppattern")
        self.mippat = config.get("Pattern", "mippattern")
        self.dec_algorithm = config.get("Deconvolution", "algorithm")
        self.dec_params = config.get("Deconvolution", "params")
        self.dec_processes = int(config.get("Deconvolution", "processes"))
        self.par_processes = int(config.get("Parallel", "processes"))

    def readConfig(self, fn):
        config = configparser.RawConfigParser()
        if os.path.exists(fn):
            config.read(fn)
        return config

    def createFileDataFrame(self, files):
        basefn = list(map(os.path.basename,files))
        regexp = re.compile(self.pat)
        matches = [map(int,regexp.match(x).groups()) for x in basefn]
        rows,cols,fields,slices,channels = zip(*matches)
        df = pd.DataFrame({'path': files, 'filename': basefn, 'row': rows, 'col': cols, 'field': fields, 'slice': slices, 'channel': channels})
        try:
            df.sort_values('filename',inplace=True)
        except:
            df.sort('filename',inplace=True)
        return df
