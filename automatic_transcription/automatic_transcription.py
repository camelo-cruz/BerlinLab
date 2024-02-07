# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import whisper
import warnings
import argparse
import string
import pandas as pd
from pydub import AudioSegment
from pyannote.audio import Pipeline
from tqdm import tqdm


warnings.filterwarnings("ignore")
model = whisper.load_model("large-v3")
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="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")


def process_string(input_string):
    """
    Process a string by converting it to lowercase and removing punctuation.

    Parameters:
        input_string (str): The string to be processed.

    Returns:
        str: The processed string.
    """
    lowercase_string = input_string.lower()

    translator = str.maketrans("", "", string.punctuation)
    processed_string = lowercase_string.translate(translator)

    return processed_string


def cut_audio(audiofile, start, end):
    """
    Cut a segment from an audio file based on start and end timestamps.

    Parameters:
        audiofile (str): Path to the input audio file.
        start (float): Start timestamp (in seconds) for the segment.
        end (float): End timestamp (in seconds) for the segment.

    Returns:
        str: Path to the output audio file containing the segment.
    """
    output = "tmp.wav"

    if audiofile.endswith('.wav'):
        sound = AudioSegment.from_wav(audiofile)  # for mp3: AudioSegment.from_mp3()
    elif audiofile.endswith('.mp3'):
        sound = AudioSegment.from_mp3(audiofile)

    StrtTime = float(start) * 1000
    EndTime = float(end) * 1000
    extract = sound[StrtTime:EndTime]

    # save
    extract.export(output, format="wav")

    return output


def transcribe_with_diarization(audiofile):
    """
    Perform transcription with speaker diarization on an audio file.

    Parameters:
        audiofile (str): Path to the input audio file.

    Returns:
        list: List of dictionaries containing transcription information.
    """
    transcription = []
    # diarize the audiofile
    diarization = pipeline(audiofile)

    # for each segment in diarization: get the whisper transcription
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        audio_cut = cut_audio(audiofile, turn.start, turn.end)
        wh_trans = model.transcribe(audio_cut, language="de")
        os.remove(audio_cut)

        # add the whisper transcription to dict:transcription with the proper SpeakerID and timestamps
        new_dict = {
            'text': process_string(wh_trans['text']),
            'start': turn.start,
            'end': turn.end,
            'speaker': speaker
        }

        transcription.append(new_dict)

    return transcription



def process_data(directory, diarization = False):
    """
    Process audio files in a directory, perform transcription, and update a CSV file.

    Parameters:
        directory (str): Path to the input directory.
    """
    for subdir, dirs, files in os.walk(directory):
        if 'binaries' in subdir:
            csv_file_path = os.path.join(subdir, '..', 'trials_and_sessions.csv')
            excel_file_path = os.path.join(subdir, '..', 'trials_and_sessions.xlsx')
            output_file = os.path.join(subdir, '..', 'trials_and_sessions_annotated.csv')
            if diarization:
                output_file = os.path.join(subdir, '..', 'trials_and_sessions_diarized.csv')
            if os.path.exists(csv_file_path):
                df = pd.read_csv(csv_file_path)
            elif os.path.exists(excel_file_path):
                df = pd.read_excel(excel_file_path)

            for file in tqdm(files, desc=f"Processing Files in {subdir}", unit="file"):
                if file.endswith('.mp3'):
                    # Use subdir as the base directory
                    audio_file_path = os.path.join(subdir, file)
                    if 'automatic_transcription' not in df.columns:
                        df['automatic_transcription'] = ""
                    if 'automatic_translation' not in df.columns:
                        df['automatic_translation'] = ""
                    series = df[df.isin([file])].stack()
                    transcription = ""
                    if diarization:
                        diarized_transcription = transcribe_with_diarization(audio_file_path)
                        add_speaker = lambda segment: f"{'CHI:' if '00' in segment['speaker'] else 'EXP:'}: {segment['text']} "
                        for index in range(len(diarized_transcription)):
                            segment = diarized_transcription[index]
                            if index != 0:
                                previous_speaker = diarized_transcription[index - 1]["speaker"]
                                current_speaker = diarized_transcription[index]["speaker"]
                                same_speaker = previous_speaker == current_speaker
                                if same_speaker:
                                    transcription += segment['text'] + " "
                                else:
                                    transcription += add_speaker(segment)
                            else:
                                transcription += add_speaker(segment)
                        print(transcription)
                    else:
                        transcription = model.transcribe(audio_file_path)
                        transcription = transcription["text"]
                    translation = model.transcribe(audio_file_path, task='translate')
                    for idx, value in series.items():
                        df.at[idx[0], "automatic_transcription"] = transcription
                        df.at[idx[0], "automatic_translation"] = translation['text']

            df.to_csv(output_file)
            print(f"\nTranscription and translation completed for {subdir}.")



def main():
    """
    Main function to parse command line arguments and initiate data processing.
    """
    parser = argparse.ArgumentParser(description="automatic transcription")
    parser.add_argument("input_dir")
    parser.add_argument("--diarization", action="store_true")
    args = parser.parse_args()
    process_data(args.input_dir, args.diarization)

if __name__ == "__main__":
    main()
