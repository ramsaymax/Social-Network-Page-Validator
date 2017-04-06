import csv
from bing_api import BingAPI
from bing_parser import BingParser
from subscriber_counter import SubscriberCounter
from csv_output import CSVOutput
import itertools

class Validator():

    def __init__(self):
        self.input_filename = 'input.csv'
        self.header = []
        self.users = []
        # self.user = {} # current user dict: {header,data}
        self.load_users()
        self.bing_api = BingAPI()
        # self.p = BingParser()
        self.user_dict = None

        self.ep_fh = None
        self.output_filenames = ['complete match.csv','partial match.csv','zero match.csv','new accounts.csv','scraped matches.csv']
        self.output_fhs = [CSVOutput(filename) for filename in self.output_filenames]

        # header = ['youtube_id','youtube_username','facebook_title','']
        header = ['Initial YTID','Verified YT','Verified FB','Verified Instagram','Verified Vine','Verified Twitter']
        self.output_fhs[0].write_row(header)

        header += ['Unverified YT','Unverified FB','Unverified Instagram','Unverified Vine','Unverified Twitter']
        self.output_fhs[1].write_row(header)

        header = ['Initial YTID','Original YT','Original FB','Original Instagram','Original Vine','Original Twitter']
        self.output_fhs[2].write_row(header)

        new_header = ['New YT','New FB','New Instagram','New Vine','New Twitter']
        self.new_header_domains = ['youtube.com','facebook.com','instagram.com','vine.co','twitter.com']
        header = ['Initial YTID'] + [val for val in new_header for _ in (0,1) ]
        self.output_fhs[3].write_row(header)

        self.output_fhs[4].write_row(self.new_header_domains)

        self.sc = SubscriberCounter()
        self.sc.cache = True

    def load_users(self,filename=None):
        if filename is None:
            filename = self.input_filename
        with open(filename,'rb') as csvin:
            csvin = csv.reader(csvin, delimiter=',')
            self.header = [i.lower() for i in next(csvin)]
            for row in csvin:
                self.users.append(row)

    def check_users(self):
        count = 0
        for user in self.users:
            count += 1
            # if count < 8900:
                # continue
            self.make_user_dict(user)
            print "\n%i checking user: %s" % (count,self.user_dict['name'])
            self.check_user()
            # if count > 10000:
                # break

    def make_user_dict(self,user=None):
        self.user_dict = dict(zip(self.header,user))
        return self.user_dict

    def check_user(self,user_dict=None):
        try:
            if user_dict is None:
                user_dict = self.user_dict
        except Exception as e:
            print e

        query_string = self.construct_search_query(user_dict)
        print "query string = ",query_string
        self.p = BingParser()
        self.p.results_list = self.bing_api.send_request(query_string)
        self.p.run()

        self.compare_matches()

        self.output_extended_presense_matches()

    def compare_matches(self):

        subscriber_counts = []
        num_matches = 0
        self.matched_domain_username = {}

        print 'user dict', self.user_dict

        for domain in self.p.original_matches:
            print "domain == " + domain
            username = self.get_domain_username_for_domain(domain)

            if username == '':
              num_matches += 1
              continue

            print domain, self.p.paths_for_domain[domain], "<=>", username

            num_domain_matches = len(self.p.paths_for_domain[domain])

            if num_domain_matches == 1:
                path = self.p.paths_for_domain[domain][0].lower()
                path = path.replace('/','')
                print path.encode('utf-8')
                if path == username:
                    print "matched"
                    self.matched_domain_username[domain] = True
                    num_matches += 1
                else:
                    print "no match"
            else:
                # more than one path for domain, so need see if there is a match, then check it has the highest subscriber count for that match.
                index = self.index_containing_substring(self.p.paths_for_domain[domain], username)

                if index is not None:
                    print "matched index: %i" % index

                    # check that match index is index of highest sub count.
                    subscriber_counts = []
                    for url in self.p.urls_for_domain[domain]:
                        print url.encode('utf-8')
                        # get subscriber counts for each url
                        self.sc.assign_subclass(url)
                        print self.sc.get_count()
                        subscriber_counts.append(self.sc.get_count())
                    print subscriber_counts
                    if self.is_index_highest_in_list(subscriber_counts, index):
                        num_matches += 1
                        self.matched_domain_username[domain] = True
                    else:
                        print "index is not highest in list, match not counted"

                else:
                    print "more than one path in domain list, no match"
                pass
            print "\n"

        print "matched %i of %i social platforms" % (num_matches, len(self.p.original_matches))

        if num_matches == len(self.p.original_matches) and num_matches != 0:
            # complete match
            row = self.populate_row_from_user_dict()
            self.output_fhs[0].write_row(row)
        elif num_matches > 0:
            print "PARTIAL"
            # partial match
            youtube_id = self.user_dict['youtube_id']
            row = [None] * ( len(self.new_header_domains) * 2 + 1 )
            row[0] = youtube_id
            print len(row)

            print self.matched_domain_username
            for domain in self.p.original_domains:
                print domain
                username = self.get_domain_username_for_domain(domain)
                if domain in self.matched_domain_username:
                    # put in matched pos
                    header_pos = self.new_header_domains.index(domain) + 1
                    row[header_pos] = username
                else:
                    # put in unmatched pos
                    header_pos = self.new_header_domains.index(domain) + 5 + 1
                    row[header_pos] = username

            self.output_fhs[1].write_row(row)

        elif num_matches == 0:
            # zero match / new accounts
            subscriber_counts = [] # since there are no matches, just check there is at least one with over 50k subs
            if subscriber_counts == []:
                for domain in self.p.original_matches:
                    for url in self.p.urls_for_domain[domain]:
                        self.sc.assign_subclass(url)
                        subscriber_counts.append(self.sc.get_count())

            print subscriber_counts
            # print len(subscriber_counts)

            min_sub_count = 50000
            # print min(subscriber_counts)

            if len(subscriber_counts) > 0 and max(subscriber_counts) > min_sub_count:
                # new accounts
                youtube_id = self.user_dict['youtube_id']
                row = [None] * ( len(self.new_header_domains) * 2 + 1 )
                row[0] = youtube_id
                # print "min sub count > ",min_sub_count
                index = 0
                header_pos = 0
                for domain in self.p.original_matches:
                    header_offset = 0
                    header_pos = self.get_header_pos_for_domain(domain)
                    for url in self.p.urls_for_domain[domain]:
                        if header_offset == 2:
                            continue
                        if subscriber_counts[index] > min_sub_count:
                            print url, subscriber_counts[index]
                            # need to put this url in the right position for the domain
                            row[header_pos + header_offset] = url
                            header_offset += 1

                        index += 1

                self.output_fhs[3].write_row(row)
            else:
                # zero match
                row = self.populate_row_from_user_dict()
                self.output_fhs[2].write_row(row)

        row = [None] * len(self.new_header_domains)

        for domain, path in self.p.paths_for_domain.items():
            if domain not in self.new_header_domains:
              continue
            username = self.get_domain_username_for_domain(domain)
            if username == '':
              username = path[0]
            row[self.new_header_domains.index(domain)] = username
        self.output_fhs[4].write_row(row)

        # quit()

    def get_header_pos_for_domain(self,domain):
        return self.new_header_domains.index(domain) * 2 + 1

    def populate_row_from_user_dict(self):
        youtube_id = self.user_dict['youtube_id']
        youtube_username = self.user_dict['youtube_username']
        facebook_username = self.user_dict['facebook_username']
        instagram_username = self.user_dict['instagram_username']
        vine_username = self.user_dict['vine_username']
        twitter_username = self.user_dict['twitter_username']
        row = [youtube_id,youtube_username,facebook_username,instagram_username,vine_username,twitter_username]
        return row


    def index_containing_substring(self,list, substring): # http://stackoverflow.com/a/2170915/376718
        substring = substring.decode('utf-8') if isinstance(substring, str) else substring
        for i, s in enumerate(list):
            s = s.decode('utf-8') if isinstance(s, str) else s
            if substring.lower() == s.lower():
                return i
        for i, s in enumerate(list):
            s = s.decode('utf-8') if isinstance(s, str) else s
            if substring.lower() in s.lower():
                return i
        return None

    def is_index_highest_in_list(self,list,index):
        list = [self.convert_to_int(i) for i in list]
        max_index = list.index(max(list))
        return max_index == index

    def convert_to_int(self,x):
        try:
            return int(x)
        except Exception:
            return None

    def get_domain_username_for_domain(self,domain): # youtube.com -> self.user_dict['youtube_username']
        # print "domain = ",domain
        domain_username = domain
        domain_username = domain_username.replace('.com','')
        domain_username = domain_username.replace('.co','')
        domain_username += '_username'
        # print domain_username
        return self.user_dict[domain_username]

    def output_extended_presense_matches(self):
        if self.ep_fh is None:
            self.ep_fh = CSVOutput('extended_presense.csv') # output to ./output/extended_presense.csv
            header = ['Initial YTID','Potential Pinterest','Potential IMDB','Potential Twitch','Potential Snapchat','Potential Periscope']
            self.extended_header_domains = ['pinterest.com','imdb.com','twitch.tv','snapchat.com','periscope.tv']
            self.ep_fh.write_row(header)

        youtube_id = self.user_dict['youtube_id']
        row = [None] * 6
        row[0] = youtube_id
        data_found = False

        for domain in self.p.extended_matches:
            url = self.p.urls_for_domain[domain][0] # just get first url
            print "found ep url: ",url.encode('utf-8')

            header_pos = self.extended_header_domains.index(domain) + 1
            row[header_pos] = url
            data_found = True

        if data_found:
            self.ep_fh.write_row(row)

    def construct_search_query(self,user_dict=None):
        if user_dict is None:
            user_dict = self.user_dict

        # for item in sorted(user_dict):
        #     print item, user_dict[item]

        if user_dict['twitter_username'] != '':
            query_string = user_dict['name'] + ", "+ user_dict['twitter_username']
        elif user_dict['youtube_username'] != '':
            query_string = user_dict['name'] + ", " + user_dict['youtube_username']
        else:
            highest_sub_platform = self.get_platform_with_highest_sub_count(user_dict)
            query_string = user_dict['youtube_title'] + ", " + \
                           user_dict[highest_sub_platform + '_username']
        return query_string

    def get_platform_with_highest_sub_count(self,user_dict=None):
        if user_dict is None:
            user_dict = self.user_dict

        user_subs = {}
        for key in user_dict:
            if '_subs' in key:
                if user_dict[key].isdigit():
                    user_subs[key] = int(user_dict[key])
        # print user_subs
        for item in sorted(user_subs, key=lambda x: int(user_subs[x]), reverse=True):
            # print item, user_subs[item]
            return item.replace('_subs','')
        # just find any platform
        for key, value in user_dict.items():
          if key != "name" and value:
            if key.find('_') != -1:
              return key[0:key.find('_')]
            else:
              return key


if __name__ == "__main__":
    v = Validator()
    v.check_users()
    # v.get_platform_with_highest_sub_count(v.users[0])

    # todo: parse the results
    # check and compare domains/urls match the data in self.user
    # extended presense - url checker class? / return/filter matching domains/urls

    # subscriber count for domain
    # each platform subclass for facebook_sub_counter

    # add logging
    # add database/cache?

    # cache results, allows resuming of script and testing


    # compare social results
    # foreach result in original data
    #
    # filter bing data
    # compare each result to original data.
