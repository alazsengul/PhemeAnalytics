#https://www.nytimes.com/2018/05/12/sunday-review/when-spies-hack-journalism.html
#https://www.nytimes.com/2018/05/29/us/eric-greitens-resigns.html
#https://www.nytimes.com/2018/06/07/us/politics/house-immigration-showdown.html

import requests
import numpy as np
import newspaper
import nltk
import re
import inflect
import os
import time
from selenium import webdriver
from datetime import datetime
from unidecode import unidecode
from newspaper import Article
from selenium.webdriver.common.keys import Keys
from newsapi import NewsApiClient
import webbrowser
import pickle

#######
class Particle(object):

    def __init__(self, text, comments):
        self.text = text
        self.comments = comments

        self.raw = raw_text(self.text)
        self.word_text = word_tokenize(self.raw)
        self.sent_text = sent_tokenize(self.raw)
        self.sylla = sylco(self.raw)

    def clean_text(self):
        punctuations = '!()-[]}{;—:"\,<>./?@#$%^&*_~'
        punctuation_text = []
        string_text = self.raw
        string_text = string_text.lower()
        string_text = ' '.join(string_text.split())
        for character in string_text:
            if character not in punctuations:
                punctuation_text.append(character)
        final_text = ''.join(punctuation_text)
        final_text = ''.join(i for i in final_text if not i.isdigit())
        return(final_text)

    def char_count(self):
        return(len("".join(self.word_text)))

    def word_count(self):
        return(len((self.raw).split()))

    def sent_count(self):
        return(len(self.sent_text))

    def coleman_liau(self):
        sents = self.sent_count()
        words = self.word_count()
        chars = self.char_count()

        l_var = (chars / words) * 100
        s_var = (sents / words) * 100

        formula_index = (0.0588 * l_var) - (0.296 * s_var) - 15.8
        return(round(formula_index, 2))

    def automated_readibility(self):
        sents = self.sent_count()
        words = self.word_count()
        chars = self.char_count()

        formula_index = (4.71 * (chars / words)) + (0.5 * (words / sents)) - 21.43
        return(round(formula_index, 2))

    def flesch_kincaid(self):
        sents = self.sent_count()
        words = self.word_count()
        chars = self.char_count()
        sylla = self.sylla

        formula_index = 206.835 - 1.015 * (words/sents) - 84.6 * (sylla/words)
        return(round(formula_index, 2))

    def gunning_fog(self):
        complex_count = 0
        raw_loop = (self.clean_text()).split()
        for word in raw_loop:
            if sylco(word) >= 3:
                complex_count += 1

        sents = self.sent_count()
        words = self.word_count()

        formula_index = 0.4 * ((words/sents) + (100 * (complex_count/words)))
        return(round(formula_index, 2))

    def dale_chall(self):
        p = inflect.engine()

        with open('dale_chall.txt', 'r') as myfile:
            raw_list = myfile.read().replace('\n', '')
        common_list = raw_text(raw_list).split()
        complex_count = 0
        raw_loop = (self.clean_text()).split()

        for word in raw_loop:
            if (word not in common_list) and (p.singular_noun(word) not in common_list):
                complex_count += 1

        sents = self.sent_count()
        words = self.word_count()

        if (complex_count/words) > 0.05:
            formula_index = 3.6365 + (0.1579 * ((complex_count/words) * 100) + 0.0496 * (words/sents))
        else:
            formula_index = 0.1579 * ((complex_count/words) * 100) + 0.0496 * (words/sents)

        return(round(formula_index, 2))

    def reading_time(self):
        time = ((self.word_count()) / 275) * 60
        return(time)

    def difficulty_score(self):
        article_score = alma_score(self.coleman_liau(), self.automated_readibility(), self.flesch_kincaid(), self.gunning_fog(), self.dale_chall())
        return(article_score)
class Commentator(object):
    def __init__(self, text, name, location, upvotes, starred):
        self.text = text
        self.name = name
        self.location = location
        self.upvotes = upvotes
        self.starred = starred
#######
def extract_article(url):
    raw_article = Article(url, language = "en")
    raw_article.download()
    raw_article.parse()
    article_text = raw_article.text
    article_text = article_text.strip()
    return(article_text)
