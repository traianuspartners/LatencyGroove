import aiohttp
import asyncio
from datetime import datetime
import json
import numpy as np
from prettytable import PrettyTable
from termcolor import colored
from urllib.parse import urlparse
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
        round_trip_times_ns, server_to_exchange_times_ns, exchange_to_server_times_ns = zip(*results)
        table = PrettyTable()
        table.field_names = ["Metric", "Average (ns)", "Median (ns)", "95th Percentile (ns)"]
        for label, values in zip(["Round Trip Time", "Server to Exchange", "Exchange to Server"],
                                 [round_trip_times_ns, server_to_exchange_times_ns, exchange_to_server_times_ns]):
            avg = np.mean(values)
            median = np.median(values)
            percentile_95 = np.percentile(values, 95)
            table.add_row([label, f"{avg:.2f}", f"{median:.2f}", f"{percentile_95:.2f}"])
        print(colored(table, "yellow"))
        logging.info(table.get_string())

async def schedule_checks_async(config):
    print_watchdog_logo()
    while True:
        print(colored("Starting scheduled latency checks...", "blue"))
        results = await perform_latency_checks_async(config)
        calculate_and_print_statistics(results)
        print(colored(f"Waiting {config['scheduling_frequency_seconds']} seconds before the next round of checks...", "magenta"))
        await asyncio.sleep(config['scheduling_frequency_seconds'])

if __name__ == '__main__':
    asyncio.run(schedule_checks_async(load_config()))
