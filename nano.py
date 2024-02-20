import aiohttp
import asyncio
from datetime import datetime

async def fetch_server_time(session):
    url = "https://api.bybit.com/v5/market/time"
    async with session.get(url) as response:
        response_json = await response.json()
        # Assumendo che 'time_now' sia il campo che stiamo cercando e sia in nanosecondi
        # Adatta il parsing del tempo qui se il formato è diverso
        server_time_now = response_json['result']['time_now']
        return server_time_now

async def measure_latency(session, url):
    local_start_time_ns = datetime.utcnow().timestamp() * 1e9  # Converti in nanosecondi
    server_time_now_str = await fetch_server_time(session)
    server_time_now_ns = float(server_time_now_str)  # Converti la stringa in float per nanosecondi
    local_finish_time_ns = datetime.utcnow().timestamp() * 1e9  # Converti in nanosecondi

    # Calcolo delle latenze
    round_trip_time_ns = local_finish_time_ns - local_start_time_ns
    server_to_exchange_ns = server_time_now_ns - local_start_time_ns
    exchange_to_server_ns = local_finish_time_ns - server_time_now_ns

    return round_trip_time_ns, server_to_exchange_ns, exchange_to_server_ns

async def perform_latency_checks_async(config):
    async with aiohttp.ClientSession() as session:
        round_trip_time_ns, server_to_exchange_ns, exchange_to_server_ns = await measure_latency(session, config['api_endpoint'])
        print(f"Round Trip Time (ns): {round_trip_time_ns}")
        print(f"Server to Exchange (ns): {server_to_exchange_ns}")
        print(f"Exchange to Server (ns): {exchange_to_server_ns}")

# Qui puoi definire la configurazione e chiamare `perform_latency_checks_async` come necessario
