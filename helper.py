import os
import re
from PIL import Image
from datetime import datetime
import json
import time
from tqdm import tqdm

def rename_json_file(directory_path, filename):
    if filename.endswith('.json') and '(' in filename and ')' in filename:
        new_name = re.sub(r'(.*)\.(.*)\((\d+)\)\.json', r'\1(\3).\2.json', filename)
        os.rename(os.path.join(directory_path, filename), os.path.join(directory_path, new_name))

def change_modified_date(file_path):
    # Check the file extension
    if file_path.endswith('.jpg') or file_path.endswith('.JPG'):
        # Open the image file
        with Image.open(file_path) as img:
            # Extract the taken date from the metadata
            taken_date = img._getexif()[36867]  # This is a common tag for taken date
    elif file_path.endswith('.mp4') or file_path.endswith('.MP4'):
        # Get the creation date of the MP4 file
        taken_date = os.path.getmtime(file_path)
    else:
        raise ValueError("Unsupported file type. Only .jpg and .mp4 files are supported.")

    # Parse the taken date to a datetime object
    if isinstance(taken_date, str):
        taken_datetime = datetime.strptime(taken_date, "%Y:%m:%d %H:%M:%S")
    else:
        taken_datetime = datetime.fromtimestamp(taken_date)

    # Convert datetime to a timestamp
    taken_timestamp = taken_datetime.timestamp()

    # Change the modified date of the file
    os.utime(file_path, (taken_timestamp, taken_timestamp))


def find_json_filename(directory_path, filename):
    possible_paths = [
        f'{directory_path}/{filename}.json',
        f"{directory_path}/{filename.split('.')[0][:-1]}.json",
        f'{directory_path}/{filename}.supplemental-metadata.json',
        f"{directory_path}/{filename.split('.')[0][:-1]}.supplemental-metadata.json",
        f"{directory_path}/{filename.split('.')[0]}.supplemental-metadata.json",
        f"{directory_path}/{filename.split('(')[0]}.{filename.split('.')[-1]}({filename.split('(')[1].split(')')[0]}).supplemental-metadata.json" if '(' in filename and ')' in filename and '.' in filename else None,
        f'{directory_path}/{filename}.suppl.json',
        f'{directory_path}/{filename}.supplemen.json'
    ]

    for path in possible_paths:
        if path and os.path.exists(path):
            return path

    raise FileNotFoundError(f'JSON file not found for {filename}')

def find_jsonname_for_mp4(directory_path, filename):
    mp4name = filename
    jpgname = filename.replace('.MP4', '.JPG')
    heicname = filename.replace('.MP4', '.HEIC')
    if os.path.exists(os.path.join(directory_path, jpgname)):
        return jpgname
    elif os.path.exists(os.path.join(directory_path, heicname)):
        return heicname
    elif os.path.exists(os.path.join(directory_path, heicname)):
        return mp4name
    else:
        change_modified_date(f'{directory_path}/{filename}')
        return None

def update_file_modification_time(directory_path, filename, timestamp):
    formatted_time = time.gmtime(timestamp)
    modification_time = time.mktime(formatted_time)
    new_file_path = f'{directory_path}/{filename}'
    os.utime(new_file_path, (modification_time, modification_time))


def rename_files_in_directory(directory_path):
    for filename in os.listdir(directory_path):
        rename_json_file(directory_path, filename)

    for filename in tqdm(os.listdir(directory_path), desc=f"Processing Files in {directory_path}"):
        if not filename.endswith('.json'):
            if filename.endswith('.MP4'):
                jsonname = find_jsonname_for_mp4(directory_path, filename)
                if jsonname is None:
                    continue
                json_file_path = os.path.join(directory_path, f'{jsonname}.supplemental-metadata.json')
            else:
                json_file_path = find_json_filename(directory_path, filename)
                if json_file_path is None:
                    continue

            with open(json_file_path, 'r') as json_file:
                data = json.load(json_file)

            photo_taken_timestamp = int(data['photoTakenTime']['timestamp'])
            update_file_modification_time(directory_path, filename, photo_taken_timestamp)

    print(f'Finished with {directory_path}')