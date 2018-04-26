import requests

r = requests.get('https://api.binance.com/api/v1/ping')
print r.status_code
print r.content
print r.cookies
