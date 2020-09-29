from datetime import datetime
from enum import Enum
import os
from pathlib import Path
from PIL import Image

WHITE = (255, 255, 255)
PADDING = 500

'''
Directories
'''
SRC_FOLDER = "/Users/jesse/Desktop/src_images/"
OUT_FOLDER = ""
OUT_FOLDER_DEFAULT = "/Users/jesse/Documents/"

class Orientation(Enum):
    LANDSCAPE = 1
    PORTRAIT = 2

def main():
    for _, _, files in os.walk(SRC_FOLDER):
        for filename in files:
            process_image(filename)
            delete_src(SRC_FOLDER + filename)

def process_image(filename):
    print("Processing images...")

    src = Image.open(SRC_FOLDER + filename)
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
        out_width = out_width + PADDING
    else:
        out_height = out_height + PADDING
    out_size = (out_width, out_height)

    out_img = Image.new("RGB", out_size, WHITE)

    mid_x = int((out_size[0] - src_size[0]) / 2)
    mid_y = int((out_size[1] - src_size[1]) / 2)
    out_img.paste(src, (mid_x, mid_y))

    save(src, out_img, filename)


def save(src, out, filename):
    date = datetime.today().strftime('%Y-%m-%d')

    dir_raw = OUT_FOLDER_DEFAULT + date + "/raw/"
    dir_processed = OUT_FOLDER_DEFAULT + date + "/processed/"

    Path(dir_raw).mkdir(parents=True, exist_ok=True)
    Path(dir_processed).mkdir(parents=True, exist_ok=True)

    # write file
    src.save(dir_raw + filename)
    out.save(dir_processed + filename)

def delete_src(filename):
    os.remove(filename)

    # Delete folder if empty
    if not os.listdir(SRC_FOLDER):
        os.rmdir(SRC_FOLDER)


if __name__ == '__main__':
    main()