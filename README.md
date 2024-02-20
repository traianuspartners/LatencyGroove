
# Latency Check Script for Bybit API

This script performs latency checks against the Bybit API, providing insights into network performance and diagnostics. It utilizes asynchronous requests to simulate concurrent operations, akin to a high-frequency trading (HFT) bot's workload.

## Features

- Asynchronous API requests to measure latency
- Network diagnostics including ping, traceroute, and MTR
- Statistical analysis of latency (average, median, 95th percentile)
- User-friendly console output with color-coded messages and tabular data presentation

## Requirements

Ensure you have Python 3.7+ installed on your system. This script relies on several third-party libraries listed in `requirements.txt`.

## Installation

1. Clone this repository or download the script to your local machine.
2. Install the required Python libraries:

```bash
pip install -r requirements.txt
```

## Configuration

Modify the `config.json` file to set the API endpoint, the number of checks, scheduling frequency, and whether to enable network diagnostics.

Example `config.json`:

```json
{
    "scheduling_frequency_seconds": 600,
    "number_of_checks": 10,
    "api_endpoint": "https://api.bybit.com/v2/public/time",
    "enable_network_diagnostics": true
}
```

## Usage

Run the script with Python:

```bash
python watchdog.py
```

## License

This script is provided "as is", without warranty of any kind. Use it at your own risk.
