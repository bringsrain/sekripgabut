import os
import json
import logging

import jmespath
# import search
from sekripgabut.helpers import es_helpers
from sekripgabut.splunk_ops.search import (
    set_search_jobs,
    get_search_results,
)


def pemutihan(base_url, token, path, earliest_time, latest_time):
    """
    Clean up unclosed notable events. Fetch notable events based on
    a time range, save them to files in the specified directory,
    extract event IDs from the files, and close the notable events.

    Arguments:
        base_url -- Splunk instance base URL.
        token -- Splunk token access.
        path -- Directory or file path to store and read event data.
        earliest_time -- Start of the time range for fetching events.
        latest_time -- End of the time range for fetching events.
    """
    try:
        # Fetch unclosed notable events and save to files
        logging.info("Fetching unclosed notable events...")
        es_helpers.fetch_unclosed_notable_to_file(
            base_url,
            token,
            earliest_time=earliest_time,
            latest_time=latest_time,
            output_dir=path
        )
    except Exception as e:
        logging.error(f"Failed to fetch unclosed notable events: {e}")
        return

    # Validate the existence of the path
    if not os.path.exists(path):
        logging.error(f"Input {path} not found")
        return

    event_ids = []
    try:
        # Read JSON file from a file or directory
        if os.path.isfile(path):
            event_ids = _read_event_ids_from_file(path)
        else:
            event_ids = _read_event_ids_from_directory(path)

        # Extract event_id
        event_ids = [
            item['event_id'] for item in event_ids if 'event_id' in item
        ]

        if not event_ids:
            logging.warning("No valid event IDs found in the input.")
            return

        # Close notable events per batch
        batch_size = 8000
        for i in range(0, len(event_ids), batch_size):
            batch = event_ids[i:i + batch_size]
            logging.info(
                f"processing batch {i // batch_size + 1}:"
                f"{len(batch)} notable events..."
            )
            try:
                results = es_helpers.close_notable_event_by_event_id(
                    base_url,
                    token,
                    batch,
                )
                logging.info(
                    f":Batch {i // batch_size + 1} from: {len(event_ids)}"
                    f"results: {results}")
            except Exception as e:
                logging.error(
                    f"Error processing batch {i // batch_size + 1}"
                    f"from {len(event_ids)}: {e}")
    except Exception as e:
        logging.error(f"An error occurred during event processing: {e}")


def pemutihan_v2(base_url, token, earliest_time, latest_time):
    """
    Process and close notable events in a specified time range.

    Arguments:
        base_url (str): Base URL of the Splunk instance.
        token (str): Bearer token for authentication.
        earliest_time (str): Start time for processing notable events.
        latest_time (str): End time for processing notable events.
    """
    # Determine the time if not provided
    if not earliest_time:
        first_notable = es_helpers.find_first_notable_time(base_url, token)
        if (first_notable and isinstance(first_notable, list) and
                len(first_notable) > 0):
            earliest_time = first_notable[0].get("_time")
            logging.info(f"Derived earliest_time: {earliest_time}")

    query = """
    search `notable` | search (NOT `suppression` AND NOT status=5)
    """
    total_results = 0

    try:
        # Start the searach job
        logging.info("Starting search jobs...")
        sid = set_search_jobs(
            base_url=base_url,
            token=token,
            query=query,
            earliest_time=earliest_time,
            latest_time=latest_time,
            adhoc_search_level="smart",
            exec_mode="blocking",
        )
        logging.info(f"Search job started with search ID: {sid}")

        # Fetch search results
        results = get_search_results(base_url, token, sid)
        total_results = len(results)
        logging.info(f"Total notable events found: {total_results}")

    except Exception as e:
        logging.error(f"Error starting search or fetching results: {e}")
        return

    if not total_results:
        logging.info("No notable event found in the specified range.")
        return

    closed_count = 0
    try:
        while closed_count < total_results:
            logging.info(f"Closing notable events for SID: {sid}")
            update_results = es_helpers.close_notable_event_by_sid(
                base_url, token, sid)

            # Process the response
            success = jmespath.search("success", update_results)
            if success:
                success_count = jmespath.search(
                    "success_count", update_results)
                failure_count = jmespath.search(
                    "failure_count", update_results)
                message = (jmespath.search("message", update_results) or
                           ("No details available."))

                closed_count += success_count
                if failure_count:
                    logging.warning(
                        f"Failed to close: {failure_count} notable events."
                        f"Message: {message}"
                    )
                    break
                logging.info(
                    f"Successfully closed {success_count} notable events."
                    f"Total closed: {closed_count}"
                )
            else:
                logging.error(f"Failed to close notable events."
                              f"Response: {update_results}")
                break
    except Exception as e:
        logging.error(f"Error closing notable events: {e}")

    logging.info(f"Closed notable event: {closed_count}")


def _read_event_ids_from_file(file_path):
    """
    Read event data from a single JSON file.

    Arguments:
        file_path -- Path to the JSON file.

    Returns:
        list -- Parsed JSON content.
    """
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (OSError, IOError) as e:
        raise RuntimeError(f"Failed to read file {file_path}: {e}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in file {file_path}: {e}")


def _read_event_ids_from_directory(directory_path):
    """
    Read event data from all JSON files in a directory.

    Arguments:
        directory_path -- Path to the directory containing JSON files.

    Returns:
        list -- Aggregated JSON content from all files.
    """
    event_ids = []
    try:
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                event_ids.extend(_read_event_ids_from_file(file_path))
    except Exception as e:
        raise RuntimeError(
            f"Failed to process directory {directory_path}: {e}")
    return event_ids
