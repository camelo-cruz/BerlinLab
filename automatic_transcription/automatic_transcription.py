# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import whisper
import shutil
import warnings
import argparse
import string
import pandas as pd
from tqdm import tqdm


def process_string(input_string):
    lowercase_string = input_string.lower()

    translator = str.maketrans("", "", string.punctuation)
    processed_string = lowercase_string.translate(translator)

    return processed_string


def main():
    parser = argparse.ArgumentParser(description="automatic transcription")

    parser.add_argument("input_dir")

    args = parser.parse_args()

    directory = args.input_dir

    warnings.filterwarnings("ignore")

    # ffmpeg_path = shutil.which('ffmpeg')
    # os.environ['PATH'] += f':{os.path.dirname(ffmpeg_path)}'

    model = whisper.load_model("large-v3")

    for subdir, dirs, files in os.walk(directory):
        if 'binaries' in subdir:
            csv_file_path = os.path.join(subdir, '..', 'trials_and_sessions.csv')
            excel_file_path = os.path.join(subdir, '..', 'trials_and_sessions.xlsx')
            output_file = os.path.join(subdir, '..', 'trials_and_sessions_annotated.csv')
            if os.path.exists(csv_file_path):
                df = pd.read_csv(csv_file_path)
            elif os.path.exists(excel_file_path):
                df = pd.read_excel(excel_file_path)

            for file_count, file in enumerate(tqdm(files, desc=f"Processing Files in {subdir}", unit="file")):
                if file.endswith('.mp3'):
                    # Use subdir as the base directory
                    audio_file_path = os.path.join(subdir, file)
                    # Perform transcription and translation
                    transcription = model.transcribe(audio_file_path)
                    transcription = process_string(transcription["text"])
                    translation = model.transcribe(audio_file_path, task='translate')
                    translation = translation['text']

                    # create columns if they doesn't exist
                    if 'automatic_transcription' not in df.columns:
                        df['automatic_transcription'] = ""
                    if 'automatic_translation' not in df.columns:
                        df['automatic_translation'] = ""

                    # find in which column and row the file is
                    series = df[df.isin([file])].stack()
                    for idx, value in series.items():
                        df.at[idx[0], "automatic_transcription"] += f"\ntranscription {file_count}: {transcription}"
                        df.at[idx[0], "automatic_translation"] += f"\ntranslation {file_count}: {translation}"

            df.to_csv(output_file)

    print(f"\nTranscription and translation completed for {subdir}.")


if __name__ == "__main__":
    main()