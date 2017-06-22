import argparse
from os import makedirs
from os.path import exists, join, abspath
import logging
from shutil import rmtree
from cv2 import imwrite, VideoCapture


logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)

# Parse variables
parser = argparse.ArgumentParser(description="Extract frames from a video file")
parser.add_argument('videopath', metavar='v', type=str, help="video file")
parser.add_argument('outdir', metavar='o', type=str, help="output directory")
parser.add_argument('--every', metavar='n', type=int, default=1, help="sample one frame every n frame(s) (default: 1)")
parser.add_argument('--outlen', metavar='l', type=int, default=4, help="length of output filenames (default: 4)")
args = parser.parse_args()
videopath = args.videopath
outdir = abspath(args.outdir)
every = args.every
outlen = args.outlen

# Make directory
if exists(outdir):
    rmtree(outdir)
makedirs(outdir)

# Read frames from video
vid = VideoCapture(videopath)
frameidx = 0
frameidx_out = 1
while vid.isOpened():
    success, im = vid.read()
    if not success:
        break
    if frameidx % every == 0:
        outpath = join(outdir, str(frameidx_out).zfill(outlen) + '.png')
        logging.info("%s: Frame %d saved as %s", thisfile, frameidx, outpath)
        imwrite('%s' % outpath, im)
        frameidx_out += 1
    frameidx += 1
vid.release()
