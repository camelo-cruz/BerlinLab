# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 13:23:57 2023

@author: emanu
"""

from praatio import textgrid
from praatio.utilities.constants import Interval

import json 

with open("input.json", "r", encoding = "utf-8") as jsonfile:
    
    speakonly = json.load(jsonfile)
    

# create an empty textgrid
tg = textgrid.Textgrid()

# create a tier to store all the words
wordTier = textgrid.IntervalTier(name = "words: ", entries = [], minT = 0, maxT = 10000)

all_words = dict()
#idx = 1
for segment in speakonly["segments"]:
    for word in segment["words"]:
        print(word["word"], word["start"], word["end"])
        all_words[word["word"]] = (word["start"], word["end"])
        
        # create the intervals for the tier
        
        # IF YOU USE WHISPER_TIMESTAMPED, UNCOMMENT THIS LINE AND COMMENT THE 3 LINES BELOW
        # interval = Interval(start = word["start"], end = word["end"], label = word["text"], )
        # wordTier.insertEntry(interval)
        
        
        # IF YOU USE WHISPERX, USE THESE 3 LINES INSTEAD
        if "start" in word:
            interval = Interval(start = word["start"], end = word["end"], label = word["word"]) 
            wordTier.insertEntry(interval)
        
        
        
# add the tier to the textgrid

# tg.addTier(wordTier)


#print(tg.wordTier.entries)
        
#print(tg.tierNames)
# save the textgrid

tg.save("output.TextGrid", format="long_textgrid", includeBlankSpaces=True, reportingMode = "silence")
