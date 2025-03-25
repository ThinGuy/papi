#!/usr/bin/env python3
# indexer.py v1.5
#
# Indexes Ubuntu repositories by scanning `dists/` directories.
# Outputs JSON data structured by repo, release, suite, component, and arch.
# Supports specifying an output path with `--output`.

import os
import json
import requests
from urllib.parse import urljoin
import argparse

# Known Repository URLs
REPO_URLS = {
    "lts-amd64": "https://archive.ubuntu.com/ubuntu/",
    "lts-ports": "https://ports.ubuntu.com/ubuntu-ports/",
    "pro-anbox": "https://archive.anbox-cloud.io/stable/",
    "pro-apps": "https://esm.ubuntu.com/apps/ubuntu/",
    "pro-cc": "https://esm.ubuntu.com/cc/ubuntu/",
    "pro-cis": "https://esm.ubuntu.com/cis/ubuntu/",
    "pro-infra": "https://esm.ubuntu.com/infra/ubuntu/",
    "pro-infra-legacy": "https://esm.ubuntu.com/infra-legacy/ubuntu/",
    "pro-fips": "https://esm.ubuntu.com/fips/ubuntu/",
    "pro-fips-preview": "https://esm.ubuntu.com/fips-preview/ubuntu/",
    "pro-fips-updates": "https://esm.ubuntu.com/fips-updates/ubuntu/",
    "pro-rtk": "https://esm.ubuntu.com/realtime/ubuntu/",
    "pro-ros": "https://esm.ubuntu.com/ros/ubuntu/",
    "pro-ros-updates": "https://esm.ubuntu.com/ros-updates/ubuntu/",
    "pro-usg": "https://esm.ubuntu.com/usg/ubuntu/"
}

def web_exists(url):
    """Check if a given URL exists."""
    try:
        response = requests.head(url, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def fetch_repo_structure():
    """Fetch and structure data from the correct URLs."""
    repo_data = {}

    for repo, base_url in REPO_URLS.items():
        dists_path = urljoin(base_url, "dists/")
        if not web_exists(dists_path):
            print(f"Warning: {dists_path} not found. Skipping...")
            continue

        repo_data[repo] = {}

        response = requests.get(dists_path)
        for line in response.text.splitlines():
            if 'href="' in line and '/"' in line:
                suite = line.split('href="')[1].split('/')[0]

                if suite not in repo_data[repo]:
                    repo_data[repo][suite] = {}

                components_path = urljoin(dists_path, f"{suite}/")
                response = requests.get(components_path)

                for line in response.text.splitlines():
                    if 'href="' in line and '/"' in line:
                        component = line.split('href="')[1].split('/')[0]

                        if component not in repo_data[repo][suite]:
                            repo_data[repo][suite][component] = []

                        # Arch and index file detection
                        for arch in ['binary-amd64', 'binary-arm64', 'source']:
                            index_uri = urljoin(components_path, f"{component}/{arch}/Packages.gz")
                            if web_exists(index_uri):
                                repo_data[repo][suite][component].append({
                                    "arch": arch,
                                    "index_uri": index_uri
                                })

    return repo_data

def main():
    parser = argparse.ArgumentParser(description="Ubuntu Repository Indexer")
    parser.add_argument("-o", "--output", required=True, help="Output path for JSON data")
    args = parser.parse_args()

    repo_data = fetch_repo_structure()

    output_path = os.path.join(args.output, "ubuntu_indexes.json")
    with open(output_path, "w") as f:
        json.dump(repo_data, f, indent=4)

    print(f"Indexing complete. Data saved to {output_path}")

if __name__ == "__main__":
    main()
