import requests

url = "http://127.0.0.1:5000/screening-results/1"

response = requests.get(url)

print(response.json())