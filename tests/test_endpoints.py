import requests
import unittest
from census import DEFINITIONS


class TestRemoteAPI(unittest.TestCase):
    def test_urls(self):
        """Ensure the Census XML URLs are available"""
        for dataset, years in DEFINITIONS.items():
            for year, url in years.items():
                resp = requests.head(url)
                self.assertEqual(resp.status_code, 200,
                        "{0} responded with status code {1}".format(url, resp.status_code))


if __name__ == '__main__':
    unittest.main()
