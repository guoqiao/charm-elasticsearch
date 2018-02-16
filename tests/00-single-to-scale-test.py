#!/usr/bin/python3

import amulet
import json
import time
import unittest

CLUSTER_NAME = 'unique-name'
CURL_TIMEOUT = 180
JUJU_TIMEOUT = 1200


class TestElasticsearch(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.deployment = amulet.Deployment(series='xenial')
        cls.deployment.add('elasticsearch')
        cls.deployment.configure('elasticsearch',
                                 {'cluster-name': CLUSTER_NAME})

        try:
            cls.deployment.setup(timeout=JUJU_TIMEOUT)
            cls.deployment.sentry.wait_for_messages(
                {"elasticsearch": "Ready"}, timeout=JUJU_TIMEOUT)
        except amulet.helpers.TimeoutError:
            amulet.raise_status(
                amulet.SKIP, msg="Environment wasn't setup in time")
        cls.elasticsearch = cls.deployment.sentry['elasticsearch'][0]

    def test_health(self):
        ''' Test the health of the node upon first deployment
            by getting the cluster health, then inserting data and
            validating cluster health'''
        health = self.get_cluster_health()
        assert health['status'] in ('green', 'yellow')

        # Create a test index.
        curl_command = """
        curl -XPUT 'http://localhost:9200/test/tweet/1' -d '{
            "user" : "me",
            "message" : "testing"
        }'
        """
        self.curl_on_unit(curl_command)
        health = self.get_index_health('test')
        assert health['status'] in ('green', 'yellow')

    def test_config(self):
        ''' Validate our configuration of the cluster name made it to the
            application configuration'''
        health = self.get_cluster_health()
        cluster_name = health['cluster_name']
        assert cluster_name == CLUSTER_NAME

    def test_scale(self):
        ''' Validate scaling the elasticsearch cluster yields a healthy
            response from the API, and all units are participating '''
        self.deployment.add_unit('elasticsearch', units=2)
        self.deployment.setup(timeout=JUJU_TIMEOUT)
        self.deployment.sentry.wait_for_messages(
            {"elasticsearch": "Ready"}, timeout=JUJU_TIMEOUT)

        health = self.get_cluster_health(wait_for_nodes=3)
        index_health = self.get_index_health('test')
        print(health['number_of_nodes'])
        assert health['number_of_nodes'] >= 3
        assert index_health['status'] in ('green', 'yellow')

    def curl_on_unit(self, curl_command):
        ''' Run a curl command on the sentried ES unit. We'll retry this
            command until the CURL_TIMEOUT because it may take a few seconds
            for the ES systemd service to start.'''
        timeout = time.time() + CURL_TIMEOUT
        while time.time() < timeout:
            response = self.elasticsearch.run(curl_command)
            # run returns a msg,retcode tuple
            if response[1] == 0:
                return json.loads(response[0])
            else:
                print("Unexpected curl response: {}. "
                      "Retrying in 30s.".format(response[0]))
                time.sleep(30)

        # we didn't get rc=0 in the alloted time; raise amulet failure
        msg = (
            "Elastic search didn't respond to the command \n"
            "'{curl_command}' as expected.\n"
            "Return code: {return_code}\n"
            "Result: {result}".format(
                curl_command=curl_command,
                return_code=response[1],
                result=response[0])
        )
        amulet.raise_status(amulet.FAIL, msg=msg)

    def get_cluster_health(self, wait_for_nodes=0):
        curl_url = "http://localhost:9200/_cluster/health"
        if wait_for_nodes > 0:
            # Give the API up to 3m to determine if desired nodes are present
            curl_url = curl_url + "?timeout=180s&wait_for_nodes=ge({})".format(
                wait_for_nodes)
        curl_command = "curl -XGET '{}'".format(curl_url)

        return self.curl_on_unit(curl_command)

    def get_index_health(self, index_name):
        curl_url = "http://localhost:9200/_cluster/health/" + index_name
        curl_command = "curl -XGET '{}'".format(curl_url)

        return self.curl_on_unit(curl_command)


if __name__ == "__main__":
    unittest.main()
