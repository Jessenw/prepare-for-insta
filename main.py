from PIL import Image
from enum import Enum

WHITE = (255, 255, 255)
PADDING = 160

class Orientation(Enum):
    LANDSCAPE = 1
    PORTRAIT = 2

def main():
    print("Processing images...")

    src = Image.open('res/god_cares.jpg')
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

    out_img.show()

if __name__ == '__main__':
    main()