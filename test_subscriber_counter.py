import unittest
from subscriber_counter import SubscriberCounter

class SubscriberCounterTest(unittest.TestCase):

    def setUp(self):
        self.sc = SubscriberCounter()
        self.sc.cache = True

    def test_facebook_likes_counter(self):
        url = 'https://www.facebook.com/jerseydemic/'
        self.sc.assign_subclass(url)
        self.assertGreaterEqual(self.sc.get_count(), 2518212)

    def test_youtube_subscriber_counter(self):
        url = 'https://www.youtube.com/user/taylorswift'
        self.sc.assign_subclass(url)
        self.assertGreaterEqual(self.sc.get_count(), 1331053)

    def test_instagram_follower_counter(self):
        url = 'https://www.instagram.com/taylorswift'
        self.sc.assign_subclass(url)
        self.assertGreaterEqual(self.sc.get_count(), 59221887)

    def test_vine_follower_counter(self):
        url = 'https://vine.co/u/1229983076923695104'
        self.sc.assign_subclass(url)
        self.assertGreaterEqual(self.sc.get_count(), 2159436)

    def test_twitter_follower_counter(self):
        url = 'https://twitter.com/taylorswift13/'
        self.sc.assign_subclass(url)
        self.assertGreaterEqual(self.sc.get_count(), 67721872)

    def test_non_matching_url_raises_exception(self):
        url = 'http://google.com'
        with self.assertRaises(Exception):
            self.sc.assign_subclass(url)

    def test_youtube_get_username_from_url(self):
        url = 'https://www.youtube.com/user/taylorswift'
        self.sc.assign_subclass(url)
        username = self.sc.get_username_from_url(url)
        self.assertEqual('taylorswift',username)

    def test_use_cache_with_reuse(self):
        url_count = [
            ('https://www.facebook.com/jerseydemic/',2518212),
            ('https://www.instagram.com/taylorswift',59221887),
            ('https://www.facebook.com/taylorswift/',73747502)
        ]
        for url,count in url_count:
            self.sc.assign_subclass(url)
            self.assertGreaterEqual(self.sc.get_count(), count)

    def test_url_doesnt_start_with_http_www(self):
        url = 'youtube.com/user/taylorswift'
        self.sc.assign_subclass(url)
        self.assertGreaterEqual(self.sc.get_count(), 1331053)

    def test_url_doesnt_start_with_http(self):
        url = 'www.youtube.com/user/taylorswift'
        self.sc.assign_subclass(url)
        self.assertGreaterEqual(self.sc.get_count(), 1331053)

    def test_non_profile_url_returns_none(self):
        url = 'youtube.com/watch'
        self.sc.assign_subclass(url)
        self.assertEqual(None, self.sc.get_count())

    def test_fb_url_doesnt_start_with_http(self):
        url = 'facebook.com/jerseydemic/'
        self.sc.assign_subclass(url)
        # print self.sc.get_count()
        self.assertGreaterEqual(self.sc.get_count(), 2518212)

    def test_twitter_url(self):
        url = 'twitter.com/unilad/status/471070400768929792'
        self.sc.assign_subclass(url)
        # print self.sc.get_count()

    def test_vine_url(self):
        url = 'https://vine.co/kuu/'
        self.sc.assign_subclass(url)
        print self.sc.get_count()

if __name__ == '__main__':
    unittest.main()