def clean_text(text):
    punctuations = '!()-[]}{;—:"\,<>./?@#$%^&*_~'
    punctuation_text = []
    string_text = text
    string_text = string_text.lower()
    string_text = ' '.join(string_text.split())
    for character in string_text:
        if character not in punctuations:
            punctuation_text.append(character)
    final_text = ''.join(punctuation_text)
    final_text = ''.join(i for i in final_text if not i.isdigit())
    return(final_text)
def raw_text(original_text):
    text = unidecode(original_text)
    punctuations = '!()-[]}{;:"\,<>/?@#$%^&*_~'
    punctuation_text = []

    string_text = text.lower()
    string_text = ' '.join(string_text.split())

    for character in string_text:
        if character not in punctuations:
            punctuation_text.append(character)
    final_text = ''.join(punctuation_text)

    final_text = ''.join(i for i in final_text if not i.isdigit())

    sentences = sent_tokenize(final_text)

    final_text = ' '.join(sentences)

    return(final_text)
def word_tokenize(raw_text):
    word_tokens = nltk.word_tokenize(raw_text)

    word_list = []
    for word in word_tokens:
        word_list.append(word)

    return(word_list)
def sent_tokenize(raw_text):
    sent_tokens = nltk.sent_tokenize(raw_text)

    sent_list = []
    for sentence in sent_tokens:
        sent_list.append(sentence)

    return(sent_list)
def sylco(word) :

    word = word.lower()

    # exception_add are words that need extra syllables
    # exception_del are words that need less syllables

    exception_add = ['serious','crucial']
    exception_del = ['fortunately','unfortunately']

    co_one = ['cool','coach','coat','coal','count','coin','coarse','coup','coif','cook','coign','coiffe','coof','court']
    co_two = ['coapt','coed','coinci']

    pre_one = ['preach']

    syls = 0 #added syllable number
    disc = 0 #discarded syllable number

    #1) if letters < 3 : return 1
    if len(word) <= 3 :
        syls = 1
        return syls

    #2) if doesn't end with "ted" or "tes" or "ses" or "ied" or "ies", discard "es" and "ed" at the end.
    # if it has only 1 vowel or 1 set of consecutive vowels, discard. (like "speed", "fled" etc.)

    if word[-2:] == "es" or word[-2:] == "ed" :
        doubleAndtripple_1 = len(re.findall(r'[eaoui][eaoui]',word))
        if doubleAndtripple_1 > 1 or len(re.findall(r'[eaoui][^eaoui]',word)) > 1 :
            if word[-3:] == "ted" or word[-3:] == "tes" or word[-3:] == "ses" or word[-3:] == "ied" or word[-3:] == "ies" :
                pass
            else :
                disc+=1

    #3) discard trailing "e", except where ending is "le"

    le_except = ['whole','mobile','pole','male','female','hale','pale','tale','sale','aisle','whale','while']

    if word[-1:] == "e" :
        if word[-2:] == "le" and word not in le_except :
            pass

        else :
            disc+=1

    #4) check if consecutive vowels exists, triplets or pairs, count them as one.

    doubleAndtripple = len(re.findall(r'[eaoui][eaoui]',word))
    tripple = len(re.findall(r'[eaoui][eaoui][eaoui]',word))
    disc+=doubleAndtripple + tripple

    #5) count remaining vowels in word.
    numVowels = len(re.findall(r'[eaoui]',word))

    #6) add one if starts with "mc"
    if word[:2] == "mc" :
        syls+=1

    #7) add one if ends with "y" but is not surrouned by vowel
    if word[-1:] == "y" and word[-2] not in "aeoui" :
        syls +=1

    #8) add one if "y" is surrounded by non-vowels and is not in the last word.

    for i,j in enumerate(word) :
        if j == "y" :
            if (i != 0) and (i != len(word)-1) :
                if word[i-1] not in "aeoui" and word[i+1] not in "aeoui" :
                    syls+=1

    #9) if starts with "tri-" or "bi-" and is followed by a vowel, add one.

    if word[:3] == "tri" and word[3] in "aeoui" :
        syls+=1

    if word[:2] == "bi" and word[2] in "aeoui" :
        syls+=1

    #10) if ends with "-ian", should be counted as two syllables, except for "-tian" and "-cian"

    if word[-3:] == "ian" :
    #and (word[-4:] != "cian" or word[-4:] != "tian") :
        if word[-4:] == "cian" or word[-4:] == "tian" :
            pass
        else :
            syls+=1

    #11) if starts with "co-" and is followed by a vowel, check if exists in the double syllable dictionary, if not, check if in single dictionary and act accordingly.

    if word[:2] == "co" and word[2] in 'eaoui' :

        if word[:4] in co_two or word[:5] in co_two or word[:6] in co_two :
            syls+=1
        elif word[:4] in co_one or word[:5] in co_one or word[:6] in co_one :
            pass
        else :
            syls+=1

    #12) if starts with "pre-" and is followed by a vowel, check if exists in the double syllable dictionary, if not, check if in single dictionary and act accordingly.

    if word[:3] == "pre" and word[3] in 'eaoui' :
        if word[:6] in pre_one :
            pass
        else :
            syls+=1

    #13) check for "-n't" and cross match with dictionary to add syllable.

    negative = ["doesn't", "isn't", "shouldn't", "couldn't","wouldn't"]

    if word[-3:] == "n't" :
        if word in negative :
            syls+=1
        else :
            pass

    #14) Handling the exceptional words.

    if word in exception_del :
        disc+=1

    if word in exception_add :
        syls+=1

    # calculate the output
    return(numVowels - disc + syls)
