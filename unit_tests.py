import requests
import json
import unittest
import config.config as cfg

URL = "http://localhost:8080/"

class QueryUrlUnitTests(unittest.TestCase):
    """unit test module"""

    def test_health_check(self):
        """ Test if healthcheck is working"""

        r = requests.get(URL+"healthcheck")
        self.assertEqual(r.json()["app_status"], "ok")

    def test_query_url(self):
        """ Test if query_url is working"""

        r = requests.get(URL+"queryurl")
        self.assertEqual(r.json()["status"], "ok")
        self.assertEqual(r.status_code, 200)
        # self.assertTrue(r.json()['response'])
        # for url in r.json()['response']:
        #     if "message" not in r.json()['response'][url]:
        #         self.assertIn("status_code",r.json()['response'][url])
        #         self.assertIn("up",r.json()['response'][url])
        #         self.assertIn("response_time_in_ms",r.json()['response'][url])

        """ Test if /metrics is working"""
        
        r = requests.get(URL+"metrics")
        urls=cfg.urls
        for url in urls:
            responseTimeKey="sample_external_url_response_ms{url=\""+url+"\"}"
            self.assertIn(responseTimeKey,r.text)
            statusKey="sample_external_url_up{url=\""+url+"\"}"
            self.assertIn(statusKey,r.text)

if __name__ == "__main__":
    unittest.main()
