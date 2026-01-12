import argparse
import asyncio
import logging
import os
from datetime import datetime

import aiohttp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

logger = logging.getLogger(__name__)


async def run_client(client_id, num_requests):
    success_count = 0
    error_count = 0

    async with aiohttp.ClientSession() as session:
        for i in range(num_requests):
            success = await send_request(session)
            if success:
                success_count += 1
            else:
                error_count += 1

    return success_count, error_count


async def send_request(session):
    try:
        async with session.get(url='http://127.0.0.1:8080/inc') as response:
            return response.status == 200
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return False


async def main(num_clients, requests_per_client):
    tasks = [
        run_client(client_id, requests_per_client) for client_id in range(num_clients)
    ]
    results = await asyncio.gather(*tasks)

    total_success = sum(r[0] for r in results)
    total_errors = sum(r[1] for r in results)

    return total_success, total_errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Load testing client')
    parser.add_argument('--clients', type=int, default=1, help='Number of clients')
    parser.add_argument(
        '--requests', type=int, default=10000, help='Requests per client'
    )

    args = parser.parse_args()

    total_requests = args.clients * args.requests
    logger.info(f"Storage type {os.getenv('STORAGE_TYPE', 'MEMORY').upper()}")
    logger.info(
        f"Test: {args.clients} client(s) × {args.requests} requests = {total_requests} total"
    )

    start_time = datetime.now()

    total_success, total_errors = asyncio.run(main(args.clients, args.requests))

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    throughput = total_requests / duration if duration > 0 else 0
    success_rate = (total_success / total_requests) * 100 if total_requests > 0 else 0

    logger.info(f"Duration: {duration:.2f}s")
    logger.info(f"Throughput: {throughput:.2f} req/s")
    logger.info(f"Success: {total_success}/{total_requests} ({success_rate:.2f}%)")

    if total_errors > 0:
        logger.warning(f"Errors: {total_errors}")
