# Song Dashboard Project

## What is this?

### Overview

Many people frequently listen to songs on the radio, or listen to music from sources where they don't have precise control over which songs are played. If a user is not familiar with a song that starts playing, they can either skip the song or they must listen to the song to determine whether they like it. Many users use basic information like the artist to decide whether they're likely to enjoy the song. This project aims to provide users a better "dashboard" of information about the song that they can use to determine whether they want to press skip, or change the radio channel. Collecting more complex information about songs could also be useful for other things. For example, you could use song information to create filters, which could be used for auto-generation of playlists.

To generate these song dashboards, song lyrics are used, and text mining techniques are used to gain information about the songs.

### Song Metrics Calculated

Speed - Words/Second

Repetitiveness - Unique Words/Total Words

Explicitness Score - More explicit songs have higher values (range 0-1).

Topics - Topics that are most related to a song.

## Usage

### Setup

This project is written in Python. To use this project, you should make sure you have a working installation of python3.7. You need to have the following packages (some of these may come preinstalled) : numpy, metapy, csv. You can generally install these with:

```bash
pip3.7 install numpy metapy csv
```

### Searching

The main use case of this project is to search for a song and view the dashboard of metrics for that song. This project directory comes with a database pre-generated and a search script that allows you search this database. To search for a song titled "XYZ":

```bash
# open search script
python3.7 search.py

# enter song title/artist name
Search by Title/Artist: XYZ
```

### Song Dashboard Database Generation

This project also comes with a script (song_info_build.py) that utilizes the lyric analysis files to generate a song metric database. To use this script, you must have a valid song lyric file (containing song lyrics and metadata). For reference, see data/songs_lyrics.txt, the file must be in the same format. You may need to edit various pieces of this file, make sure to set the data_file to the location of your song lyric file. This may take some time to run (the topic generation is slow for lots of songs), you can either use smaller song databases or change the parameters in the topic model section. To use this file to generate song lyrics:

```bash
python3.7 song_info_build.py
```

### More Information

You can also directly interact with the lyric analysis files (word_stats.py, explicit_model.py, and topics_model.py) if you're interested in only some of the song metrics, or if you're interested in using the song metrics for other purposes. The song_info_build.py gives a good idea of how to use these to analyze lyrics. You can also refer to the documentation for each.


## Implementation

Below I'll give some information on the techniques used to generate each of the song metrics.

### Song Speed

This is number of words in the song divided by the length of the songs in seconds.

### Song Repetitiveness

This is the number of unique words in the song divided by the total number of words in the song.

### Song Explicitness Score

This assigns each song an explicitness score, where more explicit songs have higher values range (0-1).

This is done by taking songs that are known to be explicit (songs that contain at least one word from a list) and using them to create a large set of words. Songs that have highest similarity to this are considered more explicit. TF weighting is used.

The starting explicit words can be altered by changing the list in the model class below. Generally, adding more words to the explicit list (as long as they are reasonable) doesn't vary the model, and the same songs will have high explicit scores.

Scores are normalized to be in range 0-1.

### Song Topics

This assigns each song to topic(s) common in song lyrics.

The PLSA algorithm is used. Vanilla PLSA does not work well for this task. Since we are interested in certain topics that songs may be about, there are slight modifications to the vanilla PLSA to steer the algorithm towards topics.

This is done by defining pre-defining topics with words that you believe will be correlated. The PLSA algorithm then initializes topic models to start close to these distributions, and extra word counts are injected into the model during the M-step.


## Other Things to Know

### Scraping

The song data used in this project was scraped from https://www.billboard.com and from https://genius.com. There are two scraping files included which allow you to scrape these sites.

The Billboard scraper finds the X number of most recent songs that have been in the Billboard Hot 100. In the data used for this project, X=5000, this goes back to mid-2007. 

The Genius scraper goes through the songs file generated by the Billboard scraper and returns and saves lyrics (along with other data) to a file which can then be directly input to the song_info_build.py script. 






