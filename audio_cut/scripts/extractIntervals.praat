### extractIntervals.praat
#
# Description:
#   Save relevant intervals from a TextGrid to wav-files
# Options:
#   - filename=label, filename=index, or filename=index+label
#   - exclude intervals with certain labels (empty intervals are always excluded)
#   - crop position = boundary, or crop position = boundary with zero crossing adjustment
#   - user selected target directory to save files
#
# Usage:
#   - select a Sound and a TextGrid
#   - launch the script
#   - specify options
#   - select target directory
#
### jm, 2013-12-04

# Some tests
noSel = numberOfSelected ()
if noSel <> 2
	exit Select a Sound and a TextGrid object, then launch the script.
else
	name1$ = extractWord$ (selected$ (1), " ")
	name2$ = extractWord$ (selected$ (2), " ")
	if name1$ <> name2$
		# different object names, hence sound and textgrid seem not to be associated
		exit Object names do not match!
	endif
	id1 = selected (1)
	id2 = selected (2)
	selectObject (id1)
	dur1 = do ("Get total duration")
	selectObject (id2)
	dur2 = do ("Get total duration")
	selectObject (id1,id2)
	if dur1 <> dur2
		# different object durations, hence sound and textgrid seem not to be associated
		exit Object durations do not match!
	endif
	type1$ = extractWord$ (selected$ (1), "")
	type2$ = extractWord$ (selected$ (2), "")
	if type1$ = "Sound" && type2$ = "TextGrid"
		sound = selected (1)
		grid = selected (2)
	elsif type2$ = "Sound" && type1$ = "TextGrid"
		sound = selected (2)
		grid = selected (1)
	else
		exit Select a Sound and a TextGrid object, then launch the script.
	endif
endif

# let the user specify some options
beginPause ("Extract intervals (labels as names)...")
	comment ("Specify filename pattern")
	choice ("Filename", 1)
	option ("label only (e.g. label.wav)")
	option ("index only (e.g. 001.wav)")
	option ("index + label (e.g. 001_label.wav)")
	comment ("Ignore empty intervals and all intervals with a")
	optionMenu ("label", 1)
	option ("equal to")
	option ("containing")
	option ("not containing")
	option ("starting with")
	option ("not starting with")
	sentence ("the text", "<P>")
	comment ("Extract exactly between boundaries or adjust for zero crossings?")
	boolean ("Adjust zero crossings", 1)
clicked = endPause ("Cancel", "Ok", 2, 1)
if clicked = 1
	exit
endif

# analyse textgrid, count relevant and irrelevant intervals
selectObject (grid)
noInt = do ("Get number of intervals...", 1)
noFiles = 0
noIgn = 0
for i to noInt
	theLabel$ = do$ ("Get label of interval...", 1, i)
	# first, exclude empty intervals
	# then test the different exclusion specifications
	if theLabel$ = ""
		ignore = 1
	elsif label = 1 && theLabel$ = the_text$
		ignore = 1
	elsif label = 2 && index (theLabel$, the_text$) <> 0
		ignore = 1
	elsif label = 3 && index (theLabel$, the_text$) = 0
		ignore = 1
	elsif label = 4 && left$ (theLabel$, length (the_text$)) = the_text$
		ignore = 1
	elsif label = 5 && left$ (theLabel$, length (the_text$)) <> the_text$
		ignore = 1
	else
		ignore = 0
	endif
	if ignore = 0
		noFiles = noFiles + 1
	else
		noIgn = noIgn + 1
	endif
endfor

if noFiles = 0
	# tell user the bad news
	beginPause ("Summary")
		comment (string$ (noInt) + " intervals found;")
		comment (string$ (noFiles) + " intervals have relevant labels;")
		comment (string$ (noIgn) + " intervals will be ignored;")
		comment ("")
		comment ("Sorry, no relevant intervals were found;")
		comment ("check your TextGrid and/or your Ignore settings.")
	clicked = endPause ("Cancel", "Exit", 2, 1)
	selectObject (sound,grid)
	exit
