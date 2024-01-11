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
import pandas as pd
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description = "automatic transcription")
    
    parser.add_argument("input_dir")
    
    args = parser.parse_args()
    
    directory = args.input_dir

    warnings.filterwarnings("ignore")
    
    #ffmpeg_path = shutil.which('ffmpeg')
    #os.environ['PATH'] += f':{os.path.dirname(ffmpeg_path)}'
    
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
              
          for file in tqdm(files, desc=f"Processing Files in {subdir}", unit="file"):
              if file.endswith('.mp3'):
                  # Use subdir as the base directory
                  audio_file_path = os.path.join(subdir, file)
                  # Perform transcription and translation
                  transcription = model.transcribe(audio_file_path)
                  translation = model.transcribe(audio_file_path, task='translate')
                  if 'automatic_transcription' not in df.columns:
                    df['automatic_transcription'] = ""
                  if 'automatic_translation' not in df.columns:
                    df['automatic_translation'] = ""
                  series = df[df.isin([file])].stack()
                  for idx, value in series.items():
                    df.at[idx[0], "automatic_transcription"] = transcription['text']
                    df.at[idx[0], "automatic_translation"] = translation['text']
                    
          df.to_csv(output_file)

              
    print(f"\nTranscription and translation completed for {subdir}.")
    
if __name__ == "__main__":
    main()