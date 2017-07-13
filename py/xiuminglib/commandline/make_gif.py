"""
Command Line Tool -- Make Annotated GIF from Image-Text Pairs

Xiuming Zhang, MIT CSAIL
July 2017
"""

from argparse import ArgumentParser
from os import makedirs
from os.path import exists, join, abspath, dirname, basename
import logging
from shutil import copyfile, rmtree
from subprocess import call
import cv2

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)

# Parameters
GIF_DELAY = 400
GIF_LOOP = 1
BOTTOM_LEFT_CORNER = (100, 150)
FONT_SCALE = 4
FONT_BGR = (0, 0, 255)
FONT_THICK = 5

# Parse variables
parser = ArgumentParser(description="Make annotated GIF from image-text pairs")
parser.add_argument('input', metavar='i', type=str, nargs='+',
                    help="input image-text pairs, e.g., im.png,'foo bar' or im.png")
parser.add_argument('outpath', metavar='o', type=str, help="output GIF")
args = parser.parse_args()
pairs = args.input
outpath = abspath(args.outpath)

# Make directory
outdir = dirname(outpath)
if not exists(outdir):
    makedirs(outdir)

# Put text on images and write to a tmp folder
tmpdir = join(outdir, 'tmp-make_gif')
if not exists(tmpdir):
    makedirs(tmpdir)
for impath_text in pairs:
    impath_text = impath_text.split(',')
    impath = impath_text[0]
    tmppath = join(tmpdir, basename(impath))
    if len(impath_text) == 1 or impath_text[1] == '':
        # No text -- just copy
        copyfile(impath, tmppath)
    else:
        text = impath_text[1]
        im = cv2.imread(impath, cv2.IMREAD_UNCHANGED)
        cv2.putText(im, text, BOTTOM_LEFT_CORNER, cv2.FONT_HERSHEY_SIMPLEX,
                    FONT_SCALE, FONT_BGR, FONT_THICK)
        cv2.imwrite(tmppath, im)

# Make GIF
call(['convert', '-delay', str(GIF_DELAY), '-loop', str(GIF_LOOP),
      join(tmpdir, '*'), outpath])

# Clean up
rmtree(tmpdir)

logging.info("%s: Generated %s", thisfile, outpath)
