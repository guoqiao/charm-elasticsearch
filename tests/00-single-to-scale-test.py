#!/usr/bin/python3

import amulet
import unittest
import requests
import json

class TestElasticsearch(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.deployment = amulet.Deployment(series='trusty')
        self.deployment.add('elasticsearch')
        self.deployment.configure('elasticsearch',
                                  {'cluster-name': 'unique-name'})

        try:
            self.deployment.setup(timeout=1200)
            self.deployment.sentry.wait()
        except amulet.helpers.TimeoutError:
            amulet.raise_status(
                amulet.SKIP, msg="Environment wasn't setup in time")


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
        response = self.curl_on_unit(curl_command)
        health = self.get_index_health('test')
        assert health['status'] in ('green', 'yellow')

    def test_config(self):
        ''' Validate our configuration of the cluster name made it to the
            application configuration'''
        health = self.get_cluster_health()
        cluster_name = health['cluster_name']
        assert cluster_name == 'unique-name'

    def test_scale(self):
        ''' Validate scaling the elasticsearch cluster yields a healthy
            response from the API, and all units are participating '''
        self.deployment.add_unit('elasticsearch', units=2)
        self.deployment.setup(timeout=1200)
        self.deployment.sentry.wait()
        health = self.get_cluster_health(wait_for_nodes=3)
        index_health = self.get_index_health('test')
        print(health['number_of_nodes'])
        assert health['number_of_nodes'] == 3
        assert index_health['status'] in ('green', 'yellow')

    def curl_on_unit(self, curl_command, unit_number=0):
        unit = "elasticsearch"
        response = self.deployment.sentry[unit][unit_number].run(curl_command)
        if response[1] != 0:
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

        return json.loads(response[0])

    def get_cluster_health(self, unit_number=0, wait_for_nodes=0,
                           timeout=180):
        curl_command = "curl http://localhost:9200"
        curl_command = curl_command + "/_cluster/health?timeout={}s".format(
            timeout)
        if wait_for_nodes > 0:
            curl_command = curl_command + "&wait_for_nodes={}".format(
                wait_for_nodes)

        return self.curl_on_unit(curl_command, unit_number=unit_number)

    def get_index_health(self, index_name, unit_number=0):
        curl_command = "curl http://localhost:9200"
        curl_command = curl_command + "/_cluster/health/" + index_name

        return self.curl_on_unit(curl_command)


def check_response(response, expected_code=200):
    if response.status_code != expected_code:
        msg = (
            "Elastic search did not respond as expected. \n"
            "Expected status code: %{expected_code} \n"
            "Status code: %{status_code} \n"
            "Response text: %{response_text}".format(
                expected_code=expected_code,
                status_code=response.status_code,
                response_text=response.text))

        amulet.raise_status(amulet.FAIL, msg=msg)


if __name__ == "__main__":
    unittest.main()
