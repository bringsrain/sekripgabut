import requests
# import json
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
        logging.info("Start to update events")
        response = requests.post(endpoint, headers=headers, data=data,
                                 verify=False)

        # Check response status and log details
        if response.status_code == 200:
            logging.info(f"Successfully update events: {response.json()}")
        else:
            error_details = response.json()
            logging.error(
                f"Failed to update events ({ruleUIDs or searchID}):"
                f"{error_details}"
                )
        # Raise HTTPError for non-200 status codes
        response.raise_for_status()

    except Exception as e:
        logging.critical(f"Failed to update event: {e}")
        raise
