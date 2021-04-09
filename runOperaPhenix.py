import FindFocalPlane
import ConvertToStack
import MIP
import Deconvolution
import os.path

def main():
    folder = '/path_to_data/'

    # Convert to stacks
    inputpat = os.path.join(folder,'output/r*')
    outputdir = os.path.join(folder,'stacks')
    cts = ConvertToStack.ConvertToStack()
    cts.run(inputpat, outputdir, merge=False)

    # Deconvolution
    outputdir = os.path.join(folder,'deconvolution')
    chpat = [('ch2','PSF63x-ch2'), ('ch3','PSF63x-ch3')]
    for cp in chpat:
        inputpat = os.path.join(folder,'stacks/*%s*'%cp[0])
        psf = "/path_to_psf/PSF_63x/%s.tif"%cp[1]
        dec = Deconvolution.Deconvolution()
        dec.run(inputpat, outputdir, psf, subtract=True)

    # MIP
    inputpat = os.path.join(folder,'Images/*.tiff')
    outputdir = os.path.join(folder,'MIP')
    mip = MIP.MIP()
    mip.run(inputpat, outputdir, stacks=False)

if __name__ == "__main__":
    main()
