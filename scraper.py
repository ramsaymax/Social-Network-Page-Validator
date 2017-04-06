import requests
import os

class Scraper(object):
    def __init__(self):
        super(Scraper, self).__init__()
        self.user_agent_string = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
        self.cache_dir = './cache/'
        self.ensure_dir(self.cache_dir)
        self.cache = True

    def ensure_dir(self,dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def make_request(self,url=None,filename=None):
        if url is None:
            url = self.url

        filename = filename.replace('*','')
        filename = (filename[:100] + '.json') if len(filename) > 100 else filename

        if self.cache is True:
            if filename is not None:
                output_path = self.cache_dir + filename
                if os.path.isfile(output_path):
                    file = open(output_path, "r")
                    return file.read()

        headers = {'user-agent':self.user_agent_string}
        # print url
        self.response = requests.get(url,headers=headers)
        self.output_response_to_file(filename)
        return self.response.content

    def output_response_to_file(self,filename=None):
        if filename is None:
            return
        output_path = self.cache_dir + filename
        file = open(output_path, "wb")
        file.write(self.response.content)
        file.close()
        print "saved to:",output_path.encode('utf-8')

if __name__ == "__main__":
    s = Scraper()
