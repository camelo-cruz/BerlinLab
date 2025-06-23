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


def transcribe(filepath):
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"The file {filepath} does not exist.")
        print(f"Processing file: {filepath}")
        result = model.transcribe(filepath, language='de', word_timestamps=True)
        output = os.path.splitext(filepath)[0] + '.json'
        print(f"Saving transcription to: {output}")
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print("Transcription saved successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


def get_audio_length(filepath):
    audio = AudioSegment.from_file(filepath)
    return len(audio) / 1000.0  # seconds


def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def create_annotations(json_data, min_timestamp, max_timestamp, include_words=False):
    sentence_tier = textgrid.IntervalTier(name="sentences", entries=[], minT=min_timestamp, maxT=max_timestamp)
    word_tier = None
    counter = 1

    for segment in json_data.get("segments", []):
        # Add word-level intervals with generic labels
        if include_words:
            if word_tier is None:
                word_tier = textgrid.IntervalTier(name="words", entries=[], minT=min_timestamp, maxT=max_timestamp)
            for word in segment.get("words", []):
                if "start" in word and "end" in word:
                    label = f"item{counter}"
                    interval = Interval(start=word["start"], end=word["end"], label=label)
                    word_tier.insertEntry(interval)
                    counter += 1
        # Add sentence-level intervals with generic labels
        if "start" in segment and "end" in segment:
            label = f"item{counter}"
            sentence_interval = Interval(start=segment["start"], end=segment["end"], label=label)
            sentence_tier.insertEntry(sentence_interval)
            counter += 1

    return sentence_tier, word_tier


def main():
    parser = argparse.ArgumentParser(description='Generate generic-item TextGrid')
    parser.add_argument('input', help='Path to the input WAV file')
    parser.add_argument('-w', '--words', help='Include word-level items', action='store_true')
    parser.add_argument('-minT', default=0, type=float, help='Minimum timestamp')
    args = parser.parse_args()

    transcribe(args.input)
    base, _ = os.path.splitext(args.input)
    json_file = base + '.json'
    json_data = load_json(json_file)

    # Determine full audio length and set grid bounds
    max_timestamp = get_audio_length(args.input)

    # Create a Textgrid with explicit bounds matching the audio
    tg = textgrid.Textgrid(minT=args.minT, maxT=max_timestamp)
    sentence_tier, word_tier = create_annotations(json_data, args.minT, max_timestamp, include_words=args.words)
    tg.addTier(sentence_tier)
    if word_tier:
        tg.addTier(word_tier)

    output = base + '.TextGrid'
    tg.save(output, format='long_textgrid', includeBlankSpaces=True, reportingMode='silence')
    print(f"TextGrid saved to: {output}")

if __name__ == '__main__':
    main()
