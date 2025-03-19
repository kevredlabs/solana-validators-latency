# Solana Validator Latency Monitor

A Docker container to measure Solana validator latencies.

## Features

- Fetches the top Solana validators based on total SOL staked
- Configurable number of validators to test (1 to 100+)
- Measures ICMP (ping) latency to each validator
- Shows validator location (city) and data center (ASN)
- Exports results to CSV format

## Quick Start

```bash
# Build the image
docker build -t solana-validators-latency .

# Run with default settings (20 validators)
docker run --net host --cap-add=NET_RAW --cap-add=NET_ADMIN solana-validators-latency

# Test specific number of validators
docker run --net host --cap-add=NET_RAW --cap-add=NET_ADMIN solana-validators-latency --limit 5

# Export to CSV (with volume mount)
docker run --net host --cap-add=NET_RAW --cap-add=NET_ADMIN -v $(pwd):/app/output solana-validators-latency --csv /app/output/results.csv
```

## Options

- `--limit <number>`: Number of validators to test (default: 20, minimum: 1)
- `--csv <filename>`: Export results to a CSV file

## Note

The container requires `--net host` and capabilities `NET_RAW` and `NET_ADMIN` for ICMP ping operations.