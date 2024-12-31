import os
import json
import logging
from time import sleep

import jmespath
import requests
# import search
from sekripgabut.helpers import es_helpers
from sekripgabut.splunk_ops.search import (
    get_search_job_by_sid,
    set_search_jobs,
    get_search_results,
)
from sekripgabut.utils.gabutils import (
    generate_daily_ranges,
    generate_weekly_ranges
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


def pemutihan_v2(
        base_url,
        token,
        earliest_time,
        latest_time,
        offset=0,
        batch_size=3000):
    """
    Process and close notable events in a specified time range.

    Arguments:
        base_url (str): Base URL of the Splunk instance.
        token (str): Bearer token for authentication.
        earliest_time (str): Start time for processing notable events.
        latest_time (str): End time for processing notable events.
    """
    # TODO:
    # - Check status. dispatchState, isDone?
    # - Find valid results count. eventAvailableCount, eventCount, resultCount,
    #   scanCount
    # - Compare final closed result (offset accumulated) with the real results
    #   count
    # - Repeat close notable events by event_id
    #   while closed_notables < results count
    # event_available_count = None
    # result_count = None

    if earliest_time:
        start_date = earliest_time
    else:
        first_notable = es_helpers.find_first_notable_time(base_url, token)
        if isinstance(first_notable, dict):
            start_date = first_notable["_time"]
        else:
            logging.warning(
                """ No notable event found on this instance.
                or check your earliest time input.""")
            return

    dates = generate_daily_ranges(start_date, latest_time)

    query = """
    search `notable`
    | search (NOT `suppression` AND NOT status=5)
    """

    for date in dates:
        earliest_time = date["start"]
        latest_time = date["end"]

        dispatch_state = None
        event_count = None
        # For reports
        successes_count = 0
        success_count = 0
        failures_count = 0
        failure_count = 0
        total_processed = 0
        total_final_proccessed = 0

        while True:
            # Determine the time if not provided

            logging.info(
                f"'Pemutihan' will start from {earliest_time} "
                f"till {latest_time}.")

            try:
                # Start the search job
                logging.debug("Starting search jobs...")
                sid = set_search_jobs(
                    base_url=base_url,
                    token=token,
                    query=query,
                    earliest_time=earliest_time,
                    latest_time=latest_time,
                    adhoc_search_level="smart",
                )
                logging.info(f"Jobs {sid} is Done.")
            except Exception as e:
                logging.error(f"Failed to set the search jobs: {e}")
                return

            # Wait for search jobs to complete
            try:
                while True:
                    # Monitoring {sid} search job status isDone.
                    job_info = get_search_job_by_sid(base_url, token, sid)

                    is_done = jmespath.search(
                        "entry[0].content.isDone", job_info)
                    dispatch_state = jmespath.search(
                        "entry[0].content.dispatchState", job_info)
                    # event_available_count = jmespath.search(
                    #     "entry[0].content.eventAvailableCount", job_info)
                    event_count = jmespath.search(
                        "entry[0].content.eventCount", job_info)
                    # result_count = jmespath.search(
                    #     "entry[0].content.resultCount", job_info)

                    logging.info(
                        f"Job status: dispatchState={dispatch_state},"
                        f"eventCount={event_count}, isDone={is_done}"
                    )

                    if is_done:
                        break

                    sleep(3)

            except Exception as e:
                logging.error(f"Error while monitoring job {sid}: {e}")
                return

            if not event_count or event_count == 0:
                logging.info("===============================================")
                logging.info(f"Time range: {earliest_time} -- {latest_time}")
                logging.info(f"Successfully closed: {successes_count}")
                logging.info(f"Failed to close: {failures_count}")
                logging.info(
                    f"Total processed events: {total_final_proccessed}")
                logging.info("===============================================")
                break

            # Fetch and update notable event
            endpoint = f"{base_url}/services/search/jobs/{sid}/results"
            headers = {"Authorization": f"Bearer {token}"}

            while total_processed < event_count:
                # Fetch search results
                payload = {
                    "output_mode": "json",
                    "offset": offset,
                    "count": batch_size,
                }

                # fetch the results
                try:
                    r = requests.get(
                        endpoint,
                        headers=headers, params=payload, verify=False)
                    r.raise_for_status()

                    results = r.json()

                    event_ids = jmespath.search("results[*].event_id", results)

                    # if not isinstance(event_ids, list):
                    #     logging.error(
                    #         f"Event IDs content: {event_ids}"
                    #         f"Event IDs type: {type(event_ids)}"
                    #     )
                    #     return

                    if not event_ids:
                        results_message = jmespath.search("messages", results)
                        if event_count > 0:
                            print("======")
                            print(json.dumps(results, indent=4))
                            print("======")
                            break
                        logging.info(
                            f"Event IDs not found:"
                            f"{results_message}"
                        )
                        logging.info(
                            "======================")
                        logging.info(
                            f"Time range: {earliest_time} -- {latest_time}")
                        logging.info(f"Event Count: {event_count}")
                        logging.info(f"Successfully closed: {success_count}")
                        logging.info(f"Failed to close: {failure_count}")
                        logging.info(
                            f"Total processed events: {total_processed}")
                        logging.info(
                            "======================")
                        break

                    close_results = es_helpers.close_notable_event_by_event_id(
                        base_url, token, event_ids)

                    if isinstance(close_results, dict):
                        message = jmespath.search("message", close_results)
                        success_count = jmespath.search(
                            "success_count", close_results
                        )
                        failure_count = jmespath.search(
                            "failure_count", close_results
                        )
                        success = jmespath.search("success", close_results)
                        details = jmespath.search("details", close_results)

                        successes_count += success_count
                        failures_count += failure_count
                        total_processed += len(event_ids)
                        logging.info(
                            f"Success = {success},"
                            f"Total processed = {total_processed}"
                        )
                        logging.info(
                            f"Current processed notable = "
                            f"{success_count}/{event_count}"
                        )
                        if failure_count:
                            logging.info(f"Failures count = {failures_count}")
                            logging.info(f"Success = {success}")
                            logging.info(f"Message = {message}")
                            logging.info(f"Details = {details}")
                            return

                        logging.debug("Batch update success!")
                    else:
                        logging.error(f"Failed processing {batch_size} batch.")
                        break

                    total_final_proccessed += total_processed
                    offset += batch_size

                except Exception as e:
                    logging.error(
                        f"Error processing batch starting at offset {offset}: "
                        f"{e}")
                    return

            if total_processed < event_count:
                logging.info("=================")
                logging.info(
                    f"""
                    Rechecking for remaining notable events.
                    Proccesed: {total_final_proccessed}
                    Closed: {successes_count} successfully
                    """
                )
                logging.info("=================")

                total_processed = 0
                offset = 0
                continue
            logging.info("===============================================")
            logging.info(f"Time range: {earliest_time} -- {latest_time}")
            logging.info(f"Successfully closed: {successes_count}")
            logging.info(f"Failed to close: {failures_count}")
            logging.info(
                f"Total processed events: {total_final_proccessed}")
            logging.info("===============================================")
            break


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
