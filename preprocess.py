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

#create acoustic features folders
for sound in acoustic:
	mydir = root+'/'+sound
	if True and os.path.isdir(mydir): #CHANGE to True to overwrite existing wav segment directories
		subprocess.call(["rm", "-rf", mydir])
	if not os.path.isdir(mydir):
		subprocess.call(["mkdir", mydir])


#find all TextGrid files
#finds matching audio file if in same directory
for subdir, dirs, files in os.walk(root):
	if not subdir[subdir.rfind('/')+1].isdigit():
		continue
	
	for file in files:
		if file[file.rfind('.')+1:] == 'TextGrid':
			anFiles[subdir+'/'+file] = ''
			tmp = file[:-9]
			if tmp+'.wav' in files and os.path.getsize(subdir+'/'+tmp+'.wav') > 0:
				anFiles[subdir+'/'+file] = subdir+'/'+tmp+'.wav'
			elif tmp+'.flac' in files:
				#convert annotated flac to wav file
				subprocess.call(["flac", "-d", "-f", subdir+'/'+tmp+'.flac'])
				anFiles[subdir+'/'+file] = subdir+'/'+tmp+'.wav'
			else:
				unmatched.append(subdir+'/'+file)
	for file in files:
		if file[file.rfind('.')+1:] == 'flac':
			subprocess.call(["rm", "-f", subdir+'/'+file])
		
	print "Progress : "+str(len(anFiles.keys()))+" /772"

print "Check:"
print "# TextGrids (772) : " + str(len(anFiles.keys()))
print "# unmatched TextGrids (0) : " + str(len(unmatched))
for tg in sorted(unmatched):
	print tg

#tries to find matching flac for TextGrid file if not in same directory
#turns out doesn't find any
'''
for subdir, dirs, files in os.walk(root):
	for file in unmatched:
		tmp = file[file.rfind('/')+1:]
		tmp = tmp[:-9]+'.flac'
		if tmp in files:
			print "yes"
			anFiles[file] = subdir+'/'+tmp
'''

#splits wav files into acoustic feature files according to TextGrid content
prog = 1
for key, value in anFiles.iteritems():
	if len(value) > 0:
		print str(prog)+' /772'
		prog += 1
		annot = TextGrid.load(key)
		
		origAudio = wave.open(value, 'r')
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
	subprocess.call(["rm", "-rf", root+'/train'])
	subprocess.call(["rm", "-rf", root+'/test'])
	subprocess.call(["mkdir", root+'/train'])
	subprocess.call(["mkdir", root+'/test'])
	for sound in acoustic:
		subprocess.call(["mkdir", root+'/train/'+sound])
		subprocess.call(["mkdir", root+'/test/'+sound])

#split acoustic feature files into test and training sets
#TODO: create acoustic folders in train and test
#TODO: split accoustic folder contents between two sets