#######
def coleman_score(score):
    if score >= 17:
        return(17)
    elif score < 6:
        return(5)
    else:
        return(score)
def automated_score(score):
    if score < 7:
        return(5)
    elif ((score >= 7) and (score < 8)):
        return(6 + (score - 7))
    elif ((score >= 8) and (score < 9)):
        return(7 + (score - 8))
    elif ((score >= 9) and (score < 10)):
        return(8 + (score - 9))
    elif ((score >= 10) and (score < 11)):
        return(9 + (score - 10))
    elif ((score >= 11) and (score < 12)):
        return(10 + (score - 11))
    elif ((score >= 12) and (score < 13)):
        return(11 + (score - 12))
    elif ((score >= 13) and (score < 14)):
        return(12 + (score - 13))
def flesch_score(score):
    if score > 90:
        return(5)
    elif ((score > 80) and (score <= 90)):
        return(6 + ((90 - score) / 10))
    elif ((score > 70) and (score <= 80)):
        return(7 + ((80 - score) / 10))
    elif ((score > 65) and (score <= 70)):
        return(8 + ((70 - score) / 5))
    elif ((score > 60) and (score <= 65)):
        return(9 + ((65 - score) / 5))
    elif ((score > (56 + (2/3))) and (score <= 60)):
        return(10 + ((60 - score) / (10/3)))
    elif ((score > (53 + (1/3))) and (score <= (56 + (2/3)))):
        return(11 + (((56 + (2/3)) - score) / (10/3)))
    elif ((score > 50) and (score <= (53 + (1/3)))):
        return(12 + (((53 + (1/3))) - score) / (10/3))
    elif ((score > 45) and (score <= 50)):
        return(13 + ((50 - score) / 5))
    elif ((score > 40) and (score <= 45)):
        return(14 + ((45 - score) / 5))
    elif ((score > 35) and (score <= 40)):
        return(15 + ((40 - score) / 5))
    elif ((score > 30) and (score <= 35)):
        return(16 + ((35 - score) / 5))
    elif (score < 30):
        return(17)
def gunning_score(score):
    if score >= 17:
        return(17)
    elif score < 6:
        return(5)
    else:
        return(score)
def dale_score(score):
    if score < 5.5:
        return(5)
    elif ((score >= 5.5) and (score < 6)):
        return(6 + ((score - 5.5) / 0.5))
    elif ((score >= 6) and (score < 6.5)):
        return(7 + ((score - 6) / 0.5))
    elif ((score >= 6.5) and (score < 7)):
        return(8 + ((score - 6.5) / 0.5))
    elif ((score >= 7) and (score < 7.5)):
        return(9 + ((score - 7) / 0.5))
    elif ((score >= 7.5) and (score < 8)):
        return(10 + ((score - 7.5) / 0.5))
    elif ((score >= 8) and (score < 8.5)):
        return(11 + ((score - 8) / 0.5))
    elif ((score >= 8.5) and (score < 9)):
        return(12 + ((score - 8.5) / 0.5))
    elif ((score >= 9) and (score < 9.25)):
        return(13 + ((score - 9) / 0.25))
    elif ((score >= 9.25) and (score < 9.5)):
        return(14 + ((score - 9.25) / 0.25))
    elif ((score >= 9.5) and (score < 9.75)):
        return(15 + ((score - 9.5) / 0.25))
    elif ((score >= 9.75) and (score < 10)):
        return(16 + ((score - 9.75) / 0.25))
    elif score >= 10:
        return(17)
