#!/usr/bin/env python3
"""
Load Test Script for Project Parva API

Tests API performance under load to verify:
- P95 latency < 500ms
- Stable at 50 req/s
"""

import asyncio
import time
import statistics
from datetime import datetime
from typing import List, Dict
import aiohttp


API_BASE = "http://localhost:8000/api/calendar"

# Test endpoints
ENDPOINTS = [
    "/festivals/calculate/dashain?year=2026",
    "/festivals/calculate/tihar?year=2026",
    "/festivals/calculate/shivaratri?year=2026",
    "/festivals/calculate/holi?year=2026",
    "/convert?date=2026-02-15",
    "/today",
    "/panchanga?date=2026-02-15",
]


async def make_request(session: aiohttp.ClientSession, url: str) -> Dict:
    """Make a single API request and measure latency."""
    start = time.perf_counter()
    try:
        async with session.get(url) as response:
            await response.json()
            latency = (time.perf_counter() - start) * 1000  # ms
            return {"url": url, "status": response.status, "latency_ms": latency}
    except Exception as e:
        latency = (time.perf_counter() - start) * 1000
        return {"url": url, "status": 0, "latency_ms": latency, "error": str(e)}


async def run_load_test(
    requests_per_second: int = 50,
    duration_seconds: int = 10
) -> Dict:
    """
    Run load test at specified request rate.
    
    Args:
        requests_per_second: Target RPS
        duration_seconds: How long to run
    
    Returns:
        Test results with latency stats
    """
    total_requests = requests_per_second * duration_seconds
    interval = 1.0 / requests_per_second
    
    print(f"Starting load test: {requests_per_second} req/s for {duration_seconds}s")
    print(f"Total requests: {total_requests}")
    print("-" * 50)
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        start_time = time.perf_counter()
        
        for i in range(total_requests):
            # Pick endpoint round-robin
            endpoint = ENDPOINTS[i % len(ENDPOINTS)]
            url = f"{API_BASE}{endpoint}"
            
            # Fire request without waiting
            task = asyncio.create_task(make_request(session, url))
            results.append(task)
            
            # Rate limiting
            elapsed = time.perf_counter() - start_time
            expected = (i + 1) * interval
            if elapsed < expected:
                await asyncio.sleep(expected - elapsed)
        
        # Wait for all requests to complete
        completed = await asyncio.gather(*results)
    
    # Analyze results
    latencies = [r["latency_ms"] for r in completed if r.get("status") == 200]
    errors = [r for r in completed if r.get("status") != 200]
    
    if not latencies:
        return {"error": "No successful requests", "errors": errors}
    
    latencies.sort()
    n = len(latencies)
    
    stats = {
        "total_requests": total_requests,
        "successful": len(latencies),
        "failed": len(errors),
        "error_rate": len(errors) / total_requests * 100,
        "latency": {
            "min": round(min(latencies), 2),
            "max": round(max(latencies), 2),
            "mean": round(statistics.mean(latencies), 2),
            "p50": round(latencies[int(n * 0.5)], 2),
            "p90": round(latencies[int(n * 0.9)], 2),
            "p95": round(latencies[int(n * 0.95)], 2),
            "p99": round(latencies[int(n * 0.99)], 2),
        },
        "throughput": {
            "target_rps": requests_per_second,
            "actual_rps": round(len(latencies) / duration_seconds, 2),
        },
    }
    
    return stats


def print_results(stats: Dict):
    """Print load test results."""
    print("\n" + "=" * 50)
    print("LOAD TEST RESULTS")
    print("=" * 50)
    
    print(f"\nRequests: {stats['successful']}/{stats['total_requests']} ({stats['error_rate']:.1f}% errors)")
    print(f"Throughput: {stats['throughput']['actual_rps']} req/s (target: {stats['throughput']['target_rps']})")
    
    print(f"\nLatency (ms):")
    lat = stats['latency']
    print(f"  Min:  {lat['min']:>8.2f}")
    print(f"  P50:  {lat['p50']:>8.2f}")
    print(f"  P90:  {lat['p90']:>8.2f}")
    print(f"  P95:  {lat['p95']:>8.2f}  {'✅' if lat['p95'] < 500 else '❌'} (target < 500)")
    print(f"  P99:  {lat['p99']:>8.2f}")
    print(f"  Max:  {lat['max']:>8.2f}")
    
    # Pass/Fail
    p95_pass = lat['p95'] < 500
    throughput_pass = stats['throughput']['actual_rps'] >= stats['throughput']['target_rps'] * 0.9
    
    print("\n" + "-" * 50)
    if p95_pass and throughput_pass:
        print("✅ PASSED: P95 < 500ms and throughput stable")
    else:
        if not p95_pass:
            print("❌ FAILED: P95 latency exceeds 500ms")
        if not throughput_pass:
            print("❌ FAILED: Throughput below target")


async def main():
    """Run load tests at different levels."""
    
    # Warmup
    print("Warming up API...")
    async with aiohttp.ClientSession() as session:
        for ep in ENDPOINTS:
            try:
                await make_request(session, f"{API_BASE}{ep}")
            except:
                pass
    
    # Test at 50 req/s
    stats = await run_load_test(requests_per_second=50, duration_seconds=10)
    print_results(stats)
    
    return stats


if __name__ == "__main__":
    asyncio.run(main())
