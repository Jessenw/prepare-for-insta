import argparse
import io
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from PIL import Image
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

import tkinter as tk
from tkinter import filedialog
from tkinter import Frame

root = tk.Tk()

# UI State
src_label_var = tk.StringVar()
dst_label_var = tk.StringVar()
padding_label_var = tk.StringVar()
upload_drive_var = tk.IntVar()

# Directories
src_dir = ''
dst_dir = ''

parent_drive_dir = 'Instagram'
padding = 60

def process_images():
    src_dir = src_label_var.get()
    dst_dir = dst_label_var.get()

    print("running...")
    print("src: " + src_dir)
    print("dst: " + dst_dir)

    for root, _, files in os.walk(src_dir):
        for filename in files:
            process_image(root, filename)
            # delete_src(src_dir + filename)

def process_image(dir, filename):
    print('Processing: ' + filename)

    # Load source image
    src_path = os.path.join(dir, filename)
    src_img = Image.open(src_path)
    src_size = src_img.size

    # Determine the greatest dimmension to use for the 
    # background size + padding
    max_dimmension = src_size[0] + padding
    if src_size[0] < src_size[1]:
        max_dimmension = src_size[1] + padding

    # Create background
    out_size = (max_dimmension + padding, max_dimmension + padding)
    out_img = Image.new("RGB", out_size, (255, 255, 255))

    # Center source image on background
    mid_x = int((out_size[0] - src_size[0]) / 2)
    mid_y = int((out_size[1] - src_size[1]) / 2)
    out_img.paste(src_img, (mid_x, mid_y))

    save(src_img, out_img, filename)

def save(src_img, out_img, filename):
    date = datetime.today().strftime('%Y-%m-%d')

    dir_raw = os.path.join(dst_dir + date, 'raw')
    dir_processed = os.path.join(dst_dir + date, 'processed')

    Path(dir_raw).mkdir(parents=True, exist_ok=True)
    Path(dir_processed).mkdir(parents=True, exist_ok=True)

    # Write file
    src_img.save(os.path.join(dir_raw, filename))
    out_img.save(os.path.join(dir_processed, filename))

def delete_src(filename):
    os.remove(filename)

    # Delete folder if empty
    if not os.listdir(src_dir):
        os.rmdir(src_dir)

def save_to_drive():
    date = datetime.today().strftime('%Y-%m-%d')
    dir_processed = os.path.join(dst_dir + date, 'processed')

    try:
        # Log into Google Drive account
        g_login = GoogleAuth()
        drive = GoogleDrive(g_login)

        file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()

        # If root folder doesn't exist, create it
        root_folder_id = get_drive_id(file_list, parent_drive_dir)
        if root_folder_id == None:
            root_folder = drive.CreateFile({
                'title': parent_drive_dir,
                'mimeType': 'application/vnd.google-apps.folder'
            })
            root_folder.Upload()
            root_folder_id = get_drive_id(file_list, parent_drive_dir)

        file_list1 = drive.ListFile({
            'q': "'%s' in parents and trashed=false" % root_folder_id}).GetList()

        # Create date stamped folder
        date_str = str(date)
        date_folder_id = get_drive_id(file_list1, date_str)
        if date_folder_id == None:
            date_folder = drive.CreateFile({
                'title': date_str,
                'parents': [{"id": root_folder_id}],
                'mimeType': 'application/vnd.google-apps.folder'
            })
            date_folder.Upload()
            date_folder_id = get_drive_id(file_list1, date_str)

        # Upload images
        for _, _, files in os.walk(dir_processed):
            for filename in files:
                path = os.path.join(dir_processed, filename)
                print('Uploading: ' + path)

                # Upload to Drive
                file1 = drive.CreateFile({
                    'title': filename,
                    'parents': [{'id': date_folder_id}],
                    'mimeType': 'image/jpg'
                })
                file1.SetContentFile(path)
                file1.Upload()

    except Exception as e:
        print('ERROR: ', str(e))

def get_drive_id(file_list, filename):
    for folder in file_list:
        if folder['title'] == filename:
            return folder['id']
    
    return None

def parse_args():
    print('Parsing arguments...')

    desc = 'Process a directory of images by adding a square background and optional padding'
    src_help = 'Source directory of images to be processed'
    dst_help = 'Destination directory for images to be stored'
    padding_help = 'Additional padding to be added, default = 0'

    # Setup argument labels
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('src', help=src_help)
    parser.add_argument('dst', help=dst_help)
    parser.add_argument('padding', help=padding_help)
    args = parser.parse_args()

    global src_dir, dst_dir, padding
    src_dir = args.src.split('=')[1]
    dst_dir = args.dst.split('=')[1]
    padding = int(args.padding.split('=')[1])

    # print(src_dir + '\n' + dst_dir + '\n' + str(padding))

    # Check if there are images available in the parsed directory
    if not os.listdir(src_dir):
        print('Exiting - The provided source folder is empty')
        exit()

# ----- GUI -----

def setup_gui():

    root.title('Prepare-for-insta')
    root.geometry("+1000+500")
    root.resizable(False, False)
    
    # Source label
    src_btn_text = tk.Label(root, text="Source:")
    src_btn_text.grid(row=0, column=0)
    # Source path entry
    src_entry = tk.Entry(root, textvariable=src_label_var)
    src_entry.grid(row=0, column=1)
    # Source browse button
    src_browse_btn = tk.Button(root)
    src_browse_btn["text"] = "Browse..."
    src_browse_btn["command"] = set_src
    src_browse_btn.grid(row=0, column=2, padx=4, pady=4)

    # Destination label
    dst_btn_text = tk.Label(root, text="Output:")
    dst_btn_text.grid(row=1, column=0)
    # Destination path entry
    dst_entry = tk.Entry(root, textvariable=dst_label_var)
    dst_entry.grid(row=1, column=1)
    # Destination browse button
    dst_browse_btn = tk.Button(root)
    dst_browse_btn["text"] = "Browse..."
    dst_browse_btn["command"] = set_dst
    dst_browse_btn.grid(row=1, column=2)

    # Padding label
    padding_text = tk.Label(root, text="Padding:")
    padding_text.grid(row=2, column=0, padx=4, pady=4)
    # Padding path entry
    padding_entry = tk.Entry(root, textvariable=padding_label_var)
    padding_entry.grid(row=2, column=1)

    # Enable Google Drive button
    drive_btn = tk.Checkbutton(root, text="Upload to Google Drive", variable=upload_drive_var)
    drive_btn.grid(row=3, column=1)

    # Process button
    process_btn = tk.Button(root)
    process_btn["text"] = "Run"
    process_btn["command"] = process_images
    process_btn.grid(row=4, padx=4, pady=4)

    root.mainloop()

def set_src():
    src_dir = filedialog.askdirectory()
    src_label_var.set(src_dir)

def set_dst():
    dst_dir = filedialog.askdirectory()
    dst_label_var.set(dst_dir)

setup_gui()