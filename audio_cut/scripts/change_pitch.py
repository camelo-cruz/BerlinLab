#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 16:54:07 2024

@author: alejandra
"""

import os
import librosa
import pyrubberband
import argparse
import soundfile as sf
print(sf.__file__)


def change_pitch(input_wav, output_wav, semitone):
    y, sr = librosa.load(input_wav)
    new_y = pyrubberband.pitch_shift(y, sr, semitone)
    sf.write(output_wav, new_y, sr)

def process_folder(input_folder, output_folder, semitone):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate over each file and folder in the input folder
    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.endswith(".wav"):
                input_file_path = os.path.join(root, filename)
                # Determine relative path to input_folder
                relative_path = os.path.relpath(input_file_path, input_folder)
                output_file_path = os.path.join(output_folder, relative_path)
                # Create output subfolder if it doesn't exist
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                change_pitch(input_file_path, output_file_path, semitone)

def main():
    parser = argparse.ArgumentParser(
        description='changes pitch',
    )

    parser.add_argument('input', type=str)
    parser.add_argument('output', type=str)
    parser.add_argument('--semitone', default=-1.5)
    
    args = parser.parse_args()

    process_folder(args.input, args.output, args.semitone)
    
if __name__ == "__main__":
    main()