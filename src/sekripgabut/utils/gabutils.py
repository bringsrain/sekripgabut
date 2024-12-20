import configparser
from datetime import datetime, timedelta, timezone
import re
import json
import logging
import os


def setup_logging(log_file="app.log", log_level=logging.INFO):
    """
    Configures the logging settings for the application.

    Args:
        log_file (str): The file where logs will be saved.
        log_level (int): The logging level (e.g., logging.INFO, logging.DEBUG).
    """
    # Clear any existing handlers to avoid duplicate logging
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),  # Logs to a file
            logging.StreamHandler()        # Logs to the console
        ]
    )


def load_config(config_file, required_sections=None):
    # Check if config file exists
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")

    config = configparser.ConfigParser()

    # Read the configuration file
    try:
        config.read(config_file)
        logging.info(f"Loaded config from {config_file}")
    except configparser.Error as e:
        logging.error(f"Failed to read config file: {e}")
        raise

    # Validate required sections and options
    if required_sections:
        for section, options in required_sections.items():
            if not config.has_section(section):
                logging.error(f"Missing section: {section}")
                raise configparser.NoSectionError(section)
            for option in options:
                if not config.has_option(section, option):
                    logging.error(
                        f"Missing option '{option}' in section '{section}'")
                    raise configparser.NoOptionError(section, option)
    return config


def parse_version(version_string):
    return tuple(map(int, version_string.split('.')))


def parse_date(date_str):
    """
    Parse various date formats into a consistent datetime object.
    Supported formats:
        - 2023-06-15T09:50:07.000+07:00
        - 2023-06-15T09:50:07
        - 2024/06/15:00:00:00
        - Splunk relative time modifiers like 'now', '-1d', '-2w@w1'
    """
    # Handle Splunk "now" explicitly
    if date_str.strip().lower() == "now":
        return datetime.now(timezone.utc)

    # Handle relative time modifiers (e.g., -1d, -2w@w1)
    relative_time_pattern = r"^(-?\d+)([smhdw])(?:@(w\d+))?$"
    match = re.match(relative_time_pattern, date_str.strip())

    if match:
        value, unit, anchor = match.groups()
        value = int(value)
        now = datetime.now(timezone.utc)

        # Map units to timedelta arguments
        unit_mapping = {
            "s": "seconds",
            "m": "minutes",
            "h": "hours",
            "d": "days",
            "w": "weeks",
        }

        if unit in unit_mapping:
            delta = timedelta(**{unit_mapping[unit]: value})
            result = now + delta

            # If there is an anchor (like @w1 for start of week)
            if anchor:
                if anchor.startswith("w"):  # Start of the week
                    weekday = int(anchor[1])  # Get the desired weekday (0=Mon)
                    result = result - timedelta(
                        days=result.weekday()) + timedelta(days=weekday)
                    result = result.replace(
                        hour=0, minute=0, second=0, microsecond=0)
            return result

    # Handle "T24:00:00" edge case
    if "T24:00:00" in date_str:
        date_without_time = date_str.split("T")[0]
        parsed_date = datetime.strptime(
            date_without_time, "%Y-%m-%d") + timedelta(days=1)
        return parsed_date.replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

    # Define possible patterns and their corresponding strptime formats
    date_formats = [
        "%Y-%m-%dT%H:%M:%S.%f%z",  # ISO 8601 with microseconds and timezone
        "%Y-%m-%dT%H:%M:%S.%f",    # ISO 8601 with microseconds
        "%Y-%m-%dT%H:%M:%S%z",     # ISO 8601 with timezone
        "%Y-%m-%dT%H:%M:%S",       # ISO 8601
        "%Y/%m/%d:%H:%M:%S",       # Alternative format
        "%Y-%m-%d",                # Date only
    ]

    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            # If offset-naive, make it offset-aware (UTC)
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            return parsed_date
        except ValueError:
            continue

    raise ValueError(f"Invalid date format: {date_str}")


def generate_weekly_ranges(start_date_input, end_date_input):
    """Generate weekly range from start_date to end_date"""
    # Parse input dates into datetime objects
    start_date = parse_date(start_date_input)
    end_date = parse_date(end_date_input)

    # Normalize both dates to remove fractional seconds
    start_date = start_date.replace(microsecond=0)
    end_date = end_date.replace(microsecond=0)

    # Adjust end_date to midnight if it isn't already
    if end_date.time() != datetime.min.time():
        end_date = (
            end_date.replace(hour=0, minute=0, second=0) + timedelta(days=1))

    # Prepare weekly date ranges
    date_ranges = []
    current_start = start_date

    while current_start < end_date:
        current_end = current_start + timedelta(
            days=6, hours=23, minutes=59, seconds=59
        )
        if current_end >= end_date:
            current_end = end_date - timedelta(seconds=1)

        # Append normalized dates to results
        date_ranges.append({
            "start": current_start.strftime("%Y-%m-%dT%H:%M:%S"),
            "end": current_end.strftime("%Y-%m-%dT%H:%M:%S"),
        })

        # Move to the next week's range
        current_start = current_end + timedelta(seconds=1)

    return date_ranges


def write_to_json_file(data, file_path, mode='w'):
    """
    Write data to a JSON file.

    Args:
        data (dict or list): The data to be written to the file.
        file_path (str): Path to the JSON file.
        mode (str): Mode to open the file ('w' for overwrite, 'a' for append).
                    Defaults to 'w'.

    Returns:
        bool: True if the file was written successfully, False otherwise.
    """
    try:
        if mode not in ('w', 'a'):
            raise ValueError("Mode must be 'w' for write or 'a' for append.")

        with open(file_path, mode) as file:
            if mode == 'a':
                # If appending, ensure JSON structure integrity
                file.seek(0, 2)  # Move to the end of the file
                if file.tell() == 0:
                    # Empty file, write directly
                    json.dump(data, file, indent=4)
                else:
                    # Read existing content, append new data
                    file.seek(0)  # Move to the start of the file
                    existing_data = json.load(file)
                    if not isinstance(existing_data, list):
                        raise ValueError("Appended JSON data must be a list.")
                    if not isinstance(data, list):
                        raise ValueError("Appended data must be a list.")
                    existing_data.extend(data)
                    file.seek(0)
                    json.dump(existing_data, file, indent=4)
            else:
                # Overwrite the file
                json.dump(data, file, indent=4)
        print(f"Data successfully written to {file_path}")
        return True
    except Exception as e:
        print(f"Error writing to JSON file: {e}")
        return False
