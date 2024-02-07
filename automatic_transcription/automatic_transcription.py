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
from pyannote.audio import Pipeline
from pydub import AudioSegment

model = whisper.load_model("large-v3")
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="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")

def process_string(input_string):
    lowercase_string = input_string.lower()

    translator = str.maketrans("", "", string.punctuation)
    processed_string = lowercase_string.translate(translator)

    return processed_string

def cut_audio(audiofile, start, end):
    from pydub import AudioSegment
    
    output = "tmp.wav"

    if audiofile.endswith('.wav'):
        sound = AudioSegment.from_wav(audiofile) # for mp3: AudioSegment.from_mp3()
    elif audiofile.endswith('.mp3'):
        sound = AudioSegment.from_mp3(audiofile)

    StrtTime = float(start) * 1000
    EndTime  = float(end) * 1000
    extract = sound[StrtTime:EndTime]

    # save
    extract.export(output, format="wav")

    return output
    
def transcribe_with_diarization(audiofile):
    transcription = {
        "text": "",
        "segments": []
    }
    #diarize the audiofile
    diarization = pipeline(audiofile)
    
    #for each segment in diarization: get the whisper transcription
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        audio_cut = cut_audio(audiofile, turn.start, turn.end)
        wh_trans = model.transcribe(audio_cut, language="de")
        os.remove(audio_cut)
        
        #add the whisper transcription to dict:transcription with the proper SpeakerID and timestamps
        new_dict = {
            'text': process_string(wh_trans['text']),
            'start': turn.start,
            'end': turn.end,
            'speaker': speaker
            }
        
        transcription['text'] = transcription['text'] + " " + wh_trans['text']
        transcription['segments'].append(new_dict)
    
    return transcription 



def main():
    parser = argparse.ArgumentParser(description="automatic transcription")

    parser.add_argument("input_dir")

    args = parser.parse_args()

    directory = args.input_dir

    warnings.filterwarnings("ignore")
    
    #ffmpeg_path = shutil.which('ffmpeg')
    #os.environ['PATH'] += f':{os.path.dirname(ffmpeg_path)}'
    
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
                  diarized_transcription = transcribe_with_diarization(audio_file_path)
                  translation = model.transcribe(audio_file_path, task='translate')
                  if 'automatic_transcription' not in df.columns:
                    df['automatic_transcription'] = ""
                  if 'automatic_translation' not in df.columns:
                    df['automatic_translation'] = ""
                  series = df[df.isin([file])].stack()
                  #transcription = ""
                  #for segment in diarized_transcription['segments']:
                  #    transcription += transcription + segment['speaker'] + ": " + segment['text']
                  print(diarized_transcription)
                  #for idx, value in series.items():
                    #print(transcription)
                    #df.at[idx[0], "automatic_transcription"] = transcription
                  #  df.at[idx[0], "automatic_translation"] = translation['text']
                    
          df.to_csv(output_file)
          print(f"\nTranscription and translation completed for {subdir}.")


if __name__ == "__main__":
    main()

     

