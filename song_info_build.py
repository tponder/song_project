'''
This is a script you can use to recreate the data file which from
which dashboard.py directly pulls song information. By modifying this
file, or by editing word_stats.py, explicit_model.py or topic_model.py
you can customize your output.

If you use new/different data input, make sure your data file is in
the same format as in data/song_lyrics.txt.
'''

import explicit_model
import word_stats
import topics_model
import csv

data_file = 'data/songs_lyrics.txt'


# Load data from file.
f = open(data_file,'r')
lines = f.readlines()
f.close()
titles = [lines[x].splitlines()[0] for x in range(1, len(lines), 7)]
artists = [lines[x].splitlines()[0] for x in range(2, len(lines), 7)]
lengths = [float(lines[x].splitlines()[0]) for x in range(3, len(lines), 7)]
featurings = [lines[x].splitlines()[0] for x in range(4, len(lines), 7)]
lyrics = [lines[x].splitlines()[0] for x in range(5, len(lines), 7)]


# Use word_stats.py to calculate song speed and (unqiue words)/(total words)
# for each song.
stats = word_stats.Stats(songs=lyrics,lengths=lengths)
(song_speeds, song_unique_word_percents) = stats.evaluate_stored_songs()


# Use explicit_model.py to create an explicit model, and calculate which songs
# are most explicit. Save the model for reuse later.
exp = explicit_model.Model(lyrics)
exp.build_model()
exp.save_model_to_file('models/explicit_model.txt')
explicit_scores = exp.evaluate_songs()


# Use topics_model to model topics, and calculate which songs cover which topics.
# Save the model for reuse later.
topics = topics_model.Model(lyrics)
topics.plsa(max_iter=0,epsilon=0.001,time_cutoff=60*60*5)
best_topics = topics.songs_topics_strlist()
topics.save_model('models/topic_models.txt')


# Use the collected values, and output to a csv file.
rows = list(zip(titles,artists,lengths,featurings,song_speeds,song_unique_word_percents,explicit_scores,best_topics))
f = open('data/songdash_database.csv','w')
csvw = csv.writer(f)
for row in rows:
    csvw.writerow(row)
f.close()
