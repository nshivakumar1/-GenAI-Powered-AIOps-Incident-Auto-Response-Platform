import requests
import time
import random
import argparse

# Configuration
VICTIM_SERVICE_URL = "http://localhost:8000"  # Update if deployed remotely

def simulate_cpu_spike(duration=30):
    print(f"🔥 Triggering CPU Spike for {duration}s...")
    try:
        resp = requests.post(f"{VICTIM_SERVICE_URL}/simulate/cpu-spike?duration={duration}")
        print(f"Response: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"Error: {e}")

def simulate_memory_leak():
    print("💧 Triggering Memory Leak...")
    try:
        resp = requests.post(f"{VICTIM_SERVICE_URL}/simulate/memory-leak")
        print(f"Response: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"Error: {e}")

def simulate_crash():
    print("💥 Triggering Service Crash...")
    try:
        requests.post(f"{VICTIM_SERVICE_URL}/simulate/crash")
        print("Service crashed (as expected).")
    except requests.exceptions.ConnectionError:
        print("Service crashed successfully (Connection severed).")
    except Exception as e:
        print(f"Error: {e}")

def run_random_chaos(interval=60):
    """Randomly triggers chaos every `interval` seconds."""
    actions = [simulate_cpu_spike, simulate_memory_leak]
    
    print("😈 Chaos Monkey Service Started...")
    try:
        while True:
            action = random.choice(actions)
            action()
            print(f"Sleeping for {interval}s...")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Stopping Chaos Monkey.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chaos Engine for AIOps Demo")
    parser.add_argument("--action", type=str, choices=["cpu", "memory", "crash", "random"], default="random")
    parser.add_argument("--interval", type=int, default=60)
    
    args = parser.parse_args()
    
    if args.action == "cpu":
        simulate_cpu_spike()
    elif args.action == "memory":
        simulate_memory_leak()
    elif args.action == "crash":
        simulate_crash()
    elif args.action == "random":
        run_random_chaos(args.interval)
