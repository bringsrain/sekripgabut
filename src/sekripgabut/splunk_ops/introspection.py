# import json
import requests
import urllib3
import logging


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Endpoints
SERVER_INFO = "/services/server/info"


def get_server_info(base_url, token):
    """Get Splunk instance information.

    Arguments:
    base_url -- Splunk instance base url.
    token -- Splunk access token.

    Returns:
    json -- Current splunk instance info. Otherwise None
    """
    endpoint = f"{base_url}{SERVER_INFO}"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"output_mode": "json"}
    try:
        response = requests.get(
            endpoint, headers=headers, params=params, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError as e:
        logging.error(
            f"ConnectionError: Failed to connect to: {endpoint}. Error: {e}"
        )
    except requests.exceptions.Timeout as e:
        logging.error(
            f"TimeoutError: Request to {endpoint} timed out. Error: {e}"
        )
    except requests.exceptions.HTTPError as e:
        logging.error(
            f"HTTPError: {e.response.status_code} - {e.response.reason}"
            f"when accessing {endpoint}"
        )
    except requests.exceptions.RequestException as e:
        logging.error(
            f"RequestException: An unexpected error occurred: {e}"
        )

    return None


def get_splunk_version(base_url, token):
    try:
        splunk_info = get_server_info(base_url, token)
        if splunk_info:
            splunk_version = splunk_info["entry"][0]["content"]["version"]
            return splunk_version
    except Exception as e:
        logging.error(f"Failed to retrieve splunk info: {e}")

    return None
