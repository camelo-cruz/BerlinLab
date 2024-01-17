# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 13:23:57 2023

@author: Emanuele De Rossi - Universität Potsdam
         Alejandra Camelo Cruz - Universität Potsdam
"""

import argparse
from praatio import textgrid
from praatio.utilities.constants import Interval
import json

def load_json(file_path):
    """Load JSON data from a file and return it as a dictionary."""
    with open(file_path, "r", encoding="utf-8") as jsonfile:
        return json.load(jsonfile)

def create_annotations(json_data, min_timestamp, max_timestamp, include_words=False):
    """Create Praat TextGrid annotations based on the provided JSON data."""
    word_tier = None
    sentence_tier = textgrid.IntervalTier(name="sentences: ", entries=[], minT=min_timestamp, maxT=max_timestamp)

    for segment in json_data["segments"]:
        if include_words:
            if not word_tier:
                word_tier = textgrid.IntervalTier(name="words: ", entries=[], minT=min_timestamp, maxT=max_timestamp)
            for word in segment["words"]:
                print(word["word"], word["start"], word["end"])
                if "start" in word:
                    interval = Interval(start = word["start"], end = word["end"], label = word["word"]) 
                    word_tier.insertEntry(interval)

        if "start" in segment and segment["text"] != "":
            print(segment["text"], segment["start"], segment["end"])
            sentence_interval = Interval(start=segment["start"], end=segment["end"], label=segment["text"])
            sentence_tier.insertEntry(sentence_interval)

    return sentence_tier, word_tier

def main():
    parser = argparse.ArgumentParser(description='Generate timestamps')
    parser.add_argument('input', help='Path to the input JSON file')
    parser.add_argument("-w", '--words', help="Add words timestamps", action="store_true")
    parser.add_argument("-minT", default=0, type=float, help="Minimum timestamp")
    parser.add_argument("-maxT", default=1000, type=float, help="Maximum timestamp")

    args = parser.parse_args()
    json_data = load_json(args.input)

    tg = textgrid.Textgrid()
    sentence_tier, word_tier = create_annotations(json_data, args.minT, args.maxT, include_words=args.words)
    tg.addTier(sentence_tier)
    if word_tier:
        tg.addTier(word_tier)
        

    output = args.input.replace('.json', '.TextGrid')
    tg.save(output, format="long_textgrid", includeBlankSpaces=True, reportingMode="silence")

if __name__ == '__main__':
    main()
