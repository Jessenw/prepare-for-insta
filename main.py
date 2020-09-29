import argparse
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from PIL import Image

WHITE = (255, 255, 255)

'''
Directories
'''
src_dir = "/Users/jesse/Desktop/src_images/"
dst_dir = "/Users/jesse/Documents/"

padding = 0

class Orientation(Enum):
    LANDSCAPE = 1
    PORTRAIT = 2

def main():
    print("Processing images...")
    for _, _, files in os.walk(src_dir):
        for filename in files:
            process_image(filename)
            # delete_src(src_dir + filename)

def process_image(filename):
    src = Image.open(src_dir + filename)
    src_size = src.size

    # Determine whether the image is portrait/landscape
    orientation = Orientation.LANDSCAPE
    max_dimmension = src_size[0]
    if src_size[0] < src_size[1]:
        orientation = Orientation.PORTRAIT
        max_dimmension = src_size[1]

    out_width = max_dimmension
    out_height = max_dimmension
    if orientation == Orientation.LANDSCAPE:
        out_width = out_width + padding
    else:
        out_height = out_height + padding
    out_size = (out_width, out_height)

    out_img = Image.new("RGB", out_size, WHITE)

    mid_x = int((out_size[0] - src_size[0]) / 2)
    mid_y = int((out_size[1] - src_size[1]) / 2)
    out_img.paste(src, (mid_x, mid_y))

    save(src, out_img, filename)

def save(src, out, filename):
    date = datetime.today().strftime('%Y-%m-%d')

    dir_raw = dst_dir + date + "/raw/"
    dir_processed = dst_dir + date + "/processed/"

    Path(dir_raw).mkdir(parents=True, exist_ok=True)
    Path(dir_processed).mkdir(parents=True, exist_ok=True)

    # write file
    src.save(dir_raw + filename)
    out.save(dir_processed + filename)

def delete_src(filename):
    os.remove(filename)

    # Delete folder if empty
    if not os.listdir(src_dir):
        os.rmdir(src_dir)

if __name__ == '__main__':
    # Setup arguments labels
    parser = argparse.ArgumentParser()
    parser.add_argument('src', help="The source directory of images to be processed")
    parser.add_argument('dst', help="The destination directory for images to be saved")
    parser.add_argument('padding', help="Adds padding beyond the frame of 1:1 frame of the image. Default is no padding")
    args = parser.parse_args()

    src_dir = args.src.split("=")[1]
    dst_dir = args.dst.split("=")[1]
    padding = int(args.padding.split("=")[1])

    # Append '/' to directory paths if they dont exist
    if not src_dir[-1] == '/':
        src_dir = src_dir + '/'
    if not dst_dir[-1] == '/':
        dst_dir = dst_dir + '/'

    # Check if there are images available to process
    if not os.listdir(src_dir):
        print("Aborting... The provided source folder is empty")
        exit()

    main()