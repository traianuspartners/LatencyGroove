import aiohttp
import asyncio
from datetime import datetime
import json
import numpy as np
from prettytable import PrettyTable
from termcolor import colored
from urllib.parse import urlparse
import subprocess
import re
import logging

# Configurazione del logging
logging.basicConfig(filename='latency_checks.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def print_watchdog_logo():
    logo = '''
         __       __              __                __        _______                      
    /  |  _  /  |            /  |              /  |      /       \                     
    $$ | / \ $$ |  ______   _$$ |_     _______ $$ |____  $$$$$$$  |  ______    ______  
    $$ |/$  \$$ | /      \ / $$   |   /       |$$      \ $$ |  $$ | /      \  /      \ 
    $$ /$$$  $$ | $$$$$$  |$$$$$$/   /$$$$$$$/ $$$$$$$  |$$ |  $$ |/$$$$$$  |/$$$$$$  |
    $$ $$/$$ $$ | /    $$ |  $$ | __ $$ |      $$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |
    $$$$/  $$$$ |/$$$$$$$ |  $$ |/  |$$ \_____ $$ |  $$ |$$ |__$$ |$$ \__$$ |$$ \__$$ |
    $$$/    $$$ |$$    $$ |  $$  $$/ $$       |$$ |  $$ |$$    $$/ $$    $$/ $$    $$ |
    $$/      $$/  $$$$$$$/    $$$$/   $$$$$$$/ $$/   $$/ $$$$$$$/   $$$$$$/   $$$$$$$ |
                                                                             /  \__$$ |
                                                                             $$    $$/ 
                                                                               $$$$$$/ 
    '''
    print(colored(logo, 'green'))

def load_config():
    with open('config.json', 'r') as f:
        print(colored("Loading configuration...", "yellow"))
        return json.load(f)

async def fetch_server_time(session):
    url = "https://api.bybit.com/v5/market/time"
    async with session.get(url) as response:
        response_json = await response.json()
        if 'result' in response_json and 'timeNano' in response_json['result']:
            server_time_nano = float(response_json['result']['timeNano'])
            return server_time_nano
        else:
            print(colored("Key 'timeNano' not found in the response.", "red"))
            return None

async def measure_latency(session, url):
    local_start_time_ns = datetime.utcnow().timestamp() * 1e9
    server_time_ns = await fetch_server_time(session)
    local_finish_time_ns = datetime.utcnow().timestamp() * 1e9

    if server_time_ns:
        round_trip_time_ns = local_finish_time_ns - local_start_time_ns
        server_to_exchange_ns = server_time_ns - local_start_time_ns
        exchange_to_server_ns = local_finish_time_ns - server_time_ns
        return round_trip_time_ns, server_to_exchange_ns, exchange_to_server_ns
    return None, None, None

async def perform_latency_checks_async(config):
    async with aiohttp.ClientSession() as session:
        tasks = [measure_latency(session, config['api_endpoint']) for _ in range(config['number_of_checks'])]
        results = await asyncio.gather(*tasks)
        valid_results = [result for result in results if all(result)]
        return valid_results

def calculate_and_print_statistics(results):
    if results:
        # Unpack the results into separate lists
        round_trip_times_ns, server_to_exchange_times_ns, exchange_to_server_times_ns = zip(*results)

        # Prepare the table for display
        table = PrettyTable()
        table.field_names = ["Metric", "Average", "Median", "95th Percentile"]

        # Iterate over each metric to calculate statistics, convert to ms, and add to table
        for label, values_ns in zip(["Round Trip Time", "Server to Exchange", "Exchange to Server"],
                                    [round_trip_times_ns, server_to_exchange_times_ns, exchange_to_server_times_ns]):
            # Convert ns to ms and calculate statistics
            values_ms = [value / 1e6 for value in values_ns]  # Convert from ns to ms
            avg_ms = np.mean(values_ms)
            median_ms = np.median(values_ms)
            percentile_95_ms = np.percentile(values_ms, 95)

            # Add the row to the table, with values rounded to 2 decimal places
            table.add_row([label, f"{avg_ms:.2f} ms", f"{median_ms:.2f} ms", f"{percentile_95_ms:.2f} ms"])

        # Print the table with color
        print(colored(table, "yellow"))

        # For logging, calculate and log the full precision ns values
        logging.info("Detailed Latency Measurements in Nanoseconds:")
        for label, values_ns in zip(["Round Trip Time (ns)", "Server to Exchange (ns)", "Exchange to Server (ns)"],
                                    [round_trip_times_ns, server_to_exchange_times_ns, exchange_to_server_times_ns]):
            avg_ns = np.mean(values_ns)
            median_ns = np.median(values_ns)
            percentile_95_ns = np.percentile(values_ns, 95)

            # Log the full precision ns values
            logging.info(f"{label}: Average = {avg_ns} ns, Median = {median_ns} ns, 95th Percentile = {percentile_95_ns} ns")

async def schedule_checks_async(config):
    print_watchdog_logo()
    while True:
        print(colored("Starting scheduled latency checks...", "blue"))
        results = await perform_latency_checks_async(config)
        calculate_and_print_statistics(results)
        print(colored(f"Waiting {config['scheduling_frequency_seconds']} seconds before the next round of checks...", "magenta"))
        await asyncio.sleep(config['scheduling_frequency_seconds'])

def run_network_diagnostics(target):
    parsed_url = urlparse(target)
    domain = parsed_url.netloc
    print(colored("Running network diagnostics...", "yellow"))

    diagnostics = {
        "ping": ["ping", "-c", "4", domain],
        "traceroute": ["traceroute", domain],
        "mtr": ["mtr", "--report", "--report-cycles", "1", domain]
    }

    tests_run = 0
    tests_passed = 0
    ping_summary_ms = None

    for tool, command in diagnostics.items():
        try:
            print(colored(f"Executing {tool}...", "cyan"))
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            logging.info(f"{tool.upper()} Result: {result.stdout}")
            if result.returncode == 0:
                tests_passed += 1
                if tool == "ping":
                    # Extract the average ping time in ms
                    match = re.search(r'avg = (\d+.\d+)/', result.stdout)
                    if match:
                        ping_summary_ms = match.group(1)
            tests_run += 1
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running {tool}: {e}\n{e.stderr}")

    # Summary for UI
    summary_status = "All tests passed" if tests_run == tests_passed else "Some tests failed"

    # Print summary
    summary_table = PrettyTable()
    summary_table.field_names = ["Metric", "Value"]
    summary_table.add_row(["Tests Executed", tests_run])
    summary_table.add_row(["Tests Passed", tests_passed])
    summary_table.add_row(["Summary Status", summary_status])
    if ping_summary_ms:
        summary_table.add_row(["Ping (avg ms)", ping_summary_ms])
    print(colored(summary_table, "green"))
  
if __name__ == '__main__':
    asyncio.run(schedule_checks_async(load_config()))
