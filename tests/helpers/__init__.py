import sys

import amulet
import requests


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


def setup_deployment(deployment, timeout=900):
    """Setup the deployment and wait until installed."""
    try:
        deployment.setup(timeout=timeout)
        deployment.sentry.wait()
    except amulet.helpers.TimeoutError:
        amulet.raise_status(amulet.SKIP, msg="Environment wasn't setup in time")


def get_unit_address(deployment, unit_number=0):
    unit = deployment.sentry.unit['elasticsearch/%s' % unit_number]
    elastic_ip = unit.info['public-address']
    return 'http://' + elastic_ip + ":9200"


def get_cluster_health(deployment, unit_number=0, wait_for_nodes=0,
                       timeout=180):
    addr = get_unit_address(deployment, unit_number=0)
    addr = addr + "/_cluster/health?timeout={}s".format(timeout)
    if wait_for_nodes > 0:
        addr = addr + "&wait_for_nodes={}".format(wait_for_nodes)
    response = requests.get(addr)
    check_response(response, expected_code=200)
    return response.json()


def get_index_health(deployment, index_name, unit_number=0):
    addr = get_unit_address(deployment, unit_number=0)
    response = requests.get(addr + "/_cluster/health/" + index_name)
    check_response(response, expected_code=200)
    return response.json()
