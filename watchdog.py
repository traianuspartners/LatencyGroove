import aiohttp
import asyncio
import logging
import json
import numpy as np
import time
from datetime import datetime
import subprocess
from urllib.parse import urlparse
from termcolor import colored
from prettytable import PrettyTable

# Configure logging
logging.basicConfig(filename='latency_checks.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def load_config():
    with open('config.json', 'r') as f:
        print(colored("Loading configuration...", "yellow"))
        return json.load(f)

async def measure_latency(session, url):
    print(colored(f"Measuring latency for: {url}", "cyan"))
    start_time = datetime.now()
    async with session.get(url) as response:
        end_time = datetime.now()
        latency = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
        return latency if response.status == 200 else None

async def perform_latency_checks_async(config):
    async with aiohttp.ClientSession() as session:
        tasks = [measure_latency(session, config['api_endpoint']) for _ in range(config['number_of_checks'])]
        results = await asyncio.gather(*tasks)
        latencies = [latency for latency in results if latency is not None]
        return latencies

def calculate_statistics(latencies):
    if latencies:
        avg_latency = np.mean(latencies)
        median_latency = np.median(latencies)
        percentile_95_latency = np.percentile(latencies, 95)
        
        # Display results in a table
        table = PrettyTable()
        table.field_names = ["Metric", "Latency (ms)"]
        table.add_row(["Average", f"{avg_latency:.2f}"])
        table.add_row(["Median", f"{median_latency:.2f}"])
        table.add_row(["95th Percentile", f"{percentile_95_latency:.2f}"])
        
        print(colored(table, "green"))
        logging.info(table.get_string())

async def schedule_checks_async(config):
    while True:
        print(colored("Starting scheduled latency checks...", "blue"))
        latencies = await perform_latency_checks_async(config)
        calculate_statistics(latencies)
        if config.get('enable_network_diagnostics', False):
            run_network_diagnostics(config['api_endpoint'])
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
    for tool, command in diagnostics.items():
        try:
            print(colored(f"Executing {tool}...", "cyan"))
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            logging.info(f"{tool.upper()} Result: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running {tool}: {e}\n{e.stderr}")

if __name__ == '__main__':
    config = load_config()
    asyncio.run(schedule_checks_async(config))
