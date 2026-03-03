import argparse
import asyncio
import logging
from datetime import datetime
from time import time

import aiohttp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

logger = logging.getLogger(__name__)


async def run_client(client_id, num_requests, url, timeout):
    success_count = 0
    error_count = 0
    response_times = []

    timeout_config = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(timeout=timeout_config) as session:
        for i in range(num_requests):
            success, response_time = await send_request(session, url)
            if success:
                success_count += 1
                response_times.append(response_time)
            else:
                error_count += 1

            if (i + 1) % 1000 == 0:
                logger.debug(
                    f"Client {client_id}: {i + 1}/{num_requests} requests completed"
                )

    return success_count, error_count, response_times


async def send_request(session, url):
    try:
        start_time = time()
        async with session.get(url=url) as response:
            await response.read()
            response_time = time() - start_time
            return response.status == 200, response_time
    except asyncio.TimeoutError:
        logger.error("Request timed out")
        return False, 0
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return False, 0


async def verify_counter(url, expected_value):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    actual_value = int(await response.text())
                    logger.info(f"Final counter value: {actual_value}")
                    if actual_value == expected_value:
                        logger.info("✓ Counter verification PASSED")
                    else:
                        logger.warning(
                            f"✗ Counter verification FAILED: expected {expected_value}, got {actual_value}"
                        )
                    return actual_value
    except Exception as e:
        logger.error(f"Failed to verify counter: {e}")
    return None


async def main(num_clients, requests_per_client, url, timeout):
    tasks = [
        run_client(client_id, requests_per_client, url, timeout)
        for client_id in range(num_clients)
    ]
    results = await asyncio.gather(*tasks)

    total_success = sum(r[0] for r in results)
    total_errors = sum(r[1] for r in results)

    all_response_times = []
    for r in results:
        all_response_times.extend(r[2])

    return total_success, total_errors, all_response_times


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Load testing client for web counter')
    parser.add_argument(
        '--clients', type=int, default=10, help='Number of concurrent clients'
    )
    parser.add_argument(
        '--requests', type=int, default=10000, help='Requests per client'
    )
    parser.add_argument(
        '--url', type=str, default='http://127.0.0.1:8000/inc', help='URL to test'
    )
    parser.add_argument(
        '--timeout', type=int, default=10, help='Request timeout in seconds'
    )
    parser.add_argument(
        '--verify', action='store_true', help='Verify final counter value'
    )
    parser.add_argument(
        '--storage',
        type=str,
        default='memory',
        help='Storage type [hazelcast, memory, mongo, postgres]',
    )

    args = parser.parse_args()

    total_requests = args.clients * args.requests

    logger.info(f"Storage type: {args.storage.upper()}")
    logger.info(f"URL: {args.url}")
    logger.info(
        f"Test: {args.clients} client(s) × {args.requests} requests = {total_requests} total"
    )

    start_time = datetime.now()

    total_success, total_errors, response_times = asyncio.run(
        main(args.clients, args.requests, args.url, args.timeout)
    )

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    throughput = total_requests / duration if duration > 0 else 0
    success_rate = (total_success / total_requests) * 100 if total_requests > 0 else 0

    logger.info("=" * 60)
    logger.info("RESULTS")
    logger.info("=" * 60)
    logger.info(f"Duration: {duration:.2f}s")
    logger.info(f"Throughput: {throughput:.2f} req/s")
    logger.info(f"Success: {total_success}/{total_requests} ({success_rate:.2f}%)")

    if total_errors > 0:
        logger.warning(f"Errors: {total_errors}")

    if response_times:
        response_times.sort()
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        p50 = response_times[len(response_times) // 2]
        p95 = response_times[int(len(response_times) * 0.95)]
        p99 = response_times[int(len(response_times) * 0.99)]

        logger.info("=" * 60)
        logger.info("RESPONSE TIMES")
        logger.info("=" * 60)
        logger.info(f"Min: {min_time * 1000:.2f}ms")
        logger.info(f"Avg: {avg_time * 1000:.2f}ms")
        logger.info(f"Max: {max_time * 1000:.2f}ms")
        logger.info(f"P50: {p50 * 1000:.2f}ms")
        logger.info(f"P95: {p95 * 1000:.2f}ms")
        logger.info(f"P99: {p99 * 1000:.2f}ms")

    if args.verify:
        logger.info("=" * 60)
        logger.info("VERIFICATION")
        logger.info("=" * 60)
        verify_url = args.url.replace('/inc', '/read')
        asyncio.run(verify_counter(verify_url, total_success))
