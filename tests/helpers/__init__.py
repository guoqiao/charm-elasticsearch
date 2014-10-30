import amulet
import json


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


def curl_on_unit(curl_command, deployment, unit_number=0):
    unit = "elasticsearch/{}".format(unit_number)

    response = deployment.sentry.unit[unit].run(curl_command)
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


def setup_deployment(deployment, timeout=900):
    """Setup the deployment and wait until installed."""
    try:
        deployment.setup(timeout=timeout)
        deployment.sentry.wait()
    except amulet.helpers.TimeoutError:
        amulet.raise_status(
            amulet.SKIP, msg="Environment wasn't setup in time")


def get_cluster_health(deployment, unit_number=0, wait_for_nodes=0,
                       timeout=180):
    curl_command = "curl http://localhost:9200"
    curl_command = curl_command + "/_cluster/health?timeout={}s".format(
        timeout)
    if wait_for_nodes > 0:
        curl_command = curl_command + "&wait_for_nodes={}".format(
            wait_for_nodes)

    return curl_on_unit(curl_command, deployment, unit_number=unit_number)


def get_index_health(deployment, index_name, unit_number=0):
    curl_command = "curl http://localhost:9200"
    curl_command = curl_command + "/_cluster/health/" + index_name

    return curl_on_unit(curl_command, deployment)
