import argparse
import io
import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from PIL import Image
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

WHITE = (255, 255, 255)

src_dir = ''
dst_dir = ''
parent_drive_dir = 'Insta'
padding = 0

def process_images():
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
    out_img = Image.new("RGB", out_size, WHITE)

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

if __name__ == '__main__':
    parse_args()
    process_images()
    save_to_drive()