import requests
import json
import time
import urllib3
import logging


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Endpoints
# common
SEARCH_JOBS = "/services/search/jobs"
SEARCH_JOBS_SID = "/services/search/jobs/{search_id}"
SEARCH_SID_SUMMARY = (
    "/services/search/jobs/{search_id}/summary")
# V1
# Most are deprecated since splunk 9.0.1
SEARCH_JOBS_EXPORT = "/services/search/jobs/export"
SEARCH_JOBS_SID_EVENTS = (
    "/services/search/jobs/{search_id}/events")
SEARCH_JOBS_SID_RESULTS = (
    "/services/search/jobs/{search_id}/results")
# V2
SEARCH_JOBS_EXPORT_V2 = "/services/search/v2/export"
SEARCH_JOBS_SID_EVENTS_V2 = (
   "/services/search/v2/jobs/{search_id}/events")
SEARCH_JOBS_SID_RESULTS_V2 = (
    "/services/search/v2/jobs/{search_id}/results")


def get_search_jobs(base_url, token, output_mode="json", **kwargs):
    """Get details of all current searches."""
    endpoint = f"{base_url}{SEARCH_JOBS}"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "output_mode": output_mode
    }

    if kwargs:
        params.update(kwargs)

    response = requests.get(endpoint, headers=headers,
                            params=params, verify=False)

    if response.status_code == 200:
        return response.text
    else:
        raise Exception(
            f"Code: {response.status_code},"
            f"Response: {response.text}")


def set_search_jobs(base_url, token, query,
                    earliest_time="", latest_time="now",
                    output_mode="json", **kwargs):
    """Start a new search and return the search ID (<sid>)
    Args:
         base_url (str): Base URL of the Splunk instance.
         token (str): Splunk access token.
         query (str): The search query.
         earliest_time (str, optional): Earliest time for the search.
         latest_time (str, optional): Latest time for the search.
         output_mode (str, optional): Output format. Default is "json".
         **kwargs: Additional parameters for the search.
    Returns:
    str: The search ID (sid) if the request is successful.

    Raises:
        Exception: If the request fails, logs the error and raises an
        exception.
    """
    endpoint = f"{base_url}{SEARCH_JOBS}"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
            "search": query,
            "earliest_time": earliest_time,
            "latest_time": latest_time,
            "output_mode": output_mode,
            **kwargs
    }

    response = None

    try:
        logging.info("Initiating search jobs...")
        response = requests.post(endpoint, headers=headers,
                                 data=payload, verify=False)
        response.raise_for_status()

        # Validate the response JSON and extract 'sid'
        response_json = response.json()
        sid = response_json.get('sid')
        if not sid:
            logging.error(
                f"Search job initiated but no SID returned: {response_json}")
            raise ValueError(
                "Failed to retrieve search ID (sid) from the response."
            )

        logging.info(f"Search job created successfully wit SID: {sid}")
        return sid
    except requests.exceptions.RequestException as e:
        error_message = f"Request to {endpoint} failed: {e}"
        if response:
            error_message += (
                f" | Status Code: {response.status_code}"
                f" | Response Text: {response.text}"
            )
        logging.error(error_message)
        raise


def get_search_job_by_sid(base_url, token, sid, output_mode="json", **kwargs):
    """Manage the {search_id} search job."""
    endpoint = f"{base_url}{SEARCH_JOBS_SID.format(search_id=sid)}"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "output_mode": output_mode
    }

    if kwargs:
        params.update(kwargs)

    try:
        logging.info(f"Requesting job {sid} info...")
        response = requests.get(endpoint, headers=headers,
                                params=params, verify=False)
        response.raise_for_status()

        response_json = response.json()
        return response_json
    except requests.exceptions.RequestException as e:
        logging.error(f"Request to {endpoint} failed: {e}")
        raise


def get_search_results(base_url, token, sid, **kwargs):
    """Fetch search results per 1000 results"""
    endpoint = f"{base_url}{SEARCH_JOBS_SID_RESULTS.format(search_id=sid)}"
    page_count = 1000
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "output_mode": "json",
        "count": page_count,
        "offset": 0,
    }

    if kwargs:
        params.update(kwargs)

    all_results = []
    while True:
        response = requests.get(
            endpoint, headers=headers, params=params, verify=False
        )

        if response.status_code == 204:
            # No result yet; wait for the job to complete
            time.sleep(3)
            continue

        if response.status_code not in (200, 201):
            raise Exception(f"Failed to fetch results: {response.text}")

        # Parse the response
        response_json = response.json()

        results = response_json.get("results", [])
        if not results:
            if all_results:
                print("All results are fetched.")
                break
            else:
                print("No more results available")
                # Break when no more results are returned
                break

        all_results.extend(results)
        print(f"Fetched {len(results)} results (Total: {len(all_results)})")

        if len(results) < page_count:
            print("Fetched final result.")
            break
        params["offset"] += page_count  # get another page

    return all_results


def search_jobs_sid_events(
        base_url,
        token,
        sid,
        output_mode="json",
        **kwargs):
    endpoint = f"{base_url}{SEARCH_JOBS_SID_EVENTS.format(sid)}"
    headers = {"Authorization": f"{token}"}
    params = {
        "output_mode": "json"
    }
