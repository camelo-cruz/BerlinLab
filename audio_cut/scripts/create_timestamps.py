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

def main():
    parser = argparse.ArgumentParser(
        description='generate timestamps'
    )
    
    parser.add_argument('input')
    parser.add_argument('--sentence', help="Add sentence timestamps", action="store_true")
    
    args = parser.parse_args()
    
    with open(args.input, "r", encoding = "utf-8") as jsonfile:
        speakonly = json.load(jsonfile)
    
    # create an empty textgrid
    tg = textgrid.Textgrid()
    
    # create a tier to store all the words
    wordTier = textgrid.IntervalTier(name = "words: ", entries = [], minT = 0, maxT = 1000)
    #create a tier to store sentences 
    sentenceTier = textgrid.IntervalTier(name = "sentences: ", entries = [], minT = 0, maxT = 1000)
    
    all_words = dict()
    for segment in speakonly["segments"]:
        
        #create tier entry for word
        for word in segment["words"]:
            print(word["word"], word["start"], word["end"])
            all_words[word["word"]] = (word["start"], word["end"])
            
    
            if "start" in word:
                interval = Interval(start = word["start"], end = word["end"], label = word["word"]) 
                wordTier.insertEntry(interval)
            
        #create tier entry for sentence
        if "start" in segment and args.sentence and segment["text"] != "":
            s_interval = Interval(start = segment["start"], end = segment["end"], label = segment["text"])
            sentenceTier.insertEntry(s_interval)
        
            
    # add the tier to the textgrid
    tg.addTier(wordTier)
    tg.addTier(sentenceTier)
    
    output = args.input.replace('.json', '.TextGrid')
    
    
    tg.save(output, format="long_textgrid", includeBlankSpaces=True, reportingMode = "silence")

if __name__ == '__main__':
    main()
