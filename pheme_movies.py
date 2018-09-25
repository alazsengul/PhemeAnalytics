# "Annihilation" trailer — https://www.youtube.com/watch?v=89OP78l9oF0
# YouTube API key — AIzaSyANfCMgsxe_p9zy26Y7TMfD6zeSdXRKR14

import os # for youtubeDriver()
import time # for youtubeDriver()
from selenium import webdriver # for youtubeDriver()
from selenium.webdriver.common.keys import Keys # for youtubeDriver()
import requests # for youtubeAPI()
from textblob import TextBlob # for sentiment analysis
import re # for cleaning up text
import sys # for text-based progress bar
from collections import Counter # for atomSubsAnalysis()
import operator # for atomSubsAnalysis()

class Particle(object):
    def __init__(self, id, author, text, likes, subscriptions, subparticles):
        self.id = id
        self.author = author
        self.text = text
        self.likes = likes
        self.subscriptions = subscriptions
        self.subparticles = subparticles

    def sentimentAnalysis(self):
        analysis = TextBlob(self.text)
        # set sentiment
        if (analysis.sentiment.polarity > 0):
            return(str(analysis.sentiment.polarity) + ' positive')
        elif (analysis.sentiment.polarity == 0):
            return(str(analysis.sentiment.polarity) + ' neutral')
        else:
            return(str(analysis.sentiment.polarity) + ' negative')

class SubParticle(object):
    def __init__(self, id, author, text, likes, subscriptions):
        self.id = id
        self.author = author
        self.text = text
        self.likes = likes
        self.subscriptions = subscriptions

    def sentimentAnalysis(self):
        analysis = TextBlob(self.text)
        # set sentiment
        if (analysis.sentiment.polarity > 0):
            return(str(analysis.sentiment.polarity) + ' positive')
        elif (analysis.sentiment.polarity == 0):
            return(str(analysis.sentiment.polarity) + ' neutral')
        else:
            return(str(analysis.sentiment.polarity) + ' negative')

