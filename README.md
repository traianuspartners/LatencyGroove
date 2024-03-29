
# Latency Check Script for Bybit API

This script performs latency checks against the Bybit API, providing insights into network performance and diagnostics. It utilizes asynchronous requests to simulate concurrent operations, akin to a high-frequency trading (HFT) bot's workload.

## 📊 Overview

This script is your latency watchdog  🐾
It's a speedy little fella, running those latency checks in parallel using a thread pool 🚀, mimicking the lightning-fast operations of an HFT bot.
Once it's done its rounds, it doesn't just sit there twiddling its thumbs. Oh no! It crunches the numbers and logs fancy stats like average, median, and the 95th percentile of the latencies.
And guess what? It's also got a knack for handling errors 🛠️. If any requests fail, it makes a note of it and logs the details to a file.

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
```bash
python3 -m pip install termcolor
```
```bash
python3 -m pip install prettytable
```
3. Install external dependencies:

```bash
apt install traceroute
```
```bash
apt install mtr
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
python3 watchdog.py
```

## License

This script is provided "as is", without warranty of any kind. Use it at your own risk.
