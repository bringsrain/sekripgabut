import logging
import configparser
import sys
import urllib3
import json
from sekripgabut.utils.gabutils import (
    setup_logging,
    load_config,
)
from sekripgabut.helpers import (
    args_helper,
    es_helpers,
    splunk_helpers,
)


CONFIG_FILE = "config.ini"


def main():
    setup_logging(log_file="sekripgabut.log", log_level=logging.DEBUG)
    args = args_helper.get_args(prog="sekripgabut")

    # Load configuration file
    try:
        if args.config:
            config = load_config(args.config)
        else:
            config = load_config(CONFIG_FILE)

        token = config.get('Auth', 'token')
        base_url = config.get('Splunk', 'base_url')

    except (FileNotFoundError, configparser.Error) as e:
        logging.critical(f"Error loading configuration: {str(e)}")
        return

    except Exception as e:
        logging.critical(f"Unexpected error: {str(e)}")
        return

    if args.test:
        print(token, base_url)

    if args.command == "es":
        # Load configuration file
        try:
            config = load_config(args.config)
        except (FileNotFoundError, configparser.Error) as e:
            logging.critical(f"Error loading configuration: {str(e)}")
            return

        except Exception as e:
            logging.critical(f"Unexpected error: {str(e)}")
            return

        earliest_time = getattr(args, 'earliest', '')
        latest_time = getattr(args, 'latest', 'now')

        if args.first_notable_index:
            logging.info("Fetching the first notable index time...")
            results = es_helpers.find_first_notable_time(
                config.get('Splunk', 'base_url'),
                config.get('Auth', 'token'),
                earliest_time=earliest_time,
                latest_time=latest_time
            )

            if results:
                logging.info(f"First notable index time: {results}")
            else:
                logging.error(
                    "Failed to retrieve the first notable index time")


if __name__ == "__main__":
    main()
