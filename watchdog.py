import aiohttp
import asyncio
import logging
import json
import numpy as np
import time
from datetime import datetime
import concurrent.futures
from pythonping import ping

# Configure logging
logging.basicConfig(filename='latency_checks.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

async def measure_latency(session, url):
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
        logging.info(f"Average Latency: {np.mean(latencies):.2f} ms, Median: {np.median(latencies):.2f} ms, 95th Percentile: {np.percentile(latencies, 95):.2f} ms")

async def schedule_checks_async(config):
    while True:
        logging.info("Starting scheduled latency checks...")
        latencies = await perform_latency_checks_async(config)
        calculate_statistics(latencies)
        if config.get('enable_network_diagnostics'):
            run_network_diagnostics(config['api_endpoint'])
        await asyncio.sleep(config['scheduling_frequency_seconds'])

def run_network_diagnostics(target):
    # This is a simplified example. You might need root privileges for some operations.
    logging.info(f"Pinging {target}...")
    response = ping(target, count=4)
    logging.info(f"Ping response: {response}")

if __name__ == '__main__':
    config = load_config()
    asyncio.run(schedule_checks_async(config))
