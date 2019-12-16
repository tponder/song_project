'''
This file is used to create an 'explicit' language model.
This can then be used to rate songs on how explicit they are.

This is done by taking songs that are known to be explicit (songs that
contain at least one word from a list) and using them to create a
large set of words. Songs that have highest similarity to this are
considered more explicit. TF weighting is used.

The starting explicit words can be altered by changing the list in
the model class below. Generally, adding more words to the explicit list
(as long as they are reasonable) doesn't vary model, and the same
songs will have high explicit scores.

More complex and perhaps more accurate techniques are possible here.
'''

import metapy
import math

class Model:
    '''
    Calculate the explicitness of songs.
    '''
    def __init__ (self,songs=[]):
        '''
        Initialize with an array of songs, and array of song lengths.
        '''
        self.explicit_words = ['fuck','motherfuck','fuckin']
        self.songs = songs
        self.model = {}

    def set_songs_from_file(self, song_database_file):
        '''
        Use a file to load song lyrics.
        '''
        f = open(song_database_file,'r')
        lines = f.readlines()
        f.close()
        self.songs = [lines[x] for x in range(5, len(lines), 7)]

    def build_model(self):
        '''
        Build a language model from songs that are known to be explicit.
        These are songs that contain at least one word from explicit_words.
        '''
        ana = metapy.analyzers.load('config/config.toml')
        doc = metapy.index.Document()
        model = {}
        word_corpus_frequency = {}
        for song in self.songs:
            doc.content(song)
            words = ana.analyze(doc)
            exp_song = False
            for exp_word in self.explicit_words:
                if exp_word in words:
                    exp_song = True
            if exp_song:
                for word in words:
                    if word in model:
                        model[word] += words[word]
                    else:
                        model[word] = words[word]
            for word in words:
                if word in word_corpus_frequency:
                    word_corpus_frequency[word] += 1
                else:
                    word_corpus_frequency[word] = 1
        
        for word in model:
            model[word] = math.log2((len(self.songs)+1)/word_corpus_frequency[word])*model[word]
        modelsum = sum(model.values())
        model = sorted(list(zip(model.keys(), model.values())), key=lambda x: -x[1])[:200]
        modelsum = sum([x[1] for x in model])
        model = dict([(x[0],x[1]/modelsum) for x in model])
        self.model = model

    def evaluate_song(self,song):
        '''
        Calculates the explicit score for a song, given its lyrics. Uses the
        langauge model previously built.
        '''
        ana = metapy.analyzers.load('config/config.toml')
        doc = metapy.index.Document()
        doc.content(song)
        words = ana.analyze(doc)
        similarity_sum = 0
        for word in words:
            if word in self.model:
                similarity_sum += words[word] * self.model[word]
        return similarity_sum

    def evaluate_songs(self):
        '''
        Calculates the explicit scores for all songs available (the songs used
        in building the model). Returns the explicit scores for all songs as a
        list, in same order.
        '''
        explicit_scores = []
        for song in self.songs:
            explicit_scores.append(self.evaluate_song(song))
        explicit_scores = [x/max(explicit_scores) for x in explicit_scores]
        return explicit_scores
    
    def save_model_to_file(self, output_file):
        '''
        Save the explicit language model to a csv file
        '''
        f = open(output_file, 'w')
        output = []
        for word in self.model:
            output.append(f'{word},{self.model[word]}')
        f.write('\n'.join(output))
        f.close()
    
    def load_model_from_file(self, input_file):
        '''
        Load a previously saved language model.
        '''
        f = open(input_file, 'r')
        lines = f.readlines()
        print(len(lines))
        f.close
        for line in lines:
            line_split = line.splitlines()[0].split(',')
            self.model[line_split[0]] = float(line_split[1])
        print(self.model)
