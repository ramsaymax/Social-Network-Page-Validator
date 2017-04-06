import unittest
from bing_api import BingAPI

class BingAPITest(unittest.TestCase):

    def setUp(self):
        self.b = BingAPI()
        self.query = 'microsoft'

    @unittest.skip('')
    def test_send_request_returns_ok_status_code(self):
        self.b.cache_requests = False
        query = 'taylor swift taylorswiftvevo'
        self.b.send_request(query)
        self.assertEqual(200,self.b.r.status_code)

    @unittest.skip('')
    def test_query_with_ampersand(self):
        self.b.cache_requests = False
        query = 'dots & eggs'
        self.b.send_request(query)
        self.assertEqual(200,self.b.r.status_code)

    # @unittest.skip('')
    def test_default_limit_is_20(self):
        result_list = self.b.send_request(self.query)
        self.assertEqual(20,len(result_list))

    # @unittest.skip('')
    def test_limit_results(self):
        result_list = self.b.send_request(self.query, limit=15)
        self.assertEqual(15,len(result_list))

    # @unittest.skip('')
    def test_skip_results(self):
        result_list = self.b.send_request(self.query, limit=9, skip=15)
        first_result_uri = result_list[0]['__metadata']['uri']
        last_result_uri = result_list[-1]['__metadata']['uri']
        self.assertTrue('skip=15' in first_result_uri)
        self.assertTrue('skip=23' in last_result_uri)

    def test_cache_filename(self):
        limit, skip = 5, 2
        filename = self.b.construct_filename_from_args(self.query, limit, skip)
        self.assertEqual('5_2_microsoft.json',filename)

    def test_save_and_load_results_from_cache(self):
        limit, skip = 5, 2
        self.b.send_request(self.query, limit, skip)
        result_list = self.b.load_cached_results_from_query(self.query, limit, skip)
        self.assertEqual(5,len(result_list))



if __name__ == '__main__':
    unittest.main()
