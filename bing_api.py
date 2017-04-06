import requests
import json
import os
import urllib

# https://datamarket.azure.com/dataset/explore/bing/search
# [u'Description', u'Title', u'Url', u'__metadata', u'DisplayUrl', u'ID']

class BingAPI():
    def __init__(self):
        self.url = "https://api.datamarket.azure.com/Bing/Search/v1/Web?Query='%s'&$format=json&$top=%s&$skip=%s"
        self.api_key = ''

        self.result_limit = 20
        self.load_auth_from_file()
        self.cache_dir = './cache/'
        self.ensure_dir(self.cache_dir)
        self.cache_requests = True

    def load_auth_from_file(self):
        if self.api_key == '':
            with open ("./auth_bing.txt", "r") as myfile:
                self.api_key = myfile.readline().strip()

    def send_request(self,query=None,limit=None,skip=''):
        if query is None:
            return
        if limit is None:
            limit = self.result_limit

        print query
        query = urllib.quote(query)
        query = query.replace('&','%26').replace('/','_').replace(':','_')
        query = query.replace('%20',' ').replace('%2C',',')
        print query

        path = self.cache_dir + self.construct_filename_from_args(query, limit, skip)
        if os.path.isfile(path):
            return self.load_cached_results_from_query(query, limit, skip)

        url = self.url % (query,limit,skip)
        self.r = requests.get(url,auth=('',self.api_key))
        results = json.loads(self.r.content)
        self.results_list = results['d']['results']
        if self.cache_requests:
            self.save_result_to_cache(self.r.content, query, limit, skip)
        return self.results_list

    def load_results_from_file_path(self,path=None):
        if path is None:
            path = 'tswift.json'
        with open(path,"rb") as myfile:
            results = myfile.read().strip()
        results = json.loads(results)
        self.results_list = results['d']['results']
        return self.results_list

    def save_result_to_cache(self,results_list,query,limit,skip):
        filename = self.construct_filename_from_args(query, limit, skip)
        path = self.cache_dir + filename
        file = open(path, "wb")
        for item in results_list:
            file.write(item)
        file.close()
        return path

    def load_cached_results_from_query(self,query,limit,skip):
        filename = self.construct_filename_from_args(query, limit, skip)
        path = self.cache_dir + filename
        return self.load_results_from_file_path(path)

    def construct_filename_from_args(self,query,limit,skip):
        if skip == '':
            skip = 0
        query = query.replace('*','_').replace('?','_').replace('|','_')
        query = (query[:100]) if len(query) > 100 else query
        filename = str(limit) + "_" + str(skip) + "_" + query + ".json"
        return filename

    def ensure_dir(self,directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

if __name__ == "__main__":
    b = BingAPI()
    print b.load_results_from_file_path()
