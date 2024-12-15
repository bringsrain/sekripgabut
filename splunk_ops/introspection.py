import json
import requests
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Endpoints
SERVER_INFO = "/services/server/info"


def get_server_info(base_url, token):
    endpoint = f"{base_url}{SERVER_INFO}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"output_mode": "json"}
    response = requests.get(
        endpoint, headers=headers, data=data, verify=False)

    return response.json()


def get_splunk_version(base_url, token):
    splunk_info = get_server_info(base_url, token)
    return splunk_info["entry"][0]["content"]["version"]
