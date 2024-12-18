import requests
import json
import urllib3
import logging


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


NOTABLE_UPDATE = "/services/notable_update"


def update_notable_event(base_url, token, ruleUIDs=[], searchID="",
                         newOwner="", urgency="", status="",
                         disposition="", comment=""):
    """Update the status, urgency, owner, or comment of one or more findings.

    Arguments:
    base_url -- Splunk instance base URL.
    token -- Splunk token access.

    Keyword arguments:
    ruleUIDs -- A list of finding IDs. Must be provided if a searchID is not
    provided. Include multiples of this attribute to edit multiple events.
    searchID -- An ID of a search. All of the events associated with this
    search will be modified unless a list of ruleUIDs are provided that limit
    the scope to a subset of the results.
    newOwner -- An owner. Only required if reassigning the event.
    urgency -- An urgency. Only required if you are changing the urgency of
    the event.
    status -- A status ID matching a status in reviewstatuses.conf. Only
    required if you are changing the status of the event.
    disposition -- An ID for a disposition that matches a disposition in the
    reviewstatuses.conf configuration file. Required only if you are changing
    the disposition of the event.
    comment -- A description of the change or some information about the
    findings.

    Returns:
    json - Response text values
    """
    endpoint = f"{base_url}{NOTABLE_UPDATE}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "ruleUIDs": ruleUIDs,
        "searchID": searchID,
        "newOwner": newOwner,
        "urgency": urgency,
        "status": status,
        "disposition": disposition,
        "comment": comment,
    }

    try:
        logging.info("Start to update events")
        response = requests.post(endpoint, headers=headers, data=data,
                                 verify=False)
        logging.info(response.status_code)
        if response.status_code != 200:
            raise Exception(
                logging.error(
                    f"Failed to update {ruleUIDs if ruleUIDs else searchID}"
                    f"{response.json()}"
                )
            )
        logging.info(response.text)
        return response.json()
    except Exception as e:
        logging.critical(f"Failed to update event: {e}")
        raise
