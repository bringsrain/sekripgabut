import logging
from sekripgabut.splunk_ops import introspection, search
import requests


def splunk_search(base_url, token, query, **kwargs):
    try:
        # Log the start of the search
        logging.info("Starting search...")

        # Start the search job and get the SID
        sid = search.set_search_jobs(base_url, token, query, **kwargs)
        logging.info(f"Search job started with SID: {sid}")

        # Fetch the search results
        logging.info("Fetching results...")
        results = search.get_search_results(base_url, token, sid, **kwargs)

        # Return the search results
        return results

    except requests.exceptions.RequestException as e:
        # Log network-related errors
        logging.error(f"Request failed: {e}")
    except ValueError as e:
        # Log data-related errors
        logging.error(f"Value error: {e}")
    except Exception as e:
        # Catch any unexpected errors
        logging.error(f"An unexpected error occurred: {e}")

    return None
