# GeoNode Proxy Checker

A Python tool to fetch, check, and analyze proxies from the GeoNode API. This tool helps you find working proxies and identify the fastest ones for your needs.

## Features

- 🔄 Fetches proxies from GeoNode API
- ✅ Tests both HTTP and HTTPS protocols
- ⚡ Measures proxy response times
- 📊 Displays detailed proxy information
- 📝 Saves results in multiple formats
- 🚀 Concurrent proxy checking
- 🌍 Country and anonymity level information
- 📈 Speed and uptime statistics

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/geonode-proxy-checker.git
cd geonode-proxy-checker
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Basic usage:

```bash
python geonode_proxy_checker.py -p 2
```

### Command Line Arguments

| Argument         | Short | Default             | Description                                      |
| ---------------- | ----- | ------------------- | ------------------------------------------------ |
| `--pages`        | `-p`  | 1                   | Number of pages to fetch from GeoNode API        |
| `--timeout`      | `-t`  | 10                  | Timeout in seconds for each request              |
| `--workers`      | `-w`  | 10                  | Number of concurrent workers                     |
| `--output`       | `-o`  | proxy_results.txt   | Output file for detailed results                 |
| `--working-file` |       | working_proxies.txt | Output file for working proxies (IP:PORT format) |
| `--top`          |       | 10                  | Number of fastest proxies to display             |

### Examples

1. Check proxies from 3 pages with custom timeout:

```bash
python geonode_proxy_checker.py -p 3 -t 5
```

2. Use more concurrent workers for faster checking:

```bash
python geonode_proxy_checker.py -p 2 -w 20
```

3. Save working proxies to a custom file:

```bash
python geonode_proxy_checker.py -p 2 --working-file my_proxies.txt
```

4. Show top 20 fastest proxies:

```bash
python geonode_proxy_checker.py -p 2 --top 20
```

## Output Files

The script generates three output files:

1. `proxy_results.txt`

   - Detailed information about all checked proxies
   - Includes country, anonymity level, speed, uptime
   - Response times and error messages

2. `fastest_proxies.txt`

   - Table of fastest working proxies
   - Sorted by response time
   - Includes detailed metrics

3. `working_proxies.txt`
   - Simple list of working proxies
   - Format: `IP:PORT`
   - One proxy per line

## Example Output

### Console Output

```
Starting proxy fetch and check process...
Fetching page 1...
Successfully fetched 500 proxies from page 1

Checking 500 proxies with 10 workers...
[HTTP OK] 192.168.1.1:8080 - 150ms
[HTTPS OK] 192.168.1.1:8080 - 200ms
...

=== Summary ===
Total proxies checked: 500
Working proxies: 45
HTTP working: 40
HTTPS working: 35
Failed proxies: 455

=== Top 10 Fastest Proxies ===
+------------------+---------+------------+---------------+-----------+--------+--------+
| Proxy            | Country | Anonymity  | Response Time | Protocols | Speed  | UpTime |
+==================+=========+============+===============+===========+========+========+
| 192.168.1.1:8080 | US      | elite      | 150ms        | HTTP,HTTPS| 1000   | 95%    |
...
```

### working_proxies.txt

```
192.168.1.1:8080
10.0.0.1:3128
proxy.example.com:80
```

## Requirements

- Python 3.6+
- requests>=2.31.0
- tqdm>=4.65.0
- tabulate>=0.9.0

## Notes

- The script includes a 1-second delay between API requests to be respectful to the GeoNode API
- Proxies are tested against httpbin.org for reliability
- Response times are measured in milliseconds
- Both HTTP and HTTPS protocols are tested if supported by the proxy

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