def alma_score(coleman, automated, flesch, gunning, dale):
    if automated >= 14:
        final_score = (coleman_score(coleman) + flesch_score(flesch) + gunning_score(gunning) + dale_score(dale)) / 4
    else:
        final_score = (coleman_score(coleman) + automated_score(automated) + flesch_score(flesch) + gunning_score(gunning) + dale_score(dale)) / 5
    return(final_score)
#######
def location_details(json_id):
    #api_key = "AIzaSyBq_d-g7U6qL5QnIIUFR8Srl3NXpz_riho"
    api_key = "AIzaSyANfCMgsxe_p9zy26Y7TMfD6zeSdXRKR14"
    api_request = requests.get("https://maps.googleapis.com/maps/api/place/details/json?placeid=" + json_id + "&key=" + api_key)
    details_json = api_request.json()

    address_components = details_json["result"]["address_components"]

    lat_lng = (details_json["result"]["geometry"]["location"]["lat"], details_json["result"]["geometry"]["location"]["lng"])

    for segment in address_components:
        if (segment["types"][0] == "administrative_area_level_1"):
            state_string = segment["short_name"]

    # if a city
    if (address_components[0]["types"][0] == "locality"):
        city_string = address_components[0]["long_name"]
        complete_string = city_string + ", " + state_string
        return(("city", complete_string, lat_lng))
    # if a state
    elif (address_components[0]["types"][0] == "administrative_area_level_1"):
        complete_string = state_string
        return(("state", complete_string, lat_lng))
    # if something like brooklyn
    else:
        something_else = address_components[0]["long_name"]
        complete_string = something_else + ", " + state_string
        return(("other", complete_string, lat_lng))
def google_location(user_location):
    api_key = "AIzaSyANfCMgsxe_p9zy26Y7TMfD6zeSdXRKR14"
    user_location = user_location.replace(" ", "_")

    api_request = requests.get("https://maps.googleapis.com/maps/api/place/autocomplete/json?input=" + user_location + "&location=37.0902,95.7129&radius=8000&components=country:us&key=" + api_key)
    location_json = api_request.json()

    json_id = location_json["predictions"][0]["place_id"]
    location_tuple = location_details(json_id)

    return(location_tuple)
def mapbox_static(commentators):
    location_list = []
    for commentator in commentators:
        location_list.append((commentator.location)[2])

    url_mapbox = "https://api.mapbox.com/styles/v1/alazsengul/cjig5s5ux3udn2so9k44qdfwj/static/"
    #pin-s+000(-122.46589,37.77343),pin-s+000(-122.42816,37.75965)/auto/1200x1200@2x?access_token=pk.eyJ1IjoiYWxhenNlbmd1bCIsImEiOiJjamlnMmlwbmwxMzdqM2twZW96em92anh2In0.2aPtYBsFGbMNA1wAp9V0wQ"

    for tuple in location_list:
        try:
            substring = "pin-s+000(" + str(tuple[1]) + "," + str(tuple[0]) + "),"
        except:
            substring = ""
        url_mapbox += substring
    url_mapbox = (url_mapbox[:(len(url_mapbox) - 1)]) + "/auto/1200x1200@2x?access_token=pk.eyJ1IjoiYWxhenNlbmd1bCIsImEiOiJjamlnMmlwbmwxMzdqM2twZW96em92anh2In0.2aPtYBsFGbMNA1wAp9V0wQ"

    webbrowser.open(url_mapbox)
