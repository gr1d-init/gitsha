import itertools
import string
import requests
import time
import os
import argparse
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed

# Constants
CHECKPOINT_FILE = "progress_checkpoint.txt"
PASS_FILE = "commit_entries.txt"
MAX_WORKERS = 20
LENGTH = 4  # Adjust length for longer SHA1 prefixes
GITHUB_BASE_URL = "https://github.com/{}/commit/"
POOL_OF_CHARS = string.digits + "abcdef"

# Global flag to handle graceful shutdown
stop_flag = False

def signal_handler(signum, frame):
    global stop_flag
    print("\n[!] Received termination signal. Saving progress and exiting...")
    stop_flag = True

def generate_sha1_combinations(length=LENGTH):
    yield from itertools.product(*([POOL_OF_CHARS] * length))

def save_progress(last_sha1):
    if last_sha1 == "ffff":
        last_sha1 = "0000"  # Reset when reaching the end
    with open(CHECKPOINT_FILE, "w") as f:
        f.write(last_sha1)

def record_found_sha1(sha1):
    with open(PASS_FILE, "a") as f:
        f.write(f"{sha1}\n")

def load_progress():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return f.read().strip()
    return None

def scan_commit_sha1(short_sha1, base_url):
    global stop_flag
    if stop_flag:
        return None
    
    url = f"{base_url}{short_sha1}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code in [429, 403]:
            print(f"Rate-limited! Status: {r.status_code}. Sleeping...")
            time.sleep(30)
            return None
        if r.status_code == 200:
            print(f"[+] Found: {short_sha1} -> {r.url}")
            record_found_sha1(short_sha1)
            return short_sha1
        else:
            print(f"[-] {short_sha1} - {r.status_code}")
    except requests.RequestException as e:
        print(f"[ERROR] Request failed for {short_sha1}: {e}")
    return None

def main(repo):
    global stop_flag
    base_url = GITHUB_BASE_URL.format(repo)
    sha1_combinations = ("".join(p) for p in generate_sha1_combinations())
    
    last_sha1 = load_progress()
    found_checkpoint = False
    if last_sha1:
        print(f"[!] Resuming from {last_sha1}...")
        for sha1 in sha1_combinations:
            if sha1 == last_sha1:
                found_checkpoint = True
            if found_checkpoint:
                break
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_sha1 = {executor.submit(scan_commit_sha1, sha1, base_url): sha1 for sha1 in sha1_combinations}
        
        for future in as_completed(future_to_sha1):
            if stop_flag:
                break
            sha1 = future_to_sha1[future]
            try:
                result = future.result()
                if result:
                    print(f"[+] Match found: {result}")
                save_progress(sha1)
            except Exception as e:
                print(f"[ERROR] Exception occurred for {sha1}: {e}")
    
    print("[!] Exiting gracefully. Progress saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitSHA: Find leaked GitHub commit hashes using SHA1 prefixes.", usage="python gitsha.py [-h HELP] -r REPO")
    parser.add_argument("-r", "--repo", type=str, required=True, help="GitHub repository (format: 'user/repo')")
    args = parser.parse_args()
    
    # Register signal handlers for safe shutdown
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C behaves like Ctrl+Break
    signal.signal(signal.SIGTERM, signal_handler)  # Termination request
    
    main(args.repo)
