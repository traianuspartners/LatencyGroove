import aiohttp
import asyncio
from datetime import datetime
import json
import numpy as np
from prettytable import PrettyTable
from termcolor import colored
from urllib.parse import urlparse

# Configurazione del logging
import logging
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
    print(colored(logo, 'green', 'on_red'))

def load_config():
    with open('config.json', 'r') as f:
        print(colored("Loading configuration...", "yellow"))
        return json.load(f)

async def fetch_server_time(session):
    url = "https://api.bybit.com/v5/market/time"
    async with session.get(url) as response:
        response_json = await response.json()
        server_time_now = float(response_json['result']['time_now'])
        return server_time_now

async def measure_latency(session, url):
    local_start_time_ns = datetime.utcnow().timestamp() * 1e9
    server_time_ns = await fetch_server_time(session)
    local_finish_time_ns = datetime.utcnow().timestamp() * 1e9

    round_trip_time_ns = local_finish_time_ns - local_start_time_ns
    server_to_exchange_ns = server_time_ns - local_start_time_ns
    exchange_to_server_ns = local_finish_time_ns - server_time_ns

    return round_trip_time_ns, server_to_exchange_ns, exchange_to_server_ns

async def perform_latency_checks_async(config):
    async with aiohttp.ClientSession() as session:
        tasks = [measure_latency(session, config['api_endpoint']) for _ in range(config['number_of_checks'])]
        results = await asyncio.gather(*tasks)
        return results

def calculate_and_print_statistics(results):
    latencies = np.array(results)
    avg_latencies = np.mean(latencies, axis=0)
    median_latencies = np.median(latencies, axis=0)
    percentile_95_latencies = np.percentile(latencies, 95, axis=0)

    table = PrettyTable()
    table.field_names = ["Metric", "Round Trip Time (ns)", "Server to Exchange (ns)", "Exchange to Server (ns)"]
    table.add_row(["Average", f"{avg_latencies[0]:.2f}", f"{avg_latencies[1]:.2f}", f"{avg_latencies[2]:.2f}"])
    table.add_row(["Median", f"{median_latencies[0]:.2f}", f"{median_latencies[1]:.2f}", f"{median_latencies[2]:.2f}"])
    table.add_row(["95th Percentile", f"{percentile_95_latencies[0]:.2f}", f"{percentile_95_latencies[1]:.2f}", f"{percentile_95_latencies[2]:.2f}"])
    
    print(colored(table, "yellow"))

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
