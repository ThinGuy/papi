#!/usr/bin/env python3
# parser.py v1.5
#
# Parses copyright data and converts detected licenses to SPDX identifiers.

import json
import argparse

LICENSE_MAP = {
    "GPL-3": "GPL-3.0-only",
    "MIT": "MIT",
    "Apache 2.0": "Apache-2.0",
}

def parse_licenses(input_path, output_path):
    with open(input_path, 'r') as f:
        data = json.load(f)

    for repo in data:
        for release in data[repo]:
            for suite in data[repo][release]:
                for component in data[repo][release][suite]:
                    for entry in data[repo][release][suite][component]:
                        entry["spdx_license"] = LICENSE_MAP.get(entry.get("license", ""), "UNKNOWN")

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ubuntu Licensing Parser")
    parser.add_argument("-i", "--input", required=True, help="Input JSON data file")
    parser.add_argument("-o", "--output", required=True, help="Output JSON file path")
    args = parser.parse_args()

    parse_licenses(args.input, args.output)