#######
def comment_driver(inputted_url):
    all_commentators = []

    chromedriver = "/Users/alazsengul/Desktop/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)

    driver.get(inputted_url)

    time.sleep(1)

    try:
        #time.sleep(1)
        button0 = driver.find_element_by_xpath('//*[@id="comments-speech-bubble-top"]')
        button0.click()
    except:
        try:
            #time.sleep(1)
            driver.execute_script("window.scrollTo(0, 1200);")
            button0 = driver.find_element_by_xpath('//*[@id="comments-speech-bubble-top"]')
            button0.click()
        except:
            button_exit_ad = driver.find_element_by_class_name("css-1tfvto9")
            button_exit_ad.click()
            driver.execute_script("window.scrollTo(0, 1200);")
            button0 = driver.find_element_by_xpath('//*[@id="comments-speech-bubble-top"]')
            button0.click()

    tried_or_not = False

    try:
        # click on "All" within comments panel
        #time.sleep(1)
        initial_focus = driver.find_element_by_class_name('CommentsPanel-wrapper--1ZpaW')
        initial_focus.click()

        time.sleep(1)
        button2 = driver.find_element_by_class_name('Tabs-nav--1EAdz')
        button2_li_tags = button2.find_elements_by_tag_name('li')
        for li_tag in button2_li_tags:
            if (li_tag.text == "All"):
                li_tag.click()

        time.sleep(1)
        button3_found = True
        count = 0
        # keep clicking / scrolling for all the comment pages
        while (button3_found == True):
            print("Downloading comment page " + str(count) + "...")
            try:
                #focus_button = driver.find_element_by_class_name('Header-title--JcUSD')
                elementToFocus = driver.find_element_by_class_name("Header-title--JcUSD")
                #focus_button.click()
                driver.execute_script("arguments[0].focus();", elementToFocus)
                #driver.find_element_by_class_name('Header-title--JcUSD').send_keys(Keys.END)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)
                button3 = driver.find_element_by_class_name('CommentList-viewMore--2BjZl')
                time.sleep(0.5)
                button3.click()
            except:
                print("Scrolling done...")
                button3_found = False;
            count += 1
        all_spans = driver.find_elements_by_class_name('Comment-comment--3eRct')
        for span in all_spans:
            full_text = span.text
            # date
            full_text_split = full_text.split()
            for word in full_text_split:
                if word == "commented":
                    commented_index = full_text_split.index("commented")
                    date = full_text_split[(commented_index + 1)] + " " + full_text_split[(commented_index + 2)]
                    continue

            location_string = (span.find_element_by_class_name("Comment-subtitle--NzC2q")).text
            location_string = location_string.split(date)[0]
            # method i got from online
            try:
                i = [x.isdigit() for x in location_string].index(True)
                location_string = location_string[:i]
            except:
                pass
            print(location_string)
            # location auto-complete
            try:
                location = google_location(location_string)
            except:
                location = location_string
            name = (span.find_element_by_class_name('UserHeader-title--234hb')).text
            text = (span.find_element_by_class_name('Comment-commentText--1826c')).text
            try:
                #string_upvotes = full_text.split("\n")[(len(full_text.split("\n"))) - 1]
                #string_upvotes = string_upvotes[5:]
                #upvotes = int(string_upvotes.split()[0])
                string_upvotes = span.find_element_by_class_name('TextButton-secondary--2if1R').text
                upvotes = int(string_upvotes.split()[0])
            except:
                upvotes = 0
            if "Times Pick" in full_text.split("\n"):
                starred = True
            else:
                starred = False
            all_commentators.append(Commentator(text=text, name=name, location=location, upvotes=upvotes, starred=starred))
        tried_or_not = True
    except:
        print("There are no comments for this article.")
    if (tried_or_not):
        print("Done extracting article comments!")

    time.sleep(1)
    #driver.quit()
    return(all_commentators)
#######
def get_extracts():
    newsapi = NewsApiClient(api_key="6c75d0ad1c97410fae7c974c87a5b2f6")
    top_headlines = newsapi.get_top_headlines(sources = "the-new-york-times", language = "en")
    return(top_headlines)
def get_urls(all_articles):
    all_urls = []

    for article in all_articles["articles"]:
        all_urls.append(article["url"])
    return(all_urls)
#######
def save_pickles(pickles_list):
    pickle.dump(pickles_list, open("commentators.p", "wb"))
#######
if __name__ == "__main__":

    mode = int(input("URL [0] or Newspaper [1]? "))

    if (mode == 0):
        url = input("Input URL: ")
        get_commentators = comment_driver(url)
        text = extract_article(url)

        """
        for person in get_commentators:
            print(person.name)
            print(person.text)
            print(person.location)
            print(person.upvotes)
            print(person.starred)
            print("================")
        """

        #for person in get_commentators:
        #    yourParticle = Particle(text, person.text)

        #mapbox_static(get_commentators)

        save_pickles(get_commentators)
    else:
        all_articles = []
        all_extracts = get_extracts()
        all_urls = get_urls(all_extracts)

        for url in all_urls:
            get_comments = comment_driver(url)
            text = extract_article(url)
            all_articles.append(Particle(text, get_comments))
