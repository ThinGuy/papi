# PAPI - Ubuntu Project and Package Information

PAPI is a web application that provides detailed information about Ubuntu repositories, including package counts and size estimations across different Ubuntu releases, pockets, components, and architectures.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Overview

PAPI helps system administrators and DevOps engineers estimate the disk space required for mirroring Ubuntu repositories. It provides a user-friendly web interface to:

- Calculate repository sizes across different combinations of releases, pockets, components, and architectures
- Support for various repository types including:
  - archive.ubuntu.com
  - ports.ubuntu.com
  - esm.ubuntu.com (Ubuntu Pro repositories)
  - ubuntu-cloud.archive.canonical.com
  - Custom repository URLs
- Generate downloadable reports for capacity planning

## Features

- Multi-repository support (archive, ports, ESM, cloud archive, custom)
- Ubuntu release selection (Noble, Jammy, Focal, Bionic, Xenial, Trusty, Precise)
- Component selection (main, restricted, universe, multiverse)
- Architecture selection (amd64, arm64, i386, ppc64el, s390x, source)
- Pocket selection (release, updates, security, backports, proposed)
- Ubuntu Pro / ESM repository support with token authentication
- Parallel processing for faster response times
- Downloadable plain-text reports
- Containerized deployment option

## Screenshots

(Screenshots will be added here)

## Installation

### Prerequisites

- Python 3.6+
- Flask
- Requests

### Option 1: Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/thinguy/papi.git
   cd papi
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python papi.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

### Option 2: Docker Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/thinguy/papi.git
   cd papi
   ```

2. Build and run the Docker container:
   ```bash
   cd build
   ./docker.sh
   ```

3. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Select a repository type (archive, ports, ESM, cloud, custom)
2. Choose an Ubuntu release (Noble, Jammy, Focal, Bionic, etc.)
3. Select desired pockets (release, updates, security, etc.)
4. Select components (main, restricted, universe, multiverse)
5. Select architectures (amd64, arm64, i386, etc.)
6. For ESM repositories, enter your Ubuntu Pro token
7. Click "Calculate Size"
8. View the results and download the report if needed

## API Reference

PAPI provides a REST API for programmatic access:

### Estimate Repository Size

**Endpoint**: `/api/estimate`

**Method**: POST

**Request Body**:
```json
{
  "repo_type": "archive",
  "entitlement": "infra",
  "release": "jammy",
  "pockets": ["release", "updates", "security"],
  "components": ["main"],
  "architectures": ["binary-amd64", "source"],
  "token": "your-ubuntu-pro-token"
}
```

**Response**:
```json
{
  "config": {
    "repo_type": "archive",
    "entitlement": "infra",
    "release": "jammy",
    "pockets": ["release", "updates", "security"],
    "components": ["main"],
    "architectures": ["binary-amd64", "source"]
  },
  "results": [
    {
      "pocket": "release",
      "component": "main",
      "architecture": "binary-amd64",
      "package_count": 1845,
      "size": "2.35 GB",
      "url": "https://archive.ubuntu.com/ubuntu/dists/jammy/main/binary-amd64"
    },
    ...
  ],
  "summary": {
    "total_packages": 5280,
    "total_size": "7.92 GB",
    "estimated_disk_space": "9.50 GB"
  }
}
```

## Project Structure

```
papi/
├── build/
│   └── docker.sh        # Docker build and run script
├── Dockerfile           # Docker configuration
├── papi.py              # Main application code
├── requirements.txt     # Python dependencies
└── templates/
    └── index.html       # Web UI template
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Ubuntu and Canonical for the package repository infrastructure
- The Flask framework for making web development in Python enjoyable

## Contact

GitHub: [https://github.com/thinguy/papi](https://github.com/thinguy/papi)

## Roadmap

- [ ] Add historical data tracking
- [ ] Implement repository comparison feature
- [ ] Add package-level details
- [ ] Support for more Ubuntu derivatives
