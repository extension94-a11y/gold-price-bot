import requests

url = "https://api.telegram.org/bot<8320369580:AAFQXI51lJ6qznE3AhhapGbQRnybeUvvVek>/getMe"
response = requests.get(url)
print(response.status_code, response.text)
