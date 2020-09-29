from datetime import datetime
from enum import Enum
from pathlib import Path
from PIL import Image
import tkinter as tk

import os

class Application(tk.Frame):
    WHITE = (255, 255, 255)
    PADDING = 60

    '''
    Directories
    '''
    SRC_FOLDER = "/Users/jesse/Desktop/fuckitywuckity/"
    OUT_FOLDER = ""
    OUT_FOLDER_DEFAULT = "/Users/jesse/Documents/"

    class Orientation(Enum):
        LANDSCAPE = 1
        PORTRAIT = 2

    def process_start(self):
        print("Processing images...")
        for _, _, files in os.walk(self.SRC_FOLDER):
            for filename in files:
                self.process_image(filename)
                self.delete_src(self.SRC_FOLDER + filename)
        print("Done")

    def process_image(self, filename):
        src = Image.open(self.SRC_FOLDER + filename)
        src_size = src.size

        # Determine whether the image is portrait/landscape
        orientation = self.Orientation.LANDSCAPE
        max_dimmension = src_size[0]
        if src_size[0] < src_size[1]:
            orientation = self.Orientation.PORTRAIT
            max_dimmension = src_size[1]

        out_width = max_dimmension
        out_height = max_dimmension
        if orientation == self.Orientation.LANDSCAPE:
            out_width = out_width + self.PADDING
        else:
            out_height = out_height + self.PADDING
        out_size = (out_width, out_height)

        out_img = Image.new("RGB", out_size, self.WHITE)

        mid_x = int((out_size[0] - src_size[0]) / 2)
        mid_y = int((out_size[1] - src_size[1]) / 2)
        out_img.paste(src, (mid_x, mid_y))

        self.save(src, out_img, filename)

    def save(self, src, out, filename):
        date = datetime.today().strftime('%Y-%m-%d')

        dir_raw = self.OUT_FOLDER_DEFAULT + date + "/raw/"
        dir_processed = self.OUT_FOLDER_DEFAULT + date + "/processed/"

        Path(dir_raw).mkdir(parents=True, exist_ok=True)
        Path(dir_processed).mkdir(parents=True, exist_ok=True)

        # write file
        src.save(dir_raw + filename)
        out.save(dir_processed + filename) 

    def delete_src(self, filename):
        os.remove(filename)

        # Delete folder if empty
        if not os.listdir(self.SRC_FOLDER):
            os.rmdir(self.SRC_FOLDER)

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.start = tk.Button(self)
        self.start["text"] = "Start"
        self.start["command"] = self.process_start
        self.start.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red", command=self.master.destroy)
        self.quit.pack(side="bottom")

root = tk.Tk()
app = Application(master=root)
app.mainloop()