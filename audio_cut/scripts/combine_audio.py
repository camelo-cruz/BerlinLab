#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 15:36:30 2024

@author: Alejandra Camelo Cruz - Leibniz Center General Linguistics
"""

import os
import argparse
from pydub import AudioSegment


def main():
    
    parser = argparse.ArgumentParser(
        description='combine audios. Input two folders with audio and the result will be their combination',
    )
    
    parser.add_argument('first_input', type=str)
    parser.add_argument('second_input', type=str)
    parser.add_argument('-o', '--output', default="../output")
    parser.add_argument('-s', '--silent', default=1, type=int)
    parser.add_argument('-f', '--fade', default=1, type=int)
    
    
    args = parser.parse_args()
    
    
    first_directory = args.first_input
    files_1 = os.listdir(first_directory)
    files_1 = [fname for fname in files_1 if fname.endswith('.wav')]
    
    second_directory = args.second_input
    files_2 = os.listdir(second_directory)
    files_2 = [fname for fname in files_2 if fname.endswith('.wav')]
    
    output_directory = args.output
    os.makedirs(output_directory, exist_ok=True)
    
    for file1 in files_1:
        for file2 in files_2:
            f1_path = os.path.join(first_directory, file1)
            f2_path = os.path.join(second_directory, file2)
            
            audio1 = AudioSegment.from_wav(f1_path)
            audio2 = AudioSegment.from_wav(f2_path)
            
            combined_audio = (audio1 + AudioSegment.silent(args.silent) + audio2.fade_in(args.fade))
            
            output_file_name = f"{os.path.splitext(file1)[0]}_{os.path.splitext(file2)[0]}.wav"
            output_path = os.path.join(output_directory, output_file_name)
            
            combined_audio.export(output_path, format="wav")
            print(f"Combined audio saved as {output_file_name}")
    
    
    
    
    
if __name__ == '__main__':
    main()