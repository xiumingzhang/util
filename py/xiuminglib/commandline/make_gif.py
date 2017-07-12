"""
Command Line Tool -- Make Annotated GIF from Image-Text Pairs

Xiuming Zhang, MIT CSAIL
July 2017
"""

from argparse import ArgumentParser
from os import makedirs
from os.path import exists, join, abspath, dirname
import logging
from cv2 import imwrite

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)

# Parse variables
parser = ArgumentParser(description="Make annotated GIF from image-text pairs")
parser.add_argument('input', metavar='i', type=str,
                    help="input image-text pairs, e.g., im.png,'foo bar'")
parser.add_argument('outpath', metavar='o', type=str, help="output GIF")
args = parser.parse_args()
outpath = abspath(args.outpath)

for impath_text in args.input:
    print(impath_text)

# Make directory
outdir = dirname(outpath)
if not exists(outdir):
    makedirs(outdir)

logging.info("%s: ", thisfile)
