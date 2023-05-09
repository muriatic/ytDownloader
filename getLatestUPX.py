import requests

UPXLink = "https://api.github.com/repos/upx/upx/releases/latest"

response = requests.get(UPXLink)

print(response.json()["assets"])