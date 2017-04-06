import unittest
from scraper import Scraper

class ScraperTest(unittest.TestCase):

    def setUp(self):
        self.s = Scraper()

    def test_make_request(self):
        url = 'http://google.com'
        output_filename = 'test_google.htm'
        self.s.make_request(url, output_filename)
        # self.s.make_request(url, output_filename)




if __name__ == '__main__':
    unittest.main()
