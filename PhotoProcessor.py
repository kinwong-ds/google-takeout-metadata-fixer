import os
import re
import json
import time
from PIL import Image
from datetime import datetime
from tqdm import tqdm
import sys

class PhotoProcessor:
    def __init__(self, all_year_dir):
        self.all_year_dir = all_year_dir

    def rename_json_files(self):
        for directory in tqdm(self.all_year_dir, desc="Renaming JSON files", file=sys.stdout):
            for filename in os.listdir(directory):
                if filename.endswith('.json') and '(' in filename and ')' in filename:
                    new_name = re.sub(r'(.*)\.(.*)$(\d+)$\.json', r'\1(\3).\2.json', filename)
                    os.rename(os.path.join(directory, filename), os.path.join(directory, new_name))
                    tqdm.write(f"Renamed {filename} to {new_name}")
            tqdm.write(f"Finished renaming JSON files in {directory}")

    def change_modified_date(self, file_path):
        if file_path.endswith('.jpg') or file_path.endswith('.JPG'):
            with Image.open(file_path) as img:
                taken_date = img._getexif()[36867]
        elif file_path.endswith('.mp4') or file_path.endswith('.MP4'):
            taken_date = os.path.getmtime(file_path)
        else:
            raise ValueError("Unsupported file type. Only .jpg and .mp4 files are supported.")

        if isinstance(taken_date, str):
            taken_datetime = datetime.strptime(taken_date, "%Y:%m:%d %H:%M:%S")
        else:
            taken_datetime = datetime.fromtimestamp(taken_date)

        taken_timestamp = taken_datetime.timestamp()
        os.utime(file_path, (taken_timestamp, taken_timestamp))

    def update_file_modified_time(self, directory_path, filename):
        if filename.endswith('.MP4'):
            mp4name = filename
            jpgname = filename.replace('.MP4', '.JPG')
            heicname = filename.replace('.MP4', '.HEIC')
            if os.path.exists(os.path.join(directory_path, jpgname)):
                jsonname = jpgname
            elif os.path.exists(os.path.join(directory_path, heicname)):
                jsonname = heicname
            else:
                self.change_modified_date(os.path.join(directory_path, filename))
                return
        else:
            jsonname = filename

        json_file_path = os.path.join(directory_path, f'{jsonname}.json')
        if not os.path.exists(json_file_path):
            json_file_path = json_file_path.split('.')[0][:-1]+'.json'
            if not os.path.exists(json_file_path):
                self.change_modified_date(os.path.join(directory_path, filename))
                return

        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
        photo_taken_timestamp = int(data['photoTakenTime']['timestamp'])
        formatted_time = time.gmtime(photo_taken_timestamp)
        modification_time = time.mktime(formatted_time)
        new_file_path = os.path.join(directory_path, filename)
        os.utime(new_file_path, (modification_time, modification_time))

    def process_directories(self):
        for directory_path in tqdm(self.all_year_dir, desc="Processing Directories", file=sys.stdout):
            for filename in tqdm(os.listdir(directory_path), desc=f"Processing Files in {directory_path}", file=sys.stdout):
                if not filename.endswith('.json'):
                    try:
                        self.update_file_modified_time(directory_path, filename)
                    except ValueError as e:
                        tqdm.write(f"Error processing {filename}: {e}")
            tqdm.write(f"Finished processing {directory_path}")

def get_directory_paths():
    directory_paths = []
    while True:
        directory_path = input("Enter the path to a directory (or 'done' to finish): ")
        if directory_path.lower() == 'done':
            break
        if os.path.isdir(directory_path):
            directory_paths.append(directory_path)
        else:
            print("Invalid directory path. Please try again.")
    return directory_paths

if __name__ == "__main__":
    print("Welcome to the Photo Processor!")
    all_year_dir = get_directory_paths()
    if not all_year_dir:
        print("No directories entered. Exiting.")
    else:
        processor = PhotoProcessor(all_year_dir)
        processor.rename_json_files()
        processor.process_directories()
