"""
Command Line Tool -- Make Annotated GIF from Image-Text Pairs

Xiuming Zhang, MIT CSAIL
July 2017
"""

from argparse import ArgumentParser
from os import makedirs
from os.path import exists, join, abspath, dirname, basename
import logging
from shutil import copyfile
import cv2 import imread, imwrite

logging.basicConfig(level=logging.INFO)
thisfile = abspath(__file__)

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
    if len(impath_text) == 2 or impath_text[1] == '':
        # No text -- just copy
        copyfile(impath, join(tmpdir, basename(impath)))
    else:
        text = impath_text[1]
        im = cv2.imread(outpath_final, cv2.IMREAD_UNCHANGED)
        cv2.putText(im, text['contents'], text['bottom_left_corner'],
                    cv2.FONT_HERSHEY_SIMPLEX, text['font_scale'], text['bgr'], text['thickness'])
        cv2.imwrite(outpath_final, im)
    im_text.append([im, text])

# Make GIF


logging.info("%s: ", thisfile)
