import argparse
import cv2

# Parse variables
parser = argparse.ArgumentParser(description='Extracts frames from a video file.')
parser.add_argument('videoPath', metavar='v', type=str, help='video file')
parser.add_argument('outDir', metavar='o', type=str, help='output directory')
parser.add_argument('--every', metavar='N', type=int, default=1, help='sample one frame every N frame(s) (default: 1)')
parser.add_argument('--outLength', metavar='L', type=int, default=4, help='length of output filenames (default: 4)')
args = parser.parse_args()
