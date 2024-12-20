import os
import json
import logging
# import search
import es_helpers


def pemutihan(base_url, token, path):
    event_id = []
    if os.path.exists(path):
        if os.path.isfile(path):
            with open(path, "r") as notables:
                notables = json.load(path)

            print(json.dumps(notables, indent=4))

        # results = es_helpers.close_notable_event_by_event_id(base_url, token, event_id)
        # logging.info(f"{results}")
    else:
        logging.error(f"Input {path} Not found!")
