import requests
import concurrent.futures
import time
from typing import List, Dict, Tuple
import argparse
from datetime import datetime

class ProxyChecker:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.test_urls = {
            'http': 'http://httpbin.org/ip',
            'https': 'https://httpbin.org/ip'
        }

    def check_proxy(self, proxy: str) -> Dict:
        """
        Check if a proxy is working by testing both HTTP and HTTPS protocols
        """
        result = {
            'proxy': proxy,
            'http': False,
            'https': False,
            'response_time': None,
            'error': None
        }

        # Test HTTP
        try:
            start_time = time.time()
            response = requests.get(
                self.test_urls['http'],
                proxies={'http': f'http://{proxy}'},
                timeout=self.timeout
            )
            if response.status_code == 200:
                result['http'] = True
                result['response_time'] = round((time.time() - start_time) * 1000, 2)  # Convert to ms
        except Exception as e:
            result['error'] = str(e)

        # Test HTTPS
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
        except Exception as e:
            if not result['error']:
                result['error'] = str(e)

        return result

    def check_proxies(self, proxies: List[str], max_workers: int = 10) -> List[Dict]:
        """
        Check multiple proxies concurrently
        """
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {executor.submit(self.check_proxy, proxy): proxy for proxy in proxies}
            for future in concurrent.futures.as_completed(future_to_proxy):
                results.append(future.result())
        return results

def load_proxies(file_path: str) -> List[str]:
    """
    Load proxies from a file (one proxy per line)
    """
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def save_results(results: List[Dict], output_file: str):
    """
    Save results to a file
    """
    with open(output_file, 'w') as f:
        f.write(f"Proxy Check Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-" * 80 + "\n")
        for result in results:
            f.write(f"Proxy: {result['proxy']}\n")
            f.write(f"HTTP Working: {result['http']}\n")
            f.write(f"HTTPS Working: {result['https']}\n")
            if result['response_time']:
                f.write(f"Response Time: {result['response_time']}ms\n")
            if result['error']:
                f.write(f"Error: {result['error']}\n")
            f.write("-" * 80 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Check if proxies are alive')
    parser.add_argument('--input', '-i', required=True, help='Input file containing proxies (one per line)')
    parser.add_argument('--output', '-o', default='proxy_results.txt', help='Output file for results')
    parser.add_argument('--timeout', '-t', type=int, default=10, help='Timeout in seconds for each request')
    parser.add_argument('--workers', '-w', type=int, default=10, help='Number of concurrent workers')
    args = parser.parse_args()

    # Load proxies
    try:
        proxies = load_proxies(args.input)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found")
        return

    print(f"Loaded {len(proxies)} proxies from {args.input}")
    print("Checking proxies...")

    # Initialize checker and check proxies
    checker = ProxyChecker(timeout=args.timeout)
    results = checker.check_proxies(proxies, max_workers=args.workers)

    # Save results
    save_results(results, args.output)

    # Print summary
    working_proxies = [r for r in results if r['http'] or r['https']]
    print(f"\nResults saved to {args.output}")
    print(f"Total proxies checked: {len(results)}")
    print(f"Working proxies: {len(working_proxies)}")
    print(f"Failed proxies: {len(results) - len(working_proxies)}")

if __name__ == "__main__":
    main() 