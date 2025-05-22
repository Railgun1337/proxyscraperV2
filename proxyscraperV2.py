import requests
import threading
import time

# Configuration
THREADS = 99999999  # Number of simultaneous proxy checks
PROXY_TIMEOUT = 5  # Max time (seconds) a proxy should take to respond
OUTPUT_FILE = "proxies.txt"
CHECK_PROXIES = False  # Set to False to skip checking and save all scraped proxies

# Massive List of Proxy Sources (80+ Sources)
PROXY_SOURCES = [
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://www.proxy-list.download/api/v1/get?type=https",
    "https://www.proxy-list.download/api/v1/get?type=socks4",
    "https://www.proxy-list.download/api/v1/get?type=socks5",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
    "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    "https://www.proxyscan.io/download?type=http",
    "https://www.proxyscan.io/download?type=https",
    "https://www.proxyscan.io/download?type=socks4",
    "https://www.proxyscan.io/download?type=socks5",
    "https://api.openproxy.space/list/http",
    "https://api.openproxy.space/list/https",
    "https://api.openproxy.space/list/socks4",
    "https://api.openproxy.space/list/socks5",
    "https://proxyspace.pro/http.txt",
    "https://proxyspace.pro/https.txt",
    "https://proxyspace.pro/socks4.txt",
    "https://proxyspace.pro/socks5.txt",
    "https://multiproxy.org/txt_all/proxy.txt",
    "https://www.sslproxies.org/",
    "https://www.us-proxy.org/",
    "https://www.socks-proxy.net/",
    "https://www.proxynova.com/proxy-server-list/",
    "https://hidemy.name/en/proxy-list/",
    "https://spys.me/proxy.txt",
    "https://proxy-daily.com/",
    "https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1",
    "https://list.proxylistplus.com/Fresh-HTTPS-Proxy-List-1",
    "https://list.proxylistplus.com/Fresh-SOCKS4-Proxy-List-1",
    "https://list.proxylistplus.com/Fresh-SOCKS5-Proxy-List-1",
    "https://checkerproxy.net/api/archive/all",
    "https://www.freeproxychecker.com/result/http_proxies.txt",
    "https://www.freeproxychecker.com/result/https_proxies.txt",
    "https://www.freeproxychecker.com/result/socks4_proxies.txt",
    "https://www.freeproxychecker.com/result/socks5_proxies.txt",
    "https://www.cool-proxy.net/proxies.txt",
    "https://www.my-proxy.com/free-proxy-list.html",
    "https://www.ipaddressguide.com/proxy-list",
    "https://www.geonode.com/free-proxy-list",
    "https://proxylist.geonode.com/api/proxy-list",
    "https://www.proxydocker.com/en/proxylist",
    "https://proxypool.scrapeops.io/api/proxylist",
    "https://proxylist.me/free-proxy-list",
    "https://www.proxydatabase.com/free-proxy-list",
    "https://www.letushide.com/free-proxy-list",
    "https://www.proxynode.net/free-proxy-list",
    "https://www.proxychecker.net/free-proxy-list",
    "https://proxydb.net/",
    "https://proxylists.net/http.txt",
    "https://proxylists.net/https.txt",
    "https://www.proxyrotator.com/free-proxy-list",
    "https://www.proxyserverlist24.top/",
    "https://www.hide-my-ip.com/proxylist.shtml",
    "https://www.netzwelt.de/proxy-list",
    "https://www.freeproxylists.net/",
    "https://proxybunker.com/",
    "https://proxylist.live/",
    "https://proxyscrape.com/free-proxy-list",
    "https://proxy.rudnkh.me/txt",
    "https://free-proxy-list.net/anonymous-proxy.html",
    "https://free-proxy-list.net/uk-proxy.html",
    "https://www.ip2world.com/proxy",
    "https://openproxy.space/list",
    "https://proxy.l337.tech/txt",
    "https://www.proxylists.me/free-proxy-list",
]

# Store valid proxies
valid_proxies = []


def fetch_proxies():
    """Fetches proxies from multiple sources with clean output."""
    proxy_list = set()
    failed_sources = 0

    for url in PROXY_SOURCES:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                for line in response.text.splitlines():
                    line = line.strip()
                    if ":" in line and line.replace(":", "").replace(".", "").isdigit():
                        proxy_list.add(line)
        except requests.RequestException:
            print(f"[X] Failed to fetch from {url}")
            failed_sources += 1

    print(f"[X] Total failed sources: {failed_sources}/{len(PROXY_SOURCES)}")
    return list(proxy_list)


def test_proxy(proxy):
    """Tests a proxy by checking response time."""
    global valid_proxies
    test_url = "http://ip-api.com/json/"  # Lightweight IP check

    try:
        start = time.time()
        response = requests.get(
            test_url,
            proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
            timeout=PROXY_TIMEOUT,
        )
        latency = time.time() - start

        if response.status_code == 200:
            with threading.Lock():
                valid_proxies.append(proxy)
                print(f"[+] Working Proxy: {proxy} (Response Time: {latency:.2f}s)")

    except requests.RequestException:
        pass  # Ignore failed proxies


def main():
    """Main function to scrape and validate proxies."""
    print(f"[~] Fetching proxies from {len(PROXY_SOURCES)} sources...")
    proxies = fetch_proxies()

    if not proxies:
        print("[X] No proxies found.")
        return

    if CHECK_PROXIES:
        print(f"[~] Testing {len(proxies)} proxies with timeout {PROXY_TIMEOUT}s...")
        threads = []
        for proxy in proxies:
            if len(threads) >= THREADS:
                for t in threads:
                    t.join()
                threads = []

            thread = threading.Thread(target=test_proxy, args=(proxy,))
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

        save_list = valid_proxies
        print(f"[!] Saved {len(valid_proxies)} working proxies to {OUTPUT_FILE} ✅")
    else:
        print(f"[~] Proxy checking disabled. Saving all {len(proxies)} proxies.")
        save_list = proxies

    # Save to file
    with open(OUTPUT_FILE, "w") as f:
        for proxy in save_list:
            f.write(proxy + "\n")


if __name__ == "__main__":
    main()
