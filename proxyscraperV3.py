import requests
import threading
import time
import re

# Configuration
THREADS = 500  # Reasonable thread count
PROXY_TIMEOUT = 5
CHECK_PROXIES = True

# Output files
OUTPUT_FILES = {
    "http": "http.txt",
    "https": "https.txt",
    "socks4": "socks4.txt",
    "socks5": "socks5.txt",
    "unknown": "unknown.txt"
}

# Categorized proxy sources
PROXY_SOURCES = {
    "http": [
        "https://www.proxy-list.download/api/v1/get?type=http",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://www.proxyscan.io/download?type=http",
    ],
    "https": [
        "https://www.proxy-list.download/api/v1/get?type=https",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
        "https://www.proxyscan.io/download?type=https",
    ],
    "socks4": [
        "https://www.proxy-list.download/api/v1/get?type=socks4",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
        "https://www.proxyscan.io/download?type=socks4",
    ],
    "socks5": [
        "https://www.proxy-list.download/api/v1/get?type=socks5",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
        "https://www.proxyscan.io/download?type=socks5",
    ],
}

# Global storage
proxy_dict = {ptype: set() for ptype in OUTPUT_FILES.keys()}
lock = threading.Lock()

def fetch_proxies():
    for proxy_type, urls in PROXY_SOURCES.items():
        for url in urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    for line in response.text.splitlines():
                        line = line.strip()
                        if re.match(r"\d+\.\d+\.\d+\.\d+:\d+", line):
                            proxy_dict[proxy_type].add(line)
                else:
                    print(f"[!] Bad response from {url}")
            except requests.RequestException:
                print(f"[X] Failed to fetch from {url}")

def test_proxy(proxy, proxy_type):
    test_url = "http://ip-api.com/json/"
    try:
        response = requests.get(
            test_url,
            proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
            timeout=PROXY_TIMEOUT
        )
        if response.status_code == 200:
            with lock:
                proxy_dict[proxy_type].add(proxy)
                print(f"[+] Working {proxy_type.upper()} Proxy: {proxy}")
    except:
        pass  # Ignore broken proxies

def validate_all():
    threads = []
    for proxy_type in proxy_dict:
        raw_list = list(proxy_dict[proxy_type])
        proxy_dict[proxy_type] = set()  # Clear for validated ones

        for proxy in raw_list:
            thread = threading.Thread(target=test_proxy, args=(proxy, proxy_type))
            threads.append(thread)
            thread.start()

            if len(threads) >= THREADS:
                for t in threads:
                    t.join()
                threads = []

    for t in threads:
        t.join()

def save_results():
    for proxy_type, proxies in proxy_dict.items():
        with open(OUTPUT_FILES[proxy_type], "w") as f:
            for proxy in sorted(proxies):
                f.write(proxy + "\n")
        print(f"[✔] Saved {len(proxies)} proxies to {OUTPUT_FILES[proxy_type]}")

def main():
    print("[~] Fetching proxies from all sources...")
    fetch_proxies()

    if CHECK_PROXIES:
        print("[~] Validating proxies...")
        validate_all()
    else:
        print("[~] Skipping validation, saving raw proxies...")

    save_results()

if __name__ == "__main__":
    main()
