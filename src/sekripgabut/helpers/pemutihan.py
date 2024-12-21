import os
import json
import logging
# import search
from sekripgabut.helpers import es_helpers


def pemutihan(base_url, token, path, earliest_time, latest_time):
    """Bersih-bersih notable event yang belom ditutup. Fetch notable event
    berdasarkan time range. Save ke file dalam direktori {path}. Tarik event_id
    dari dalam file, tutup notable berdasarkan 'event_id'"""

    try:
        es_helpers.fetch_unclosed_notable_to_file(
            base_url,
            token,
            earliest_time=earliest_time,
            latest_time=latest_time,
            output_dir=path
        )
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")
        return

    if not os.path.exists(path):
        logging.error(f"Input {path} not found")
        return

    event_ids = []
    try:
        # Handle single file
        if os.path.isfile(path):
            with open(path, "r") as notables:
                event_ids = json.load(notables)
        else:
            # Handle a directory of files
            for file in os.listdir(path):
                notable_file = os.path.join(path, file)
                if os.path.isfile(notable_file):
                    with open(notable_file, "r") as notables:
                        event_ids.extend(json.load(notables))

        # Extract event_id
        event_id = [
            item['event_id'] for item in event_ids if 'event_id' in item
        ]

        if not event_id:
            logging.warning("No valid event IDs found in the input.")

        results = es_helpers.close_notable_event_by_event_id(
            base_url,
            token,
            event_id
        )
        logging.info(f"{results}")
    except (OSError, IOError) as e:
        logging.error(f"File operation failed: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
