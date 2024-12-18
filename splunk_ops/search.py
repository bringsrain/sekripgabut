import requests
import json
import time
import urllib3


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
                    earliest_time="-24h", latest_time="now",
                    output_mode="json", **kwargs):
    """Start a new search and return the search ID (<sid>)"""
    endpoint = f"{base_url}{SEARCH_JOBS}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "search": query,
        "earliest_time": earliest_time,
        "latest_time": latest_time,
        "output_mode": output_mode
    }

    if kwargs:
        data.update(kwargs)

    response = requests.post(endpoint, headers=headers,
                             data=data, verify=False)
    if response.status_code == 201:
        return response.json()["sid"]
    else:
        raise Exception(
            f"Code: {response.status_code},"
            f"Response: {response.text}")


def get_search_jobs_sid(base_url, token, sid, output_mode="json", **kwargs):
    """Manage the {search_id} search job."""
    endpoint = f"{base_url}{SEARCH_JOBS_SID.format(search_id=sid)}"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "output_mode": output_mode
    }

    if kwargs:
        params.update(kwargs)

    response = requests.get(endpoint, headers=headers,
                            params=params, verify=False)

    if response.status_code == 200:
        results = response.json()
        return results
    else:
        raise Exception(
            f"Code: {response.status_code}"
            f"Response: {response.text}"
        )


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
            time.sleep(5)
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
