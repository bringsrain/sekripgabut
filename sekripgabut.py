import logging
import urllib3
import argparse
import os
# import time
import json
from gabutils.gabutils import (
    setup_logging,
    load_config,
    generate_weekly_ranges,
    parse_version,
    write_to_json_file)
from gabutils import gabutargs as gargs
from splunk_ops import introspection, search


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_FILE = "config.ini"


def splunk_search(base_url, token, query, **kwargs):
    try:
        print("Starting search...")
        sid = search.set_search_jobs(base_url, token, query, **kwargs)
        print(f"Search job started with SID: {sid}")

        print("Fetching results...")
        results = search.get_search_results(base_url, token, sid, **kwargs)
        return results
    except Exception as e:
        print(e)
        return []


def find_first_notable_time(base_url, token):
    query = "| tstats earliest(_time) AS _time WHERE index=notable"
    results = splunk_search(base_url, token, query, earliest_time="",
                            latest_time="now")
    return results


def get_unclosed_notable_event(base_url, token,
                               earliest_time="", latest_time="now",
                               output_dir="unclosed-notables"):
    """Get all un-closed notable events since the {earliest_time}
    till the {latest_time}

    Arguments:
    base_url -- Splunk instance base URL
    token -- Splunk access token

    Keyword arguments:
    earliest_time -- Search start time. Default: First indexed notable event.
    latest_time -- Search end time, Default: now()
    output_dir -- Output directory to write the output JSON file to, this will
    rewrite if the directory exists.

    Returns:
    bool: True if the process completes successfully, False otherwise.
    """
    try:
        # Determine earliest_time
        if earliest_time:
            start_date_input = earliest_time
        else:
            logging.info("Find the first indexed notable event time.")
            first_notable = find_first_notable_time(base_url, token)
            # If first notable exists
            if first_notable:
                start_date_input = first_notable[0]['_time']
                logging.info(
                    f"First indexed notable event time found:"
                    f"{start_date_input}")
            else:
                logging.error("No earliest time found. Exiting.")
                raise ValueError("Earliest time value is empty")

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        logging.info(f"Output directory is set to: {output_dir}")

        # Generate weekly ranges
        dates = generate_weekly_ranges(start_date_input, latest_time)
        logging.info(f"Generated {len(dates)} weekly date ranges.")

        query = """
        search `notable`
        | search (NOT `suppression` AND status!=5)
        | table event_id"""

        # Search all un-closed notable and write to file
        for date in dates:
            # Get notable event_id
            earliest = date["start"]
            latest = date["end"]
            output_file = os.path.join(output_dir,
                                       f"{earliest[:10]}_{latest[:10]}.json")
            try:
                logging.info(
                    f"Fetching notable events from {earliest} to {latest}.")
                notable_events = splunk_search(
                    base_url, token, query,
                    earliest_time=earliest, latest_time=latest)

                # Write results to json
                if write_to_json_file(notable_events, output_file):
                    logging.info(
                        f"Result successfully saved to: {output_file}")
                else:
                    logging.warning(
                        f"Failed to write results for range"
                        f"{earliest} to {latest}.")
            except Exception as e:
                logging.error(
                    f"Error processing range {earliest} to {latest}: {e}")
        logging.info(f"All files saved to: {output_dir}")
        return True
    except Exception as e:
        logging.critical(f"Failed to retrieve un-closed notable events: {e}")
        return False


def close_notable_event(base_url, token):
    pass


def main():
    setup_logging(log_file="sekripgabut.log", log_level=logging.DEBUG)
    parser = argparse.ArgumentParser(
        description="Sekrip hasil kegabutan sehari-hari"
    )

    # Add global arguments
    gargs.add_global_arguments(parser)

    # Define command subparser
    subparsers = parser.add_subparsers(dest="command", required=False)

    # Define 'es' command
    es_parser = subparsers.add_parser(
        "es",
        help="Collection of Splunk Enterprise Security operations"
    )

    # Add 'es' arguments
    gargs.add_es_arguments(es_parser)

    splunk_parser = subparsers.add_parser(
        "splunk",
        help="Collection of splunk operations"
    )
    # Add 'splunk' arguments
    gargs.add_splunk_arguments(splunk_parser)

    splunk_subparsers = splunk_parser.add_subparsers(
        dest="subcommand", required=False
    )
    # Define 'splunk search' subcommand
    search_parser = splunk_subparsers.add_parser(
        "search",
        help="Collection of splunk search endpoints operations"
    )

    # Add 'splunk search' arguments
    gargs.add_search_arguments(search_parser)

    args = parser.parse_args()

    # Load config
    if args.config:
        config = load_config(args.config)
    else:
        config = load_config(CONFIG_FILE)

    token = config.get('Auth', 'token')
    base_url = config.get('Splunk', 'base_url')

    # Quick testing
    if args.test:
        testing = get_unclosed_notable_event(
            base_url, token,
            earliest_time="-15m",
            latest_time="now",
            output_dir="testing_dir")
        if testing:
            print("sukses")
        else:
            print("gagal coeg!")

    # Get full splunk instance info
    if (args.command == "splunk" and args.info):
        splunk_info = introspection.get_server_info(base_url, token)
        print(json.dumps(splunk_info, indent=4))

    # Get splunk version
    if (args.command == "splunk" and args.version):
        splunk_version = introspection.get_splunk_version(base_url, token)
        print(splunk_version)

    # Get all splunk's search jobs
    if (args.command == "splunk" and
            args.subcommand == "search" and args.get_search_jobs):
        try:
            print(search.get_search_jobs(base_url, token))
        except Exception as e:
            print(e)

    # Do splunk search
    if (args.command == "splunk" and
            args.subcommand == "search" and args.search):
        query = args.search
        # initiate a dictionary to dynamically add arguments
        search_kwargs = {}

        # Check either earliest or latest argument is not empty
        if args.earliest:
            search_kwargs['earliest_time'] = args.earliest
        if args.latest:
            search_kwargs['latest_time'] = args.latest

        try:
            print(splunk_search(
                base_url, token, query, **search_kwargs))
        except Exception as e:
            print(e)

    # Manage the search job by SID
    if (args.command == "splunk" and
            args.subcommand == "search" and args.get_search_jobs_sid):
        sid = args.get_search_jobs_sid
        add_kwargs = {}

        if args.earliest:
            add_kwargs['earliest_time'] = args.earliest
        if args.latest:
            add_kwargs['latest_time'] = args.latest

        try:
            print(search.get_search_jobs_sid(
                base_url, token, sid, **add_kwargs))
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
