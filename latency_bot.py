import aiohttp
import asyncio
from datetime import datetime
import json
import numpy as np
from prettytable import PrettyTable
from termcolor import colored
import logging

# Configure detailed logging
logging.basicConfig(filename='latency_checks_detailed.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def print_watchdog_logo():
    logging.debug("Printing WatchDog logo")
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

async def fetch_server_time(session, url):
    logging.debug(f"Fetching server time from {url}")
    async with session.get(url) as response:
        response_json = await response.json()
        if 'result' in response_json and 'timeNano' in response_json['result']:
            server_time_nano = float(response_json['result']['timeNano'])
            logging.debug(f"Server time (nano) fetched: {server_time_nano}")
            return server_time_nano
        else:
            logging.error("Key 'timeNano' not found in the response.")
            return None

async def measure_latency(session, url):
    logging.debug("Starting latency measurement")
    local_start_time_ns = datetime.utcnow().timestamp() * 1e9
    server_time_ns = await fetch_server_time(session, url)
    local_finish_time_ns = datetime.utcnow().timestamp() * 1e9

    if server_time_ns:
        latency_results = {
            "round_trip_time_ns": local_finish_time_ns - local_start_time_ns,
            "server_to_exchange_ns": server_time_ns - local_start_time_ns,
            "exchange_to_server_ns": local_finish_time_ns - server_time_ns
        }
        logging.debug(f"Latency measurement results: {latency_results}")
        return latency_results
    logging.error("Failed to fetch server time for latency measurement")
    return None

async def perform_latency_checks_async(config):
    logging.debug("Performing latency checks")
    async with aiohttp.ClientSession() as session:
        tasks = [measure_latency(session, config['api_endpoint']) for _ in range(config['number_of_checks'])]
        results = await asyncio.gather(*tasks)
        valid_results = [result for result in results if result]
        logging.debug("Latency checks completed")
        return valid_results

def calculate_and_print_statistics(results):
    logging.debug("Calculating statistics for latency measurements")
    if not results:
        logging.info("No latency data to display.")
        return
    
    round_trip_times_ms = [result['round_trip_time_ns'] / 1e6 for result in results]
    server_to_exchange_times_ms = [result['server_to_exchange_ns'] / 1e6 for result in results]
    exchange_to_server_times_ms = [result['exchange_to_server_ns'] / 1e6 for result in results]

    table = PrettyTable()
    table.field_names = ["Metric", "Average (ms)", "Median (ms)", "95th Percentile (ms)"]
    metrics = ["Round Trip Time", "Server to Exchange", "Exchange to Server"]
    for metric, values in zip(metrics, [round_trip_times_ms, server_to_exchange_times_ms, exchange_to_server_times_ms]):
        avg = np.mean(values)
        median = np.median(values)
        percentile_95 = np.percentile(values, 95)
        table.add_row([metric, f"{avg:.2f}", f"{median:.2f}", f"{percentile_95:.2f}"])
        logging.debug(f"{metric} - Avg: {avg:.2f} ms, Median: {median:.2f} ms, 95th Percentile: {percentile_95:.2f} ms")
    
    print(colored(table, "yellow"))

def load_config():
    logging.debug("Loading configuration from config.json")
    with open('config.json', 'r') as f:
        config = json.load(f)
    logging.debug(f"Configuration loaded: {config}")
    return config

async def main():
    logging.info("Starting latency check script")
    config = load_config()
    results = await perform_latency_checks_async(config)
    calculate_and_print_statistics(results)
    logging.info("Latency check script completed")

if __name__ == '__main__':
    asyncio.run(main())
