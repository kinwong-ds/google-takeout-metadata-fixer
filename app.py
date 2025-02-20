import streamlit as st
import os
from PhotoMetaHelper import PhotoMetaHelper
import json

st.title("Photo Metadata Helper")
st.write("Select directories to process:")

# Allow user to select multiple directories
directory_paths = st.text_area("Enter directory paths separated by commas").split(',')

if st.button("Process Directories"):
    if directory_paths:
        for directory_path in directory_paths:
            directory_path = directory_path.strip()
            st.write(f"Processing directory: {directory_path}")

            # Initialize the PhotoMeta
            PhotoMeta = PhotoMetaHelper(directory_path)

            # Rename files and update modification times
            for filename in os.listdir(directory_path):
                PhotoMeta.rename_json_file(filename)
            st.success(f"Finished renaming json files for {directory_path}")

            # Create a progress bar
            progress_text = "Modifying file metadata..."
            progress_bar = st.progress(0, text=progress_text)

            all_files = os.listdir(directory_path)
            total_files = len([file for file in all_files if not file.endswith('.json')])
            processed_files = 0

            for filename in os.listdir(directory_path):
                if not filename.endswith('.json'):
                    if filename.endswith('.MP4'):
                        jsonname = PhotoMeta.find_jsonname_for_mp4(filename)
                        if jsonname is None:
                            continue
                        json_file_path = os.path.join(directory_path, f'{jsonname}.supplemental-metadata.json')
                    else:
                        json_file_path = PhotoMeta.find_json_filename(filename)
                        if json_file_path is None:
                            continue

                    with open(json_file_path, 'r') as json_file:
                        data = json.load(json_file)

                    photo_taken_timestamp = int(data['photoTakenTime']['timestamp'])
                    PhotoMeta.update_file_modification_time(filename, photo_taken_timestamp)

                    processed_files += 1
                    percent_complete = processed_files/total_files
                    progress_bar.progress(percent_complete, text=progress_text)

            st.success(f"Finished processing {directory_path}")