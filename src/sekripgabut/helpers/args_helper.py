import argparse


def add_global_arguments(parser):
    """Add global arguments to the parser."""
    parser.add_argument(
        "--config",
        help="Load config file",
    )
    parser.add_argument(
        "--test",
        help="Quick call to the test use case",
        action="store_true",
    )


def add_es_arguments(parser):
    """Add arguments for 'es' subcommand"""
    parser.add_argument(
        "--config",
        help="Load config file"
    )
    parser.add_argument(
        "--first-notable-index",
        action="store_true",
        help="Find first notable index time",
    )
    parser.add_argument(
        "--weekly-unclosed-notable",
        action="store_true",
        help=("""
              Fetch un-closed notables in time range to file,
              split them weekly""")
    )
    parser.add_argument(
        "--update-notable",
        help="Update notable event"
    )
    parser.add_argument(
        "--close-notable",
        help="Close notable event by event_id or sid",
    )
    parser.add_argument(
        "--earliest",
        help="Start time to search"
    )
    parser.add_argument(
        "--latest",
        help="End time to search"
    )
    parser.add_argument(
        "--path",
        help="Output file or directory"
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
    parser.add_argument(
        "--config",
        help="Load Splunk config.ini file"
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


def add_pemutihan_arguments(parser):
    """Add arguments for 'pemutihan' command"""
    parser.add_argument(
        "ver",
        nargs="?",
        help="Optional pemutihan v2"

    )
    parser.add_argument(
        "--config",
        required=True,
        help="Load splunk config"
    )
    parser.add_argument(
        "--path",
        required=False,
        help="Path to file that contains event_id"
    )
    parser.add_argument(
        "--earliest",
        help="Start time to search"
    )
    parser.add_argument(
        "--latest",
        help="End time to search"
    )


def get_args(**kwargs):
    """Build the arguments parsers"""
    parser = argparse.ArgumentParser(
        description="Swiss army tools hasil gabut yang mungkin saja useless",
        **kwargs,
    )

    # Add global arguments
    add_global_arguments(parser)

    # Define command subparser
    subparsers = parser.add_subparsers(dest="command", required=False)

    # Define 'es' command
    es_parser = subparsers.add_parser(
        "es",
        help="Collection of Splunk Enterprise Security operations"
    )

    # Pemutihan cuy
    pemutihan_parser = subparsers.add_parser(
        "pemutihan",
        help="Bersih-bersih..."
    )

    splunk_parser = subparsers.add_parser(
        "splunk",
        help="Collection of Splunk Enterprise operations"
    )

    # Add 'es' arguments
    add_es_arguments(es_parser)

    # Add 'pemutihan' arguments
    add_pemutihan_arguments(pemutihan_parser)

    # Add 'splunk' arguments
    add_splunk_arguments(splunk_parser)

    splunk_subparsers = splunk_parser.add_subparsers(
        dest="subcommand", required=False
    )
    # Define 'splunk search' subcommand
    search_parser = splunk_subparsers.add_parser(
        "search",
        help="Collection of splunk search endpoints operations"
    )

    # Add 'splunk search' arguments
    add_search_arguments(search_parser)

    return parser.parse_args()
