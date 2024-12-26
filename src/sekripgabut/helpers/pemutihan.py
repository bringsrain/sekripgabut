import os
import json
import logging
# import search
from sekripgabut.helpers import es_helpers


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
        event_id = [
            item['event_id'] for item in event_ids if 'event_id' in item
        ]

        if not event_id:
            logging.warning("No valid event IDs found in the input.")
            return

        # Close notable events
        logging.info(f"Closing {len(event_id)} notable event...")
        results = es_helpers.close_notable_event_by_event_id(
            base_url,
            token,
            event_id
        )
        logging.info(f"Successfully closed events: {results}")
    except Exception as e:
        logging.error(f"An error occurred during event processing: {e}")


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
