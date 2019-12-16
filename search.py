'''
This is a script that allows a user to search for a song of interest.
If matching title(s) is found, the information for that song will be
printed.

This script does not use sophisticated search techniques. The use case
in mind will lead a user to search for a specific title, which is not
really the same problem of returning most relevant documents. If you want
to use a larger song database, using an inverted index would be faster.
'''

import math
import csv


# Set options
data_file = 'data/songs_lyrics.txt'
number_of_results = 1


# Load song info used in query-matching
f = open(data_file,'r')
lines = f.readlines()
f.close()
titles = [lines[x].splitlines()[0].lower() for x in range(1, len(lines), 7)]
artists = [lines[x].splitlines()[0].lower() for x in range(2, len(lines), 7)]
featurings = [lines[x].splitlines()[0].lower() for x in range(4, len(lines), 7)]


# Ask user for query
query = input('Search by Title/Artist: ').lower().split()


# Determine the songs most likely related to the query
scores = []
for i in range(len(titles)):
    score = 0
    title_terms = titles[i].split()
    artist_terms = artists[i].split()
    featuring_terms = featurings[i].split()
    for q in query:
        if q in title_terms:
            score += 3.0
        if q in artist_terms:
            score += 2.0
        if q in featuring_terms:
            score +=0.5
    score = score/(math.log2(len(title_terms)+len(artist_terms)))
    scores.append((i,score))
scores = sorted(scores,key=lambda x: -x[1])


# If no songs-query matches are found, exit
if scores[0][1] == 0:
    print('No songs found.')
    exit()


# Load the song dashboard database
f = open('data/songdash_database.csv','r')
csvr = csv.reader(f)
allsongs = list(csvr)
f.close()


# Print the song dashboard for the songs best matching the query
for i in range((number_of_results-1),-1,-1):
    if scores[i][1] == 0:
        continue
    print(f'\nResult #{i+1}')
    print(f'Title               {allsongs[scores[i][0]][0]}')
    print(f'Artist              {allsongs[scores[i][0]][1]}')
    print(f'Featuring           {allsongs[scores[i][0]][3]}')
    print(f'Length(secs)        {allsongs[scores[i][0]][2]}')
    print(f'Words/Second        {allsongs[scores[i][0]][4]}')
    print(f'Unique/Total Words  {allsongs[scores[i][0]][5]}')
    print(f'Explicit Rating     {allsongs[scores[i][0]][6]}')
    print(f'Topics              {allsongs[scores[i][0]][7]}')
