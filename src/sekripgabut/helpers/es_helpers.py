import logging
import os
import shutil
from sekripgabut.es_ops import es_api
from sekripgabut.helpers import splunk_helpers
from sekripgabut.utils.gabutils import (
    generate_weekly_ranges,
    write_to_json_file,
)


def find_first_notable_time(base_url, token,
                            earliest_time="", latest_time="now"):
    query = "| tstats earliest(_time) AS _time WHERE index=notable"
    try:
        results = splunk_helpers.splunk_search(
            base_url, token, query,
            earliest_time=earliest_time,
            latest_time=latest_time,
            )
        if not results:
            logging.warning(
                "No results found for the first notable index time")
            return None
        return results
    except Exception as e:
        logging.error(f"Failed to retrieve the first notable index time: {e}")
        return None


def fetch_unclosed_notable_to_file(
        base_url,
        token,
        earliest_time=None,
        latest_time="now",
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
        if os.path.exists(output_dir):
            logging.info(f"{output_dir} exists. Overwrite.")
            shutil.rmtree(output_dir)
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
                notable_events = splunk_helpers.splunk_search(
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


def close_notable_event_by_event_id(base_url, token, event_id, **kwargs):
    results = es_api.update_notable_event(base_url, token, status=5,
                                          ruleUIDs=event_id, **kwargs)
    return results


def close_notable_event_by_sid(base_url, token, sid, **kwargs):
    results = es_api.update_notable_event(base_url, token, status=5,
                                          searchID=sid, **kwargs)
    return results
