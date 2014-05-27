#!/bin/bash
import sys
import os
import os.path
import subprocess
import wave
from textgrid import TextGrid

root = '../elephants' #CHANGE for your setup

anFiles = {}
unmatched = []
acoustic = [
	"GRW","SQK", "LRM", "LRR", "RUM", "BRM", "TMP", "RRM", "ROR", "BRK", "SQL", "CRM1", "CRM2", "MCR"
]

#find all TextGrid files
#finds matching flac file if in same directory
for subdir, dirs, files in os.walk(root):
	if not subdir[subdir.rfind('/')+1].isdigit():
		continue
	
	for file in files:
		if file[file.rfind('.')+1:] == 'TextGrid':
			anFiles[subdir+'/'+file] = ''
			tmp = file[:-9]+'.flac'
			if tmp in files:
				anFiles[subdir+'/'+file] = subdir+'/'+tmp
			else:
				unmatched.append(subdir+'/'+file)

#tries to find matching flac for TextGrid file if not in same directory
#turns out doesn't find any
for subdir, dirs, files in os.walk(root):
	for file in unmatched:
		tmp = file[file.rfind('/')+1:]
		tmp = tmp[:-9]+'.flac'
		if tmp in files:
			print "yes"
			anFiles[file] = subdir+'/'+tmp


#create acoustic features folders
for sound in acoustic:
	mydir = root+'/'+sound
	if True and os.path.isdir(mydir): #CHANGE to True to overwrite existing wav segment directories
		subprocess.call(["rm", "-rf", mydir])
	if not os.path.isdir(mydir):
		subprocess.call(["mkdir", mydir])

#converts annotated flac to wav files
for key, value in anFiles.iteritems():
	if len(value) > 0:
		if False or not os.path.isfile(value[:-5]+'.wav'): #CHANGE to True to overwrite existing wav file
			subprocess.call(["flac", "-d", "-f", value])

#splits wav files into acoustic feature files according to TextGrid content
for key, value in anFiles.iteritems():
	if len(value) > 0:
		print key
		annot = TextGrid.load(key)
		
		origAudio = wave.open(value[:-5]+'.wav', 'r')
		frameRate = origAudio.getframerate()
		nChannels = origAudio.getnchannels()
		sampWidth = origAudio.getsampwidth()	

		count = 0

		#iterate over items/tiers
		#print key
		for i, tier in enumerate(annot):
			for (xmin, xmax, atype) in tier.simple_transcript: 
				start = float(xmin)
				end = float(xmax)
				
				if atype not in acoustic:
					continue

				origAudio.setpos(int(start*frameRate))
				chunkData = origAudio.readframes(int((end-start)*frameRate))
				#TODO: use tell?
					
				outfile = root + '/' + atype + value[value.rfind('/'):-5]+'_'+str(count)+'.wav' 
				count += 1
				chunkAudio = wave.open(outfile, 'w')
				chunkAudio.setnchannels(nChannels)
				chunkAudio.setsampwidth(sampWidth)
				chunkAudio.setframerate(frameRate)
				chunkAudio.writeframes(chunkData)
				chunkAudio.close()

#create train/test folders
if True: #CHANGE to False to not rewrite test/train sections
	subprocess.call(["rm", "-rf", root+'/'+'train'])
	subprocess.call(["rm", "-rf", root+'/'+'test'])
	subprocess.call(["mkdir", root+'/'+'train'])
	subprocess.call(["mkdir", root+'/'+'test'])

#split acoustic feature files into test and training sets
#TODO: turns out not that many samples per call type
