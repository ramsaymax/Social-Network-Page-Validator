import unittest
from validator import Validator

class ValidatorTest(unittest.TestCase):

    def setUp(self):
        self.v = Validator()

    def test_load_users(self):
        self.assertEqual(10000,len(self.v.users))

    def test_get_first_user(self):
        self.assertEqual("jerseydemic",self.v.users[0][2])

    def test_header_lower(self):
        self.assertEqual("youtube_id",self.v.header[0])

    def test_get_platform_with_highest_sub_count(self):
        user = self.v.users[0]
        user_dict = self.v.make_user_dict(user)
        self.assertEqual("facebook",self.v.get_platform_with_highest_sub_count(user_dict))
        # facebook_subs 2151703, instagram_subs, vine_subs, youtube_subs 1880

    def test_construct_search_query_case_1(self):
        user = self.v.users[0]
        user_dict = self.v.make_user_dict(user)
        query_string = self.v.construct_search_query(user_dict)
        self.assertEqual("jerseydemic, jerseydemic",query_string)

    def test_construct_search_query_case_2(self):
        user = self.v.users[0]
        user_dict = self.v.make_user_dict(user)
        user_dict['twitter_username'] = ''
        query_string = self.v.construct_search_query(user_dict)
        self.assertEqual("jerseydemic, urbanbackground",query_string)

    def test_construct_search_query_case_3(self):
        user = self.v.users[0]
        user_dict = self.v.make_user_dict(user)
        user_dict['twitter_username'] = ''
        user_dict['youtube_username'] = ''
        query_string = self.v.construct_search_query(user_dict)
        self.assertEqual("Jersey Demic, jerseydemic",query_string)

    def test_get_domain_username_for_domain(self):
        user = self.v.users[0]
        self.v.make_user_dict(user)
        domain = 'youtube.com'
        username = self.v.get_domain_username_for_domain(domain)
        self.assertEqual('urbanbackground',username)

    def test_index_containing_substring(self):
        list = ['apple','microsoft']
        substring = 'app'
        index = self.v.index_containing_substring(list, substring)
        self.assertEqual(0,index)

    def test_index_highest_in_list(self):
        list = [2,None,145,123,16,4,None]
        index = 2
        self.assertTrue( self.v.is_index_highest_in_list(list, index) )

    def test_index_containing_substring_2(self):
        list = [u'/maryack29', u'/karinricosubran']
        substring = 'karinricosubran'
        index = self.v.index_containing_substring(list, substring)
        self.assertEqual(1,index)

    def test_index_highest_in_list_if_string(self):
        list = [None, "4", "43"]
        index = 2
        self.assertTrue( self.v.is_index_highest_in_list(list, index) )

    def test_header_pos_for_domain(self): # new accounts output
        domain = 'youtube.com'
        pos = self.v.get_header_pos_for_domain(domain)
        self.assertEqual(1, pos)

        domain = 'twitter.com'
        pos = self.v.get_header_pos_for_domain(domain)
        self.assertEqual(9, pos)


if __name__ == '__main__':
    unittest.main()
