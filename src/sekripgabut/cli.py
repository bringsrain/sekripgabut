import logging
import configparser
# import sys
# import urllib3
import json
from sekripgabut.splunk_ops.introspection import (
    get_server_info,
    get_splunk_version,
)
from sekripgabut.utils.gabutils import (
    setup_logging,
    load_config,
)
from sekripgabut.helpers import (
    args_helper,
    es_helpers,
    # splunk_helpers,
    pemutihan,
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
        elif args.weekly_unclosed_notable:
            path = getattr(args, 'path', "unclosed-notables")
            results = es_helpers.fetch_unclosed_notable_to_file(
                base_url,
                token,
                earliest_time=earliest_time,
                latest_time=latest_time,
                output_dir=path
            )

            if results:
                logging.info("Un-closed notable fetched")
            else:
                logging.critical("Failed to fetch notables")
        else:
            logging.error("Invalid 'es' subcommand argument(s)")

    if args.command == "splunk":
        if args.info:
            try:
                splunk_info = get_server_info(base_url, token)
                print(json.dumps(splunk_info, indent=4))
            except Exception as e:
                logging.error(f"Failed to get splunk instance info: {e}")

        if args.version:
            try:
                version = get_splunk_version(base_url, token)
                print(version)
            except Exception as e:
                logging.error(f"Unexpected error occurred: {e}")

    if args.command == "pemutihan":
        if args.ver == "v2":
            # Extract time range arguments
            earliest = getattr(args, 'earliest', None)
            latest = getattr(args, 'latest', 'now')

            # Validate log arguments
            if not earliest:
                logging.warning(
                    "No 'earliest' provided; using default (None)."
                )

            if latest == 'now':
                logging.info(
                    "No 'latest' time provided; using default ('now')."
                )

            # Call pemutihan v2 function
            try:
                pemutihan.pemutihan_v2(
                    base_url, token, earliest, latest
                )
            except Exception as e:
                logging.critical(f"Failed to execute 'pemutihan_v2': {e}")

        elif args.ver is None:
            # Extract time range arguments
            earliest = getattr(args, 'earliest', None)
            latest = getattr(args, 'latest', 'now')

            # Validate an log arguments
            if not args.path:
                logging.error("Path is required for the 'pemutihan' command.")
                return

            if not earliest:
                logging.warning(
                    "No 'earliest' time provided; using default (None).")

            if latest == 'now':
                logging.info(
                    "'latest' time not provided; using default ('now').")

            # Call the pemutihan function
            try:
                pemutihan.pemutihan(
                    base_url, token, args.path, earliest, latest)
            except Exception as e:
                logging.critical(f"Failed to execute 'pemutihan': {e}")
        else:
            print(f"Error: unknown version '{args.ver}'")


if __name__ == "__main__":
    main()
