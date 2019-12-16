import sys
import numpy as np
import re
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options

# This script can be used to get song titles/artists from Billboards top-100 records.
# Give the number of songs (X) desired as input. This will return the X most recent songs.

NUMBER_OF_SONGS = 50

try:
    NUMBER_OF_SONGS = int(sys.argv[1])
except:
    pass


songs = set()

month = 11
year = 2019

while (len(songs) < NUMBER_OF_SONGS):
    url = f'https://www.billboard.com/charts/hot-100/{year}-{month:02d}-01'
    print(f'{len(songs):5} parsing  :  {url}')
    options = Options()
    options.headless = True
    browser = webdriver.Chrome('./chromedriver',options=options)
    browser.get(url)
    html = browser.execute_script('return document.body.innerHTML')
    soup = BeautifulSoup(html,'html.parser')
    htmlstr = str(soup)
    browser.quit()
    rows = soup.find_all('li', {'class' : 'chart-list__element display--flex'})
    for row in rows:
        title = row.find('span', {'class' : 'chart-element__information__song'}).text
        artist = row.find('span', {'class' : 'chart-element__information__artist'}).text
        songs.add((title, artist))
    year = year - (month==1)
    month = (month-2)%12+1

print(len(songs))

outfile = open('out.txt','w')
for song in songs:
    outfile.write(song[0] + ' || ' + song[1] + '\n')
outfile.close()
