import urllib3
import argparse
import os
import time
import json
from gabutils.gabutils import load_config
from splunk_ops import introspection, search


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_FILE = "config.ini"


def splunk_search(base_url, token, query, **kwargs):
    try:
        if kwargs:
            print("Starting search...")
            sid = search.set_search_jobs(base_url, token, query, **kwargs)
            print(f"Search job started with SID: {sid}")

        else:
            print("Starting search...")
            sid = search.set_search_jobs(base_url, token, query)
            print(f"Search job started with SID: {sid}")

        while True:
            search_jobs_info = search.get_search_jobs_sid(
                base_url, token, sid, **kwargs)
            search_jobs_status = search_jobs_info["entry"][0]["content"]
            if search_jobs_status["dispatchState"] == "DONE":
                print("Search job completed")
                return
            print("waiting for job to complete")
            time.sleep(5)
    except Exception as e:
        print(e)
        return e


def main():
    parser = argparse.ArgumentParser(
        description="Sekrip hasil kegabutan sehari-hari"
    )

    # Global argument
    parser.add_argument(
        "--config",
        help="Load config .ini file"
    )

    # Define main subparsers for primary commands
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 'splunk' command
    splunk_parser = subparsers.add_parser(
        "splunk",
        help="Collection of splunk operations"
    )
    splunk_subparsers = splunk_parser.add_subparsers(
        dest="subcommand", required=True
    )

    # 'splunk introspection' subcommand
    introspection_parser = splunk_subparsers.add_parser(
        "introspection",
        help="Collection of splunk introspection endpoints operations"
    )
    introspection_parser.add_argument(
        "--splunkinfo",
        help="Return full info of splunk instance",
        action="store_true"
    )
    introspection_parser.add_argument(
        "--splunkversion",
        help="Return splunk instance version",
        action="store_true"
    )

    # 'splunk search' subcommand
    search_parser = splunk_subparsers.add_parser(
        "search",
        help="Collection of splunk search endpoints operations"
    )
    # 'splunk search' parameters
    search_parser.add_argument(
        "--get-search-jobs",
        help="Split notables json file into chunks",
        action="store_true"
    )

    search_parser.add_argument(
        "--search",
        help="Input your SPL query here"
    )

    search_parser.add_argument(
        "--earliest",
        help="earliest search time range. Default to -24h"
    )

    search_parser.add_argument(
        "--latest",
        help="Latest search time range. Default to now()"
    )

    search_parser.add_argument(
        "--get-search-jobs-sid",
        help="Get detail info about search job by search id"
    )

    args = parser.parse_args()

    # Load config
    if args.config:
        config = load_config(args.config)
    else:
        config = load_config(CONFIG_FILE)

    token = config.get('Auth', 'token')
    base_url = config.get('Splunk', 'base_url')

    # Get full splunk instance info
    if (args.command == "splunk" and args.subcommand == "introspection"
            and args.splunkinfo):
        splunk_info = introspection.get_server_info(base_url, token)
        print(json.dumps(splunk_info, indent=4))

    # Get splunk version
    if (args.command == "splunk" and args.subcommand == "introspection"
            and args.splunkversion):
        splunk_version = introspection.get_splunk_version(base_url, token)
        print(splunk_version)

    # Get all splunk's search jobs
    if (args.command == "splunk" and
            args.subcommand == "search" and args.get_search_jobs):
        try:
            print(search.get_search_jobs(base_url, token))
        except Exception as e:
            print(e)

    # Start a splunk searhing and return the SID
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
