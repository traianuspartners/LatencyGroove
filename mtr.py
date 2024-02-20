import asyncio
import logging
import json
import subprocess
from aiohttp import ClientSession

# Configure logging
logging.basicConfig(filename='latency_checks.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

async def measure_latency(session, url):
    start_time = asyncio.get_event_loop().time()
    async with session.get(url) as response:
        end_time = asyncio.get_event_loop().time()
        latency = (end_time - start_time) * 1000  # Convert to milliseconds
        return latency if response.status == 200 else None

async def perform_latency_checks_async(config):
    async with ClientSession() as session:
        tasks = [measure_latency(session, config['api_endpoint']) for _ in range(config['number_of_checks'])]
        results = await asyncio.gather(*tasks)
        latencies = [latency for latency in results if latency is not None]
        return latencies

def run_network_diagnostics(target):
    diagnostics = {
        "ping": ["ping", "-c", "4", target.split("//")[-1]],
        "traceroute": ["traceroute", target.split("//")[-1]],
        "mtr": ["mtr", "--report", "--report-cycles", "1", target.split("//")[-1]]
    }
    for tool, command in diagnostics.items():
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            logging.info(f"{tool.upper()} Result: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running {tool}: {e}\n{e.stderr}")

async def schedule_checks_async(config):
    while True:
        logging.info("Starting scheduled latency checks...")
        latencies = await perform_latency_checks_async(config)
        if latencies:
            average_latency = sum(latencies) / len(latencies)
            logging.info(f"Average Latency: {average_latency:.2f} ms")
        if config.get('enable_network_diagnostics', False):
            run_network_diagnostics(config['api_endpoint'])
        await asyncio.sleep(config['scheduling_frequency_seconds'])

if __name__ == '__main__':
    config = load_config()
    asyncio.run(schedule_checks_async(config))
