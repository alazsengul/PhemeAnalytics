# there's a bug... when i look up 'call+out+my+name+the+weekend+topic' the soup is different

from __future__ import unicode_literals
import youtube_dl

import urllib.request
from urllib.parse import quote
from bs4 import BeautifulSoup

def bes_download(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist':True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def bes_link(url):
    pass
def youtube_topic(song_name, artist_name):
    # this try/except flow is to superficially work out bug
    try:
        search_text = song_name + " " + artist_name + " topic"
        search_query = quote(search_text)
        url = "https://www.youtube.com/results?search_query=" + search_query
        html = urllib.request.urlopen(url)
        soup = BeautifulSoup(html, "lxml")
        for url_result in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
            if (not url_result['href'].startswith("https://googleads.g.doubleclick.net/")) and ("list" not in url_result['href']):
                top_result = 'https://www.youtube.com' + url_result['href']
                break
        return(top_result)

    except:
        search_text = song_name + " topic"
        search_query = quote(search_text)
        url = "https://www.youtube.com/results?search_query=" + search_query
        html = urllib.request.urlopen(url)
        soup = BeautifulSoup(html, "lxml")
        for url_result in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
            if not url_result['href'].startswith("https://googleads.g.doubleclick.net/"):
                top_result = 'https://www.youtube.com' + url_result['href']
                break
        return(top_result)

if __name__ == '__main__':

    song_name = input("Name of SONG: ")
    artist_name = input("Name of ARTIST: ")

    top_result = youtube_topic(song_name, artist_name)

    bes_download(top_result)
