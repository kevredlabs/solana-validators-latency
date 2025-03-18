import requests
import subprocess
import re
import csv
import argparse
import json
from prettytable import PrettyTable
import base64
import base58
import time

def get_validator_name(vote_pubkey):
    try:
        url = "https://api.mainnet-beta.solana.com"
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [
                vote_pubkey,
                {"encoding": "base64"}
            ]
        }
        response = requests.post(url, json=payload, timeout=5)
        data = response.json()
        if data.get("result", {}).get("value", {}).get("data"):
            # Vote account data contains metadata
            account_data = data["result"]["value"]["data"]
            decoded = base64.b64decode(account_data)
            # Look for printable ASCII string after metadata
            name_match = re.search(b'[a-zA-Z0-9\-_]+', decoded[32:])
            if name_match:
                return name_match.group(0).decode('ascii')
    except Exception as e:
        print(f"Error fetching validator name: {str(e)}")
    return "Unknown"

# 🔹 1. Get the Top Validators by Staked SOL
def get_top_validators(limit=20):
    # Use Solana RPC API to get validators
    url = "https://api.mainnet-beta.solana.com"
    
    # First request to get votes and stakes
    vote_accounts_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getVoteAccounts"
    }
    
    # Second request to get gossip information
    cluster_nodes_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getClusterNodes"
    }
    
    try:
        # Get votes and stakes
        vote_response = requests.post(url, json=vote_accounts_payload)
        vote_data = vote_response.json()
        
        # Get gossip information (including IPs)
        nodes_response = requests.post(url, json=cluster_nodes_payload)
        nodes_data = nodes_response.json()
        
        # Create a dictionary of node information
        node_info = {
            node['pubkey']: {
                'ip': node.get('gossip', '').split(':')[0],
                'rpc': node.get('rpc'),
                'tpu': node.get('tpu')
            }
            for node in nodes_data['result']
        }
        
        # Combine information
        all_validators = vote_data['result']['current'] + vote_data['result']['delinquent']
        sorted_validators = sorted(
            all_validators,
            key=lambda x: int(x['activatedStake']),
            reverse=True
        )[:limit]
        
        validators = []
        for v in sorted_validators:
            node_data = node_info.get(v['nodePubkey'], {})
            ip = node_data.get('ip', '')
            ip_info = get_ip_info(ip) if ip else {"city": "Unknown", "asn": "Unknown"}
            validators.append({
                "vote_account": v['votePubkey'],
                "ip": ip,
                "stake": int(v['activatedStake']) / 1e9,
                "asn": ip_info["asn"],
                "city": ip_info["city"]
            })
        
        return validators
        
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return []

# 🔹 2. Measure ICMP Latency (Ping)
def test_icmp_latency(ip):
    try:
        result = subprocess.run(["ping", "-c", "3", ip], capture_output=True, text=True, timeout=5)
        match = re.search(r"time=([\d.]+) ms", result.stdout)
        return float(match.group(1)) if match else None
    except Exception:
        return None

# 🔹 3. Measure UDP QUIC Latency (Port 8001)
def test_quic_latency(ip):
    try:
        # Use netcat to test UDP port 8001
        start_time = time.time()
        result = subprocess.run([
            "nc",
            "-u",
            "-w", "2",  # 2 seconds timeout
            "-z",       # scan mode
            ip,
            "8001"
        ], capture_output=True, text=True, timeout=3)
        
        if result.returncode == 0:
            end_time = time.time()
            return round((end_time - start_time) * 1000, 1)  # Convert to ms
        return None
    except Exception as e:
        print(f"QUIC test failed for {ip}: {str(e)}")
        return None

def get_ip_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = response.json()
        if data["status"] == "success":
            return {
                "city": data.get("city", "Unknown"),
                "asn": f"AS{data.get('as', 'Unknown')}"
            }
    except Exception:
        pass
    return {"city": "Unknown", "asn": "Unknown"}

# 🔹 4. Run Tests and Display Results
def main():
    parser = argparse.ArgumentParser(description="Measure latency of the top Solana validators")
    parser.add_argument("--csv", type=str, help="Export results to a CSV file (e.g., --csv output.csv)")
    parser.add_argument("--limit", type=int, default=20, help="Number of validators to test (default: 20)")
    args = parser.parse_args()

    print(f"🔍 Testing latency for the top {args.limit} Solana validators...\n")
    validators = get_top_validators(args.limit)
    
    if not validators:
        print("No validators found.")
        return

    table = PrettyTable(["Vote Account", "SOL Staked", "IP", "City", "Data Center (ASN)", "Ping (ICMP)", "QUIC (UDP 8001)"])
    results = []

    for v in validators:
        icmp_latency = test_icmp_latency(v["ip"])
        quic_latency = test_quic_latency(v["ip"])
        
        row = [
            v["vote_account"],
            f"{v['stake']:.2f} SOL", 
            v["ip"], 
            v["city"], 
            v["asn"], 
            f"{icmp_latency} ms" if icmp_latency else "N/A",
            f"{quic_latency} ms" if quic_latency else "N/A"
        ]
        
        table.add_row(row)
        results.append(row)

    print(table)

    # 🔹 5. Export to CSV if requested
    if args.csv:
        with open(args.csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Vote Account", "SOL Staked", "IP", "City", "Data Center (ASN)", "Ping (ICMP)", "QUIC (UDP 8001)"])
            writer.writerows(results)
        print(f"✅ Results saved to {args.csv}")

if __name__ == "__main__":
    main()