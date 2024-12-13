import requests
import json
import configparser
import argparse
import urllib3
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename='example.log',
    filemode='w',
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def close_notables(base_url, token, rule_id, file=None):
    endpoint = f"{base_url}/services/notable_update"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        'ruleUIDs': rule_id,
        'newOwner': 'maxplus',
        'comment': "Mass close old events",
        'status': 5
    }

    response = requests.post(
        endpoint, headers=headers, data=data, verify=False)

    if response.status_code != 200:
        raise Exception(
            logger.error(
                f"Failed to update {file if file else rule_id}:"
                f"{response.text}")
        )

    return print(response.text), logger.info(response.text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--split",
        help="Split notables json file into chunks"
    )
    parser.add_argument(
        "--test",
        help="Run testing block code",
        action="store_true"
    )
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read("fs.ini")
    token = config["Auth"]["token"]
    base_url = config["Splunk"]["base_url"]
    notables_dir = "notable_chunks"

    if args.split:
        input_file = args.split
        output_dir = notables_dir

        os.makedirs(output_dir, exist_ok=True)

        with open(input_file, "r") as file:
            lines = file.readlines()
            chunk_size = 30
            total_chunk = (len(lines) + chunk_size - 1) // chunk_size
            for i in range(total_chunk):
                chunk_lines = lines[i * chunk_size:(i + 1) * chunk_size]
                json_list = [json.loads(line.strip()) for line in chunk_lines]
                chunk_file_path = os.path.join(
                    output_dir, f"chunk_{i + 1}.json")
                with open(chunk_file_path, "w") as chunk_file:
                    json.dump(json_list, chunk_file, indent=4)

                print(f"Saved chunk {i + 1} to {chunk_file_path}")
    elif args.test:
        pass
    else:
        notable_files = os.listdir(notables_dir)
        for file in notable_files:
            notable_file = os.path.join(notables_dir, file)
            with open(notable_file, "r") as notable_file:
                notables = json.load(notable_file)

            ruleUIDs = [item['result']['event_id'] for item in notables]

            try:
                close_notables(base_url, token, ruleUIDs, file)
            except Exception as e:
                print(f"Error: {e}")
                logger.error(e)


if __name__ == "__main__":
    main()
