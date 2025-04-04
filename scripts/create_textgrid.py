import os
import whisper
import json
import torch
import argparse
from pydub import AudioSegment
from praatio import textgrid
from praatio.utilities.constants import Interval

device = "cuda" if torch.cuda.is_available() else "cpu"

# Load the Whisper model on the appropriate device
model = whisper.load_model("large", device=device)


import os
import json

def transcribe(filepath):
    try:
        # Check if the input file exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"The file {filepath} does not exist.")
        
        # Transcribe the audio file
        print(f"Processing file: {filepath}")
        result = model.transcribe(filepath, language='de', word_timestamps=True)
        
        # Save the transcription to a JSON file
        output = os.path.splitext(filepath)[0] + '.json'
        print(f"Saving transcription to: {output}")
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        
        print("Transcription saved successfully.")
    
    except Exception as e:
        print(f"An error occurred: {e}")


def get_audio_length(filepath):
    audio = AudioSegment.from_file(filepath)
    return len(audio) / 1000.0  # Convert milliseconds to seconds

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_annotations(json_data, min_timestamp, max_timestamp, include_words=False):
    sentence_tier = textgrid.IntervalTier(name="sentences", entries=[], minT=min_timestamp, maxT=max_timestamp)
    word_tier = None

    for segment in json_data["segments"]:
        if include_words:
            if not word_tier:
                word_tier = textgrid.IntervalTier(name="words", entries=[], minT=min_timestamp, maxT=max_timestamp)
            for word in segment["words"]:
                if "start" in word:
                    interval = Interval(start=word["start"], end=word["end"], label=word["word"])
                    word_tier.insertEntry(interval)

        if "start" in segment and segment["text"] != "":
            sentence_interval = Interval(start=segment["start"], end=segment["end"], label=segment["text"])
            sentence_tier.insertEntry(sentence_interval)

    return sentence_tier, word_tier

def main():
    parser = argparse.ArgumentParser(description='Generate timestamps')
    parser.add_argument('input', help='Path to the input WAV file')
    parser.add_argument("-w", '--words', help="Add words timestamps", action="store_true")
    parser.add_argument("-minT", default=0, type=float, help="Minimum timestamp")

    args = parser.parse_args()
    transcribe(args.input)
    json_file = args.input.replace('.wav', '.json')
    json_data = load_json(json_file)
    max_timestamp = get_audio_length(args.input)

    tg = textgrid.Textgrid()
    sentence_tier, word_tier = create_annotations(json_data, args.minT, max_timestamp, include_words=args.words)
    tg.addTier(sentence_tier)
    if word_tier:
        tg.addTier(word_tier)

    output = json_file.replace('.json', '.TextGrid')
    tg.save(output, format="long_textgrid", includeBlankSpaces=True, reportingMode="silence")

if __name__ == '__main__':
    main()