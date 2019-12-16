import sys
import numpy as np
import re
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
import re 
import urllib
import atexit
import time

options = Options()
options.headless = True
browser = webdriver.Chrome('./chromedriver',options=options)
browser.set_page_load_timeout(15)

def close_browser():
    browser.quit()
atexit.register(close_browser)

def get_soup(url):
    browser.get(url)
    html = browser.execute_script('return document.body.innerHTML')
    soup = BeautifulSoup(html,'html.parser')
    return soup

def scrape_song_page(url):
    try:
        soup = get_soup(url)
        lyric_div = str(soup.find('div', {'class' : 'lyrics'}))
        lyrics = BeautifulSoup(re.sub('<br/>', ' ', lyric_div), 'html.parser').text
        lyrics = ' '.join(lyrics.split())
        lyrics = re.sub(r'\[[^]]*\]', '', lyrics)
        title = ' '.join(soup.find('h1').text.split())
        artist = ' '.join(soup.find('h2').text.split())
        featuring = ' '.join(soup.find('expandable-list', {'label' : 'Featuring'}).text.split())
        
        apple_links_id = re.findall('https://genius.com/songs/([0-9]*)/apple_music_player', str(soup))
        soup = get_soup(f'https://genius.com/songs/{apple_links_id[0]}/apple_music_player')
        length = float(re.findall('"duration":([0-9]+\.?[0-9]*),"country_codes"', str(soup))[0])

        return [title, artist, length, featuring, lyrics]
    except KeyboardInterrupt:
        quit()
    except :
        return False

def find_song_page(title, artist):
    search_url_prefix = 'https://genius.com/search?q='
    try:
        artist = artist.split(' Featuring ')[0].split(' With ')[0].replace(' & ', ' ').replace(', ', ' ').replace(' x ', ' ').replace(' + ', ' ')
        title = title.split(' (')[0]
        query_url = search_url_prefix+title+' '+artist
        soup = get_soup(query_url)
        href = soup.find_all('a', {'class', 'mini_card'})[1]['href']
        return href
    
    except KeyboardInterrupt:
        quit()
    except :
        return False



def scrape_songs_from_list(input_file):
    songs_added = set()
    songs_file = open(input_file, 'r')
    songs = []
    for line in songs_file.readlines():
        [title, artist] = line.strip().split(' || ')
        songs.append((title, artist))
    songs_file.close()
    outputsongs = []
    x = 0
    starttime = time.time()
    for title, artist in songs:
        x += 1
        song_url,i = False,0
        while not song_url and i < 5:
            song_url = find_song_page(title, artist)
            i += 1
        if not song_url:
            print(f'SONG NOT FOUND :   {title}   {artist}')
            continue
        
        song,i = False,0
        while  not song and i < 5:
            song = scrape_song_page(song_url)
            i += 1
        if not song:
            print(f'SONG PAGE CANNOT BE PARSED :   {title}   {artist}')
            continue
        if f'{song[0]} by {song[1]}' in songs_added:
            print(f'SONG ALREADY ADDED : {song[0]}  {song[1]}')
            continue
        songs_added.add(f'{song[0]} by {song[1]}')
        outputsong = f'#\n{song[0]}\n{song[1]}\n{song[2]}\n{song[3]}\n{song[4]}\n'
        outputsongs.append(outputsong)
        print(f'finished song {x} : {song[0]} by {song[1]}')
        if x%200==0:
            print(f'Rewriting to file. Time : {(time.time()-starttime)/60} minutes')
            f = open('songs_lyrics.txt','w')
            f.write('\n'.join(outputsongs))
            f.close()
    f = open('songs_lyrics.txt','w')
    f.write('\n'.join(outputsongs))
    f.close()

scrape_songs_from_list(sys.argv[1])