def cleanText(dirty_text):
    # utility function to clean text by removing links, special characters using regex statements
    return(' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", dirty_text).split()))

def likesStrToInt(raw_string):
    # accounts for '1K', '1.7K', etc...
    if "K" in raw_string:
        decimal = float(raw_string.split("K")[0])
        return(int(decimal * 1000))
    elif (raw_string == ""):
        return(0)
    else:
        return(int(raw_string))

def getChannelId(url_text):
    # uses the youtube api to find the channel id from the split url text (either username or id)
    channel_type = url_text.split("https://www.youtube.com/")[1].split("/")[0]
    split_text = url_text.split("https://www.youtube.com/")[1].split("/")[1]

    # id
    if (channel_type == "channel"):
        return(split_text) # the 'split_text' is the id...
    # username
    elif (channel_type == "user"):
        api_key = '' # NEED KEY FOR IT TO WORK
        find_id = 'https://www.googleapis.com/youtube/v3/channels?key=' + api_key + '&forUsername=' + split_text + '&part=id'
        url_request = requests.get(find_id)
        request_json = url_request.json()
        channel_id = request_json["items"][0]["id"]
        return(channel_id)
    # void
    else:
        return("split_text")

def channelSubs(id):
    # uses the youtube api: https://developers.google.com/youtube/v3/docs/subscriptions/list
    # first try with a channel_string that is hopefully an id and not a username
    try:
        api_key = '' # NEED KEY FOR IT TO WORK
        http_url = 'https://www.googleapis.com/youtube/v3/subscriptions?part=snippet&channelId=' + id + '&maxResults=50&key=' + api_key
        url_request = requests.get(http_url)
        request_json = url_request.json()
        # handle the json and return a list of channels subscribed to
        channels_subbed_to = []
        for dictionary in request_json["items"]:
            channels_subbed_to.append(dictionary["snippet"]["title"])
        return(channels_subbed_to)
    except:
        return("void")

def youtubeDriver(video_url):
    print("\033c")

    # set up chrome driver and actions functionality
    chromedriver = "/Users/alazsengul/Desktop/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)

    # load webpage
    driver.get(video_url)
    time.sleep(2)

    # click on pop-up 'no thanks'... this is necessary for focusing the scrolling as well
    driver.find_element_by_css_selector('.style-scope.ytd-button-renderer.style-text').click()

    # pause video
    action1 = webdriver.ActionChains(driver)
    action1.send_keys("k")
    action1.perform()

    # scroll a bit down to load comments
    driver.execute_script("window.scrollTo(0, 500);")
    time.sleep(2)

    # scroll through four (the current page plus three additional) comment pages... this leads to a total 80 comments (20 per page)
    user_choice_scroll = int(input("How many pages should I scroll through? "))

    action2 = webdriver.ActionChains(driver)
    for loop in range(user_choice_scroll - 1):
        action2.send_keys(Keys.END)
        action2.perform()
        print("Scrolling through comment page " + str(loop + 1))
        time.sleep(2)
    print("\033c")

    # open all 'show reply' / 'show all replies' buttons
    replies_webelements = driver.find_elements_by_id('replies')

    len_count_replies = len(replies_webelements)
    count_replies = 1

    for webelement in replies_webelements:
        sys.stdout.write("\r" + "Loading... " + str(count_replies) + "/" + str(len_count_replies))
        sys.stdout.flush()
        try:
            webelement.find_element_by_css_selector('.more-button.style-scope.ytd-comment-replies-renderer').click()
            time.sleep(0.1)
        except:
            pass
        count_replies += 1
    print("\033c")

    # finds comment elements... nested within other webelements
    comments_list = driver.find_element_by_id('comments').find_element_by_id('contents').find_elements_by_css_selector('.style-scope.ytd-item-section-renderer')

    len_count_comments = len(comments_list)
    count_comments = 1
    len_count_sub = 1
    count_sub = 1

    # adds on particles as object to a list... IMPORTANT: this is where particles are made/added on to list
    particles_list = []
    for comment in comments_list:
        sys.stdout.write("\r" + str(count_comments) + " out of " + str(len_count_comments) + " comments are being downloaded...")
        sys.stdout.flush()

        parent = comment.find_element_by_id('comment')

        author = parent.find_element_by_id('author-text').text
        # url string can get both id and subscriptions
        url_string = parent.find_element_by_id('author-text').get_attribute('href')
        id = getChannelId(url_string)
        subscriptions = channelSubs(id)

        text = parent.find_element_by_id('content-text').text
        likes = likesStrToInt(parent.find_element_by_id('vote-count-middle').text)

        try:
            children = comment.find_element_by_id('replies').find_element_by_id('loaded-replies').find_elements_by_css_selector('.style-scope.ytd-comment-replies-renderer')
            len_count_sub = len(children)

            subparticles_list = []
            for child in children:
                sys.stdout.write("\r" + str(count_comments) + " out of " + str(len_count_comments) + " comments are being downloaded... replies that are loading: (" + str(count_sub) + "/" + str(len_count_sub) + ")")
                sys.stdout.flush()

                c_author = child.find_element_by_id('author-text').text
                # url string can get both id and subscriptions
                c_url_string = child.find_element_by_id('author-text').get_attribute('href')
                c_id = getChannelId(c_url_string)
                c_subscriptions = channelSubs(c_id)

                c_text = child.find_element_by_id('content-text').text
                c_likes = likesStrToInt(child.find_element_by_id('vote-count-middle').text)

                subparticles_list.append(SubParticle(c_id, c_author, c_text, c_likes, c_subscriptions))
                count_sub += 1
        except:
            subparticles_list = []

        particles_list.append(Particle(id, author, text, likes, subscriptions, subparticles_list))

        len_count_sub = 1
        count_sub = 1
        count_comments += 1
        print("\033c")
    print("\033c")


    # quit browser / driver
    driver.quit()

    return(particles_list)

def atomSentimentAnalysis(particles):
    # perform ratio analysis
    pos_count = 0
    neg_count = 0

    method = input("What algorithm would you like to use? ")

    if (method == "1"):
        for particle in particles:
            # gets the number of the string returned by '.sentimentAnalysis()'
            sentiment_score = float(particle.sentimentAnalysis().split()[0])
            if (sentiment_score > 0):
                pos_count += 1
            elif (sentiment_score < 0):
                neg_count += 1
        return(pos_count/(pos_count + neg_count))

    if (method == "2"):
        for particle in particles:
            # gets the number of the string returned by '.sentimentAnalysis()'
            sentiment_score = float(particle.sentimentAnalysis().split()[0])
            if (sentiment_score > 0):
                pos_count += sentiment_score
            elif (sentiment_score < 0):
                neg_count += (sentiment_score * -1)
        return(pos_count/(pos_count + neg_count))

    if (method == "3"):
        for particle in particles:
            particle_sentiment = float(particle.sentimentAnalysis().split()[0])
            if (particle_sentiment > 0):
                pos_count += particle_sentiment
            elif (particle_sentiment < 0):
                neg_count += (particle_sentiment * -1)

            for subparticle in particle.subparticles:
                subparticle_sentiment = float(subparticle.sentimentAnalysis().split()[0])
                if (subparticle_sentiment > 0):
                    pos_count += subparticle_sentiment
                elif (subparticle_sentiment < 0):
                    neg_count += (subparticle_sentiment * -1)

        return(pos_count/(pos_count + neg_count))

def atomSubsAnalysis(particles):
    # check to see similar subs
    subs_list = []
    # make sure there aren't any duplicates
    id_list = []
    # outer for-loop for particle
    for particle in particles:
        # duplicate check
        if (particle.id not in id_list):
            id_list.append(particle.id)

            subscriptions = particle.subscriptions
            if (subscriptions != "void"):
                for sub in subscriptions:
                    subs_list.append(sub)

            # inner for-loop for subparticle
            for subparticle in particle.subparticles:
                # duplicate check
                if (subparticle.id not in id_list):
                    id_list.append(subparticle.id)

                    subscriptions = subparticle.subscriptions
                    if (subscriptions != "void"):
                        for sub in subscriptions:
                            subs_list.append(sub)
                else:
                    pass
        else:
            pass

    # count repeated elements
    subs_count = dict(Counter(subs_list))
    sorted_subs = sorted(subs_count.items(), key=operator.itemgetter(1))
    sorted_subs.reverse()
    print(len(id_list))
    return(sorted_subs)

if __name__ == '__main__':
    video_url = input("Enter URL: ")
    particles = youtubeDriver(video_url)
    # score = atomSentimentAnalysis(particles)
    # subs = atomSubsAnalysis(particles)
