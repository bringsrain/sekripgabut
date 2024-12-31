import requests
import json
import urllib3
import logging


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


NOTABLE_UPDATE = "/services/notable_update"


def update_notable_event(base_url, token, status=None, ruleUIDs=[],
                         searchID=None, newOwner="", urgency="",
                         disposition=None, comment=""):
    """Update the status, urgency, owner, or comment of one or more findings.

    Arguments:
    base_url -- Splunk instance base URL.
    token -- Splunk token access.

    Keyword arguments:
    ruleUIDs -- A list of finding IDs. Required if `searchID` is not provided.
    searchID -- ID of a search. Required if `ruleUIDs` is not provided.
    newOwner -- New owner for the notable events.
    urgency -- New urgency (severity) for the notable events.
    status -- New status ID for the notable events.
    disposition -- New disposition ID for the notable events.
    comment -- Additional comment about the changes.

    Returns:
    dict - JSON response from the API.
    """
    if not (ruleUIDs or searchID):
        raise ValueError("Either 'ruleUIDs' or 'searchID' must be provided")

    endpoint = f"{base_url}{NOTABLE_UPDATE}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        key: value for key, value in {
            "ruleUIDs": ruleUIDs,
            "searchID": searchID,
            "newOwner": newOwner,
            "urgency": urgency,
            "status": status,
            "disposition": disposition,
            "comment": comment,
        }.items() if value  # Include only non-empty values
    }

    try:
        logging.info("Starting to update events...")

        # Send the API request
        response = requests.post(endpoint, headers=headers, data=data,
                                 verify=False)

        # Parse and log response details
        try:
            response_data = response.json()
            logging.debug(f"Response JSON: {response_data}")
        except json.JSONDecodeError:
            logging.error("Failed to decode JSON from response")
            response.raise_for_status()
            raise

        # Check if the API reported success
        if response.status_code == 200 and response_data.get("success", False):
            logging.info(f"Successfully update events: {response_data}")
            return response_data
        else:
            error_message = response_data.get(
                "message", "Unknown error occurred")
            logging.error(
                # f"Failed to update events ({ruleUIDs or searchID}):"
                f"Error: {error_message}. {len(ruleUIDs) if ruleUIDs else ''}"
                )
            raise ValueError(f"Update failed: {error_message}")

    except requests.exceptions.RequestException as e:
        logging.critical(f"Request failed: {e}")
        raise
    except Exception as e:
        logging.critical(f"Unexpected error occurred: {e}")
        raise
