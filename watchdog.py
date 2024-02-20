import requests
import time
import concurrent.futures
import logging
import json
import numpy as np

# Configure logging
logging.basicConfig(filename='latency_checks.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def measure_latency(api_url):
    try:
        start_time = time.time()
        response = requests.get(api_url)
        end_time = time.time()
        latency = (end_time - start_time) * 1000  # Convert to milliseconds
        if response.status_code == 200:
            return latency
        else:
            logging.error(f"Failed request with status code {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Request exception: {e}")
        return None

def perform_latency_checks(config):
    latencies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=config['number_of_checks']) as executor:
        futures = [executor.submit(measure_latency, config['api_endpoint']) for _ in range(config['number_of_checks'])]
        for future in concurrent.futures.as_completed(futures):
            latency = future.result()
            if latency is not None:
                latencies.append(latency)

    if latencies:
        average_latency = np.mean(latencies)
        median_latency = np.median(latencies)
        percentile_95 = np.percentile(latencies, 95)
        logging.info(f"Average Latency: {average_latency:.2f} ms, Median: {median_latency:.2f} ms, 95th Percentile: {percentile_95:.2f} ms")
    else:
        logging.warning("All requests failed. No latency data collected.")

def schedule_checks(config):
    frequency = config['scheduling_frequency_seconds']
    while True:
        logging.info("Starting scheduled latency checks...")
        perform_latency_checks(config)
        time.sleep(frequency)

if __name__ == '__main__':
    config = load_config()
    schedule_checks(config)
