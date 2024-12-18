import argparse


def add_global_arguments(parser):
    """Add global arguments to the parser."""
    parser.add_argument(
        "--config",
        help="Load config file"
    )
    parser.add_argument(
        "--test",
        help="Quick call to the test use case",
        action="store_true"
    )


def add_es_arguments(parser):
    """Add arguments for 'es' subcommand"""
    parser.add_argument(
        "--update-notable",
        help="Update notable event"
    )
    parser.add_argument(
        "--earliest",
        help="Start time to search"
    )
    parser.add_argument(
        "--latest",
        help="End time to search"
    )


def add_splunk_arguments(parser):
    """Add arguments for 'introspection' subcommand"""
    parser.add_argument(
        "--info",
        help="Return full info of splunk instance",
        action="store_true"
    )
    parser.add_argument(
        "--version",
        help="Return splunk instance version",
        action="store_true"
    )


def add_search_arguments(parser):
    """Add arguments for 'search' subcommand"""
    parser.add_argument(
        "--get-search-jobs",
        help="Split notables json file into chunks",
        action="store_true"
    )
    parser.add_argument(
        "--search",
        help="Input your SPL query here"
    )
    parser.add_argument(
        "--earliest",
        help="earliest search time range. Default to -24h"
    )
    parser.add_argument(
        "--latest",
        help="Latest search time range. Default to now()"
    )
    parser.add_argument(
        "--get-search-jobs-sid",
        help="Get detail info about search job by search id"
    )
    parser.add_argument(
        "--unclosed-notables",
        help="Get un-closed notable events"
    )
