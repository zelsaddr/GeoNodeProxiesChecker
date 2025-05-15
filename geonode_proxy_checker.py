import requests
import concurrent.futures
import time
from typing import List, Dict, Tuple
import argparse
from datetime import datetime
import json
import sys
from tqdm import tqdm
from tabulate import tabulate

class GeoNodeProxyFetcher:
    def __init__(self):
        self.base_url = "https://proxylist.geonode.com/api/proxy-list"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_proxies(self, page: int = 1, limit: int = 500) -> List[Dict]:
        """
        Fetch proxies from GeoNode API
        """
        params = {
            'limit': limit,
            'page': page,
            'sort_by': 'lastChecked',
            'sort_type': 'desc'
        }

        try:
            print(f"\nFetching page {page}...")
            response = requests.get(self.base_url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('data'):
                print(f"No data found on page {page}")
                return []
            
            proxies = []
            for proxy in data['data']:
                proxy_info = {
                    'ip': proxy['ip'],
                    'port': proxy['port'],
                    'protocols': proxy['protocols'],
                    'country': proxy.get('country', 'Unknown'),
                    'anonymityLevel': proxy.get('anonymityLevel', 'Unknown'),
                    'speed': proxy.get('speed', 0),
                    'upTime': proxy.get('upTime', 0)
                }
                proxies.append(proxy_info)
            
            print(f"Successfully fetched {len(proxies)} proxies from page {page}")
            return proxies
        except Exception as e:
            print(f"Error fetching proxies from page {page}: {str(e)}")
            return []

class ProxyChecker:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.test_urls = {
            'http': 'http://httpbin.org/ip',
            'https': 'https://httpbin.org/ip'
        }

    def check_proxy(self, proxy_info: Dict) -> Dict:
        """
        Check if a proxy is working by testing both HTTP and HTTPS protocols
        """
        proxy = f"{proxy_info['ip']}:{proxy_info['port']}"
        result = {
            'proxy': proxy,
            'country': proxy_info['country'],
            'anonymityLevel': proxy_info['anonymityLevel'],
            'speed': proxy_info['speed'],
            'upTime': proxy_info['upTime'],
            'http': False,
            'https': False,
            'response_time': None,
            'error': None
        }

        # Test HTTP
        if 'http' in proxy_info['protocols']:
            try:
                start_time = time.time()
                response = requests.get(
                    self.test_urls['http'],
                    proxies={'http': f'http://{proxy}'},
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    result['http'] = True
                    result['response_time'] = round((time.time() - start_time) * 1000, 2)
                    print(f"[HTTP OK] {proxy} - {result['response_time']}ms")
            except Exception as e:
                result['error'] = str(e)
                print(f"[HTTP FAIL] {proxy} - {str(e)}")

        # Test HTTPS
        if 'https' in proxy_info['protocols']:
            try:
                start_time = time.time()
                response = requests.get(
                    self.test_urls['https'],
                    proxies={'https': f'https://{proxy}'},
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    result['https'] = True
                    if not result['response_time']:
                        result['response_time'] = round((time.time() - start_time) * 1000, 2)
                    print(f"[HTTPS OK] {proxy} - {result['response_time']}ms")
            except Exception as e:
                if not result['error']:
                    result['error'] = str(e)
                print(f"[HTTPS FAIL] {proxy} - {str(e)}")

        return result

    def check_proxies(self, proxies: List[Dict], max_workers: int = 10) -> List[Dict]:
        """
        Check multiple proxies concurrently
        """
        results = []
        print(f"\nChecking {len(proxies)} proxies with {max_workers} workers...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {executor.submit(self.check_proxy, proxy): proxy for proxy in proxies}
            
            # Create progress bar
            with tqdm(total=len(proxies), desc="Checking proxies", unit="proxy") as pbar:
                for future in concurrent.futures.as_completed(future_to_proxy):
                    results.append(future.result())
                    pbar.update(1)
                    
                    # Update progress bar description with current stats
                    working = len([r for r in results if r['http'] or r['https']])
                    pbar.set_description(f"Working: {working}/{len(results)}")
        
        return results

def save_results(results: List[Dict], output_file: str):
    """
    Save results to a file
    """
    print(f"\nSaving results to {output_file}...")
    with open(output_file, 'w') as f:
        f.write(f"Proxy Check Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-" * 100 + "\n")
        for result in results:
            f.write(f"Proxy: {result['proxy']}\n")
            f.write(f"Country: {result['country']}\n")
            f.write(f"Anonymity Level: {result['anonymityLevel']}\n")
            f.write(f"Speed: {result['speed']}\n")
            f.write(f"UpTime: {result['upTime']}%\n")
            f.write(f"HTTP Working: {result['http']}\n")
            f.write(f"HTTPS Working: {result['https']}\n")
            if result['response_time']:
                f.write(f"Response Time: {result['response_time']}ms\n")
            if result['error']:
                f.write(f"Error: {result['error']}\n")
            f.write("-" * 100 + "\n")
    print("Results saved successfully!")

def save_working_proxies(results: List[Dict], output_file: str = 'working_proxies.txt'):
    """
    Save working proxies in IP:PORT format
    """
    working_proxies = [r for r in results if r['http'] or r['https']]
    
    print(f"\nSaving {len(working_proxies)} working proxies to {output_file}...")
    with open(output_file, 'w') as f:
        for proxy in working_proxies:
            f.write(f"{proxy['proxy']}\n")
    print(f"Working proxies saved to {output_file}")

def print_summary(results: List[Dict], top_n: int = 10):
    """
    Print a detailed summary of the results with focus on fastest proxies
    """
    working_proxies = [r for r in results if r['http'] or r['https']]
    http_working = len([r for r in results if r['http']])
    https_working = len([r for r in results if r['https']])
    
    print("\n=== Summary ===")
    print(f"Total proxies checked: {len(results)}")
    print(f"Working proxies: {len(working_proxies)}")
    print(f"HTTP working: {http_working}")
    print(f"HTTPS working: {https_working}")
    print(f"Failed proxies: {len(results) - len(working_proxies)}")
    
    if working_proxies:
        # Sort proxies by response time
        sorted_proxies = sorted(working_proxies, key=lambda x: x['response_time'] if x['response_time'] else float('inf'))
        
        # Prepare data for tabulate
        table_data = []
        for proxy in sorted_proxies[:top_n]:
            protocols = []
            if proxy['http']:
                protocols.append('HTTP')
            if proxy['https']:
                protocols.append('HTTPS')
            
            table_data.append([
                proxy['proxy'],
                proxy['country'],
                proxy['anonymityLevel'],
                f"{proxy['response_time']}ms",
                ', '.join(protocols),
                f"{proxy['speed']}",
                f"{proxy['upTime']}%"
            ])
        
        # Print fastest proxies table
        print(f"\n=== Top {top_n} Fastest Proxies ===")
        print(tabulate(
            table_data,
            headers=['Proxy', 'Country', 'Anonymity', 'Response Time', 'Protocols', 'Speed', 'UpTime'],
            tablefmt='grid'
        ))
        
        # Save fastest proxies to a separate file
        fastest_file = 'fastest_proxies.txt'
        with open(fastest_file, 'w') as f:
            f.write(f"Top {top_n} Fastest Proxies - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(tabulate(
                table_data,
                headers=['Proxy', 'Country', 'Anonymity', 'Response Time', 'Protocols', 'Speed', 'UpTime'],
                tablefmt='grid'
            ))
        print(f"\nFastest proxies saved to {fastest_file}")

def main():
    parser = argparse.ArgumentParser(description='Fetch and check proxies from GeoNode API')
    parser.add_argument('--output', '-o', default='proxy_results.txt', help='Output file for results')
    parser.add_argument('--timeout', '-t', type=int, default=10, help='Timeout in seconds for each request')
    parser.add_argument('--workers', '-w', type=int, default=10, help='Number of concurrent workers')
    parser.add_argument('--pages', '-p', type=int, default=1, help='Number of pages to fetch')
    parser.add_argument('--top', type=int, default=10, help='Number of fastest proxies to display')
    parser.add_argument('--working-file', default='working_proxies.txt', help='Output file for working proxies in IP:PORT format')
    args = parser.parse_args()

    # Initialize fetcher and checker
    fetcher = GeoNodeProxyFetcher()
    checker = ProxyChecker(timeout=args.timeout)
    
    all_proxies = []
    print("Starting proxy fetch and check process...")
    
    # Fetch proxies from all pages
    for page in range(1, args.pages + 1):
        proxies = fetcher.fetch_proxies(page=page)
        if not proxies:
            print(f"No more proxies found on page {page}")
            break
        all_proxies.extend(proxies)
        time.sleep(1)  # Be nice to the API

    if not all_proxies:
        print("No proxies found!")
        return

    print(f"\nTotal proxies found: {len(all_proxies)}")
    
    # Check proxies
    results = checker.check_proxies(all_proxies, max_workers=args.workers)

    # Save results
    save_results(results, args.output)
    
    # Save working proxies in IP:PORT format
    save_working_proxies(results, args.working_file)

    # Print summary with fastest proxies
    print_summary(results, args.top)

if __name__ == "__main__":
    main() 