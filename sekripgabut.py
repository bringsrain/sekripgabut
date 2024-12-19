import logging
import urllib3
import argparse
# import time
import json
from utils.gabutils import (
    setup_logging,
    load_config,
)
from helpers import (
    args_helper,
    splunk_helpers,
    es_helpers,
)
from splunk_ops import introspection, search
from es_ops import es_api


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_FILE = "config.ini"


def main():
    setup_logging(log_file="sekripgabut.log", log_level=logging.DEBUG)
    parser = argparse.ArgumentParser(
        description="Sekrip hasil kegabutan sehari-hari"
    )

    # Add global arguments
    args_helper.add_global_arguments(parser)

# Define command subparser
    subparsers = parser.add_subparsers(dest="command", required=False)

    # Define 'es' command
    es_parser = subparsers.add_parser(
        "es",
        help="Collection of Splunk Enterprise Security operations"
    )

    # Add 'es' arguments
    args_helper.add_es_arguments(es_parser)

    splunk_parser = subparsers.add_parser(
        "splunk",
        help="Collection of splunk operations"
    )
    # Add 'splunk' arguments
    args_helper.add_splunk_arguments(splunk_parser)

    splunk_subparsers = splunk_parser.add_subparsers(
        dest="subcommand", required=False
    )
    # Define 'splunk search' subcommand
    search_parser = splunk_subparsers.add_parser(
        "search",
        help="Collection of splunk search endpoints operations"
    )

    # Add 'splunk search' arguments
    args_helper.add_search_arguments(search_parser)

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
        query = ("""search `notable`
                 | search (NOT `suppression` AND NOT status=5)""")
        earliest_time = "-30m"
        latest_time = "now"

        sid = search.set_search_jobs(base_url, token, query,
                                     earliest_time=earliest_time,
                                     latest_time=latest_time
                                     )
        print(sid)
        event_ids = search.get_search_results(base_url, token, sid,
                                              earliest_time=earliest_time,
                                              latest_time=latest_time)
        print(event_ids)
        event_id = [item['event_id'] for item in event_ids]
        print(event_id)
        try:
            event = es_helpers.close_notable_event_by_sid(
                base_url, token, sid)
            logging.info(f"event: {event}")
        except Exception as e:
            logging.error(e)

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
            print(splunk_helpers.splunk_search(
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
