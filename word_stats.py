'''
This file is used to calculate various simple flat statistics
on the words in songs. In particular, the currently calculated
stats are words/second, unique words/total words, avg word length,
and 'avg scrabble pts'/word.

The techniques used to calculate these statistics are not complex,
but these are statistics that you want to have access to, as they
tell you a lot about a song.
'''

class Stats:
    '''
    Calculate simple statistics on songs.
    '''
    def __init__(self, songs=[], lengths=[]):
        '''
        Initialize with an array of songs, and array of song lengths.
        '''
        self.songs = songs
        self.lengths = lengths
    
    def set_songs_from_file(self, song_database_file):
        '''
        Use a file to load song lyrics and lengths.
        '''
        f = open(song_database_file,'r')
        lines = f.readlines()
        f.close()
        self.songs = [lines[x].splitlines()[0] for x in range(5, len(lines), 7)]
        self.lengths = [float(lines[x].splitlines()[0]) for x in range(3, len(lines), 7)]

    
    def evaluate_song(self, song, length):
        '''
        Calculates the words/second and unique words/total words values
        for a song, given the lyrics and length.
        '''
        words = song.split()
        rate = len(words)/length
        song_vocab = set()
        for word in words:
            if word not in song_vocab:
                song_vocab.add(word)
        unique_prop = len(song_vocab)/len(words)
        return (rate, unique_prop)

    def evaluate_stored_songs(self):
        '''
        Calculates the words/second and unique words/total words values
        for all songs available, that have been loaded. The values are
        returned as a pair of arrays, in the same order.
        '''
        rates, unique_props = [], []
        for i in range(len(self.songs)):
            (rate, unique_prop) = self.evaluate_song(self.songs[i], self.lengths[i])
            rates.append(rate)
            unique_props.append(unique_prop)
        return (rates, unique_props)
