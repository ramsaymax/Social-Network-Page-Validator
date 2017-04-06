import unittest
from bing_parser import BingParser

class BingParserTest(unittest.TestCase):

    def setUp(self):
        self.p = BingParser()
        self.url = 'http://www.youtube.com/user/TaylorSwiftVEVO'

    def test_load_results(self):
        self.p.load_results_from_file()
        self.assertEqual(50,len(self.p.results_list))

    def test_split_url(self):
        netloc, path = self.p.split_url(self.url)
        self.assertEqual('www.youtube.com',netloc)
        self.assertEqual('/user/TaylorSwiftVEVO',path)

    def test_parse_results_into_paths_for_domain_dict(self):
        self.p.results_list = [{'Url':self.url}]
        self.p.add_results_to_paths_for_domain_dict()
        self.assertEqual(1,len(self.p.paths_for_domain))        
        key, value = self.p.paths_for_domain.popitem()
        self.assertEqual('youtube.com',key)
        self.assertEqual(['TaylorSwiftVEVO'],value)

    def test_load_results_from_list(self):
        self.p.results_list = [{'Url':self.url}]
        self.p.run()
        self.assertEqual(1,len(self.p.original_matches))

if __name__ == '__main__':
    unittest.main()
