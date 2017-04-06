from bing_api import BingAPI
import urlparse
import re

class BingParser():

    def __init__(self,path=None):
        self.path = path # json results file
        self.load_original_domains()
        self.load_extended_domains()

        self.results_list = []

        self.paths_for_domain = {}
        self.urls_for_domain = {}
        self.results_domains_set = ()

    def load_results_from_file(self):
        self.b = BingAPI()
        self.b.load_results_from_file_path(self.path)
        self.results_list = self.b.results_list        

    def run(self):
        self.add_results_to_paths_for_domain_dict()
        self.results_domains_set = set(self.paths_for_domain.keys())
        self.original_matches = self.get_intersection(self.results_domains_set, self.original_domains)
        self.extended_matches = self.get_intersection(self.results_domains_set, self.extended_domains)

        print 'original', self.original_matches

    def return_filtered_path_if_profile_url(self,netloc,path,url):
        
        if netloc in self.original_domains:
            print url.encode('utf-8')
        
        if netloc == 'youtube.com':
            m = re.search('youtube\.com/user/([^/\?]+)',url)
            if m:
                return m.group(1)
        elif netloc == 'twitter.com':
            m = re.search('twitter\.com/([^/\?]+)',url)
            if m:
                return m.group(1)
        elif netloc == 'facebook.com':
            m = re.search('facebook\.com/([^/\?]+)',url)
            if m:
                return m.group(1)
        elif netloc == 'vine.co':
            m = re.search('vine\.co/(v|tags)/',url) # vine url
            if m:
                return False
            m = re.search('vine\.co/u/([^/\?]+)',url) # user number url
            if m:
                return m.group(1)
            m = re.search('vine\.co/([^/\?]+)',url) # user name url
            if m:
                return m.group(1)
        elif netloc == 'instagram':
            m = re.search('instagram\.com/([^/\?]+)',url)
            if m:
                return m.group(1)

        if netloc in self.original_domains:
            return False

        if netloc in self.extended_domains:
            return True

        return False

    def get_intersection(self,s,t):
        intersection = s.intersection(t)
        return intersection

    def load_original_domains(self):
        self.original_domains = set([
            "youtube.com",
            "twitter.com",
            "facebook.com",
            "vine.co",
            "instagram.com"
        ])

    def load_extended_domains(self):
        self.extended_domains = set([
            "pinterest.com",
            "imdb.com",
            "twitch.tv",
            "snapchat.com",
            "periscope.tv"
        ])

    def add_results_to_paths_for_domain_dict(self):
        for result in self.results_list:
            url = result["Url"]
            netloc, path = self.split_url(url)
            netloc = netloc.replace('www.','')
            
            path = self.return_filtered_path_if_profile_url(netloc,path,url)
            if path:
                self.add_path_to_dict(netloc,path)
                self.add_url_to_dict(netloc,url)

    def add_path_to_dict(self,netloc,path):
        if netloc in self.paths_for_domain:
            self.paths_for_domain[netloc] += [path]
        else:
            self.paths_for_domain[netloc] = [path]

    def add_url_to_dict(self,netloc,url):
        if netloc in self.urls_for_domain:
            self.urls_for_domain[netloc] += [url]
        else:
            self.urls_for_domain[netloc] = [url]

    def print_results_domains(self):
        for item in sorted(self.paths_for_domain):
            print item, self.paths_for_domain[item]

    def split_url(self,url):
        parse_result = urlparse.urlparse(url)
        return parse_result[1], parse_result[2]

if __name__ == "__main__":
    p = BingParser()
    p.load_results_from_file()
    p.run()

    # p.print_path_for_domain()

    # bing_parser() BingParser.parse_file(filename)
    # init with domains of both sets:
    #  1. (get) domains that match in set in orig data
    #  2. (get) domains that match in set of extended domains
    #  return list of [domain,username/path] pairs

    # todo: prefilter misc. paths, e.g. youtube.com/playlist
