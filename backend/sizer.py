#!/usr/bin/env python3
# sizer.py v1.5
#
# Calculates the size of Ubuntu repositories for airgapped mirroring.
# Supports specifying an output path with `--output`.

import os
import json
import requests
import argparse

def calculate_size(index_uri):
    """Calculate size by parsing the index file."""
    try:
        response = requests.get(index_uri)
        return sum(int(line.split()[1]) for line in response.text.splitlines() if 'Size:' in line)
    except Exception:
        return 0

def main():
    parser = argparse.ArgumentParser(description="Ubuntu Repository Sizer")
    parser.add_argument("-i", "--input", required=True, help="Input JSON data file")
    parser.add_argument("-o", "--output", required=True, help="Output JSON file path")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        repo_data = json.load(f)

    for repo in repo_data:
        for release in repo_data[repo]:
            for suite in repo_data[repo][release]:
                for component in repo_data[repo][release][suite]:
                    for entry in repo_data[repo][release][suite][component]:
                        entry["size"] = calculate_size(entry["index_uri"])

    with open(args.output, "w") as f:
        json.dump(repo_data, f, indent=4)

    print(f"Size calculation complete. Data saved to {args.output}")

if __name__ == "__main__":
    main()