else
	# present analysis result and ask for permission to continue
	beginPause ("Summary")
		comment (string$ (noInt) + " intervals found;")
		comment (string$ (noFiles) + " intervals have relevant labels and will be processed;")
		comment (string$ (noIgn) + " intervals will be ignored;")
		comment ("")
		comment ("If you continue, an editor will appear. Please don't interact!")
		comment ("And be patient, saving " + string$ (noFiles) + " files may take some time.")
	clicked = endPause ("Cancel", "Continue", 2, 1)
	if clicked = 1
		exit
	endif
endif

# let the user select a target directory
dirName$ = chooseDirectory$ ("Choose a directory to save the files in")
if dirName$ = ""
	exit
endif


# now we take the gloves off...
clearinfo
# query name of editor for later
selectObject (grid)
edName$ = selected$ ()
# initializations
index = 1
noSaved = 0
noExtr = 0
# open editor...
selectObject (sound,grid)
do ("View & Edit")
# switch to editor environment
editor 'edName$'
# select first interval
do ("Move cursor to...", 0)
do ("Select next interval")
do ("Select previous interval")
# loop through intervals
for i to noInt
	# query stuff
	theLabel$ = do$ ("Get label of interval")
	start = do ("Get starting point of interval")
	end = do ("Get end point of interval")
	mid = 0.5*(start+end)
	# first, exclude empty intervals
	# then test the different exclusion specifications (same as above)
	if theLabel$ = ""
		ignore = 1
	elsif label = 1 && theLabel$ = the_text$
		ignore = 1
	elsif label = 2 && index (theLabel$, the_text$) <> 0
		ignore = 1
	elsif label = 3 && index (theLabel$, the_text$) = 0
		ignore = 1
	elsif label = 4 && left$ (theLabel$, length (the_text$)) = the_text$
		ignore = 1
	elsif label = 5 && left$ (theLabel$, length (the_text$)) <> the_text$
		ignore = 1
	else
		ignore = 0
	endif
	appendInfo (i, " of ", noInt, " ")
	# do something with relevant intervals
	if ignore = 0 
		if adjust_zero_crossings = 1
			do ("Move start of selection to nearest zero crossing")
			do ("Move end of selection to nearest zero crossing")
		endif
		# assemble nice index with leading zeros for filename
		idx$ = string$ (index)
		while length (idx$) <> length (string$ (noFiles))
			idx$ = "0" + idx$
		endwhile
		# asseble filename according to selected filename pattern
		if filename = 1
			theFilename$ = theLabel$ + ".wav"
		elsif filename = 2
			theFilename$ = idx$ + ".wav"
		else
			theFilename$ = idx$ + "_" + theLabel$ + ".wav"
		endif
		# test for existing file with same name
		# if there is one, extraction only
		if fileReadable (dirName$ + "/" + theFilename$)
			do ("Extract selected sound (time from 0)")
			endeditor
				do ("Rename...", theFilename$ - ".wav")
			editor 'edName$'
			appendInfoLine ("extracted: ", theFilename$ - ".wav")
			noExtr = noExtr + 1
		# if not, save file
		else
			do ("Save selected sound as WAV file...", dirName$ + "/" + theFilename$)
			appendInfoLine ("saved:     ", theFilename$)
			noSaved = noSaved + 1
		endif
		# with zero crossing adjustment on, it's possible that the previous interval
		# is selcted, hence move cursor to mid of target interval
		do ("Move cursor to...", mid)
		index = index + 1
	else
		appendInfoLine ("ignored:   ", theLabel$)
	endif
	do ("Select next interval")
endfor
Close

# generate concluding output
appendInfoLine (newline$, newline$, "=== Summary ===", newline$)
appendInfoLine ("files were saved to:", tab$, dirName$)
appendInfoLine ("processed intervals:", tab$, noInt)
appendInfoLine ("ignored labels:", tab$, tab$, noIgn)
appendInfoLine ("relevant labels:", tab$, tab$, noFiles)
appendInfoLine ("saved files:", tab$, tab$, noSaved)
if noExtr > 0
	appendInfoLine ("extracted intervals:", tab$, noExtr)
	appendInfoLine ("Some intervals couldn't be saved because files with the same name already existed!")
	appendInfoLine ("These intervals were only extracted. You'll find them in the object list.")
endif
