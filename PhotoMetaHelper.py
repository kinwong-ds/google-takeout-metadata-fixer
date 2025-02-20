import os
import re
from PIL import Image
from datetime import datetime
import json
import time
from tqdm import tqdm

class PhotoMetaHelper:
    def __init__(self, directory_path):
        self.directory_path = directory_path

    def rename_json_file(self, filename):
        if filename.endswith('.json') and '(' in filename and ')' in filename:
            new_name = re.sub(r'(.*)\.(.*)\((\d+)\)\.json', r'\1(\3).\2.json', filename)
            os.rename(os.path.join(self.directory_path, filename), os.path.join(self.directory_path, new_name))

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

    def find_json_filename(self, filename):
        possible_paths = [
            f'{self.directory_path}/{filename}.json',
            f"{self.directory_path}/{filename.split('.')[0][:-1]}.json",
            f'{self.directory_path}/{filename}.supplemental-metadata.json',
            f"{self.directory_path}/{filename.split('.')[0][:-1]}.supplemental-metadata.json",
            f"{self.directory_path}/{filename.split('.')[0]}.supplemental-metadata.json",
            f"{self.directory_path}/{filename.split('(')[0]}.{filename.split('.')[-1]}({filename.split('(')[1].split(')')[0]}).supplemental-metadata.json" if '(' in filename and ')' in filename and '.' in filename else None,
            f'{self.directory_path}/{filename}.suppl.json',
            f'{self.directory_path}/{filename}.supplemen.json'
        ]

        for path in possible_paths:
            if path and os.path.exists(path):
                return path

        raise FileNotFoundError(f'JSON file not found for {filename}')

    def find_jsonname_for_mp4(self, filename):
        mp4name = filename
        jpgname = filename.replace('.MP4', '.JPG')
        heicname = filename.replace('.MP4', '.HEIC')
        if os.path.exists(os.path.join(self.directory_path, jpgname)):
            return jpgname
        elif os.path.exists(os.path.join(self.directory_path, heicname)):
            return heicname
        elif os.path.exists(os.path.join(self.directory_path, heicname)):
            return mp4name
        else:
            self.change_modified_date(f'{self.directory_path}/{filename}')
            return None

    def update_file_modification_time(self, filename, timestamp):
        formatted_time = time.gmtime(timestamp)
        modification_time = time.mktime(formatted_time)
        new_file_path = f'{self.directory_path}/{filename}'
        os.utime(new_file_path, (modification_time, modification_time))

    def rename_files_in_directory(self):
        for filename in os.listdir(self.directory_path):
            self.rename_json_file(filename)

        for filename in tqdm(os.listdir(self.directory_path), desc=f"Processing Files in {self.directory_path}"):
            if not filename.endswith('.json'):
                if filename.endswith('.MP4'):
                    jsonname = self.find_jsonname_for_mp4(filename)
                    if jsonname is None:
                        continue
                    json_file_path = os.path.join(self.directory_path, f'{jsonname}.supplemental-metadata.json')
                else:
                    json_file_path = self.find_json_filename(filename)
                    if json_file_path is None:
                        continue

                with open(json_file_path, 'r') as json_file:
                    data = json.load(json_file)

                photo_taken_timestamp = int(data['photoTakenTime']['timestamp'])
                self.update_file_modification_time(filename, photo_taken_timestamp)

        print(f'Finished with {self.directory_path}')


if __name__ == "__main__":
    directory_path = input("Enter the directory path: ")
    helper = PhotoMetaHelper(directory_path)
    helper.rename_files_in_directory()