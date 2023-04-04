import requests

url = 'https://www.instagram.com/'

proxies = {
    'https': '115.68.221.147:80',
    'http': '115.68.221.147:80',
}

response = requests.get(url, proxies=proxies, timeout=15)
print(response.status_code)
print(response.elapsed.total_seconds())