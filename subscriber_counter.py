import urlparse
from bs4 import BeautifulSoup
import json
from scraper import Scraper
import re
import hashlib
import tweepy
import os
import pickle

class SubscriberCounter(Scraper):

    def __init__(self,url=None):
        super(SubscriberCounter, self).__init__()
        self.url = url
        self.cache = False

    def assign_subclass(self,url=None):
        if url is not None:
            self.url = url

        self.prepend_url_scheme()

        parse_result = urlparse.urlparse(self.url)
        mydomain = parse_result[1]

        # print parse_result

        subclass_for_domain = {}
        subclass_for_domain['facebook']  = FacebookLikesCounter
        subclass_for_domain['youtube']   = YoutubeSubscriberCounter
        subclass_for_domain['instagram'] = InstagramFollowerCounter
        subclass_for_domain['vine.co']   = VineFollowerCounter
        subclass_for_domain['twitter']   = TwitterFollowerCounter

        for domain in subclass_for_domain:
            if domain in mydomain:
                self.__class__ = subclass_for_domain[domain]
                return
        raise Exception('url does not match any known subclass')

    def prepend_url_scheme(self):
        if "://" not in self.url:
            self.url = "http://" + self.url

    def get_count(self):
        print "in sc class"

    def load_auth_from_file(self,filename):
        with open (filename, "r") as myfile:
            return myfile.readline().strip()


class FacebookLikesCounter(SubscriberCounter):
    base_url = 'http://api.facebook.com/restserver.php?method=links.getStats&format=json&urls='

    def __init__(self,url):
        super(FacebookLikesCounter, self).__init__(url)

    def get_count(self):
        filename = self.get_filename_from_url()
        # print "filename =",filename
        json_obj = self.make_request(self.base_url+self.url,'sc_fb_'+filename+'.json')
        results = json.loads(json_obj)[0]
        like_count = results['like_count']
        return like_count

    def get_filename_from_url(self):
        m = re.search('facebook.com/(.*)',self.url)
        if m:
            filename = m.group(1).replace('/','_').replace('?','')
            return filename
        else:
            return hashlib.sha224(self.url).hexdigest()[:16]

class YoutubeSubscriberCounter(SubscriberCounter):
    base_url = 'https://www.googleapis.com/youtube/v3/channels?part=id%2Csnippet%2Cstatistics%2CcontentDetails%2CtopicDetails&forUsername={0}&key={1}'

    def __init__(self,url):
        super(YoutubeSubscriberCounter, self).__init__(url)

    def get_count(self):
        api_key = self.load_auth_from_file('auth_youtube_api.txt')
        username = self.get_username_from_url(self.url)
        url = self.base_url.format(username,api_key)
        json_obj = self.make_request(url,'sc_yt_'+username+'.json')
        results = json.loads(json_obj)
        try:
            count = results['items'][0]['statistics']['subscriberCount']
            return count
        except Exception:
            return None

    def get_username_from_url(self,url):
        username = None
        m = re.search('/user/([^/^\?]+)',url)
        if m:
            username = m.group(1)
        else:
            username = hashlib.sha224(url).hexdigest()[:16]
        return username

class InstagramFollowerCounter(SubscriberCounter):

    def __init__(self,url):
        super(InstagramFollowerCounter, self).__init__(url)

    def get_count(self):
        # "followed_by":{"count":59220076},
        filename = self.get_filename_from_url()
        html = self.make_request(self.url, 'sc_ig_'+filename+'.htm')
        m = re.search(r'"followed_by":{"count":(\d+)}',html)
        if m:
            count = m.group(1)
            # print "matched:", count
            return count
        else:
            return None

    def get_filename_from_url(self):
        m = re.search('instagram.com/(.*)',self.url)
        if m:
            filename = m.group(1).replace('/','_')
            return filename
        else:
            return hashlib.sha224(self.url).hexdigest()[:16]

class VineFollowerCounter(SubscriberCounter):
    def __init__(self,url):
        super(VineFollowerCounter, self).__init__(url)

    def get_count(self):
        filename = self.get_filename_from_url()
        html = self.make_request(self.url, 'sc_vine_'+filename+'.htm')
        soup = BeautifulSoup(html, "lxml")
        followers_el = soup.find('li',class_='followers')
        if followers_el:
            count = followers_el.get_text(strip=True)
            count = count.replace(' followers','')
            return count
        # followers_el2 = soup #todo

    def get_filename_from_url(self):
        m = re.search('vine\.co/u/([^\/]+)',self.url)
        if m:
            filename = m.group(1).replace('/','_')
            return filename
        else:
            return hashlib.sha224(self.url).hexdigest()[:16]

class TwitterFollowerCounter(SubscriberCounter):
    def __init__(self,url):
        super(TwitterFollowerCounter, self).__init__(url)

    def get_count(self):
        self.load_auth_from_file('auth_twitter.txt')
        self.auth_twitter()
        username = self.get_username_from_url(self.url)
        if username is None:
            return None

        tweets = self.make_request(username)

        try:
            num_followers = tweets[0].author.followers_count
            return num_followers
        except Exception:
            return None

    def make_request(self,username):
        filename = 'sc_tw_'+username+'.pkl'
        output_path = self.cache_dir + filename
        if self.cache is True:
            if os.path.isfile(output_path):
                with open(output_path,'rb') as f:
                    return pickle.load(f)

        tweets = '-1'
        try:
            tweets = self.api.user_timeline(screen_name = username,count=0)
        except tweepy.error.TweepError:
            pass

        # print tweets[0].author.followers_count
        with open(output_path,'wb') as f:
            pickle.dump(tweets,f)
        print "saved to:",output_path
        return tweets

    def load_auth_from_file(self,filename):
        with open (filename, "r") as myfile:
            self.consumer_key = myfile.readline().strip()
            self.consumer_secret = myfile.readline().strip()
            self.access_key = myfile.readline().strip()
            self.access_secret = myfile.readline().strip()

    def auth_twitter(self):
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_key, self.access_secret)
        self.api = tweepy.API(self.auth)

    def get_username_from_url(self,url):
        username = None
        m = re.search('twitter\.com/([^\/^\?]+)/?',url)
        if m:
            username = m.group(1)
            # print username
            return username
        else:
            return hashlib.sha224(self.url).hexdigest()[:16]

if __name__ == "__main__":

    url = 'https://www.facebook.com/jerseydemic/'
    url = 'https://www.instagram.com/taylorswift'
    url = 'https://www.youtube.com/user/taylorswift'
    url = 'https://twitter.com/taylorswift13'
    sc = SubscriberCounter(url)
    sc.assign_subclass()
    print sc.get_count()

# have different subclasses for each
# cache requests
# youtube_subscriber_counter.py < subscriber_counter.py
# input: page url
# split url
# if domain matches, then handle in subclass
#  get page using reuqests
#  parse using bsoup
#  clean num
#  return num
