# 🏆 Solana Validator Latency Monitor

This script measures the **latency of Solana validators** based on **staked SOL**.  
It helps analyze **network performance**, optimize validator connections, and ensure low-latency communication.

---

## 🚀 Features
✔ Fetches the **top Solana validators** based on **total SOL staked**  
✔ Measures **ICMP (ping) latency**  
✔ Measures **QUIC (UDP 8001) latency** (Solana gossip protocol)  
✔ Displays results in a **formatted table**  
✔ Option to **export results to a CSV file**  
✔ **Docker-ready** for isolated execution  
✔ Configurable number of validators to test (1 to 100+)  

---

## 🛠 Installation

### **Docker Installation**

#### **Build the Docker Image**
```sh
docker build -t solana-validators-latency .
```

#### **Run with Docker**
```sh
# Basic usage (tests top 20 validators)
docker run --cap-add=NET_RAW --cap-add=NET_ADMIN --cap-add=NET_BIND_SERVICE solana-validators-latency

# Test a single validator
docker run --cap-add=NET_RAW --cap-add=NET_ADMIN --cap-add=NET_BIND_SERVICE solana-validators-latency --limit 1

# Test specific number of validators
docker run --cap-add=NET_RAW --cap-add=NET_ADMIN --cap-add=NET_BIND_SERVICE solana-validators-latency --limit 10

# Export results to CSV (with volume mount to save the file)
docker run --cap-add=NET_RAW --cap-add=NET_ADMIN --cap-add=NET_BIND_SERVICE -v $(pwd):/app/output solana-validators-latency --csv /app/output/results.csv

# Combine options
docker run --cap-add=NET_RAW --cap-add=NET_ADMIN --cap-add=NET_BIND_SERVICE -v $(pwd):/app/output solana-validators-latency --limit 50 --csv /app/output/results.csv
```

---

## 📝 Command Line Options

- `--limit <number>`: Number of validators to test (default: 20, min: 1)
- `--csv <filename>`: Export results to a CSV file

---

## 🔒 Security Note

The Docker container requires additional capabilities (`NET_RAW`, `NET_ADMIN`, `NET_BIND_SERVICE`) to perform network latency tests. These capabilities are necessary for ICMP and UDP testing but should be used with caution in production environments.