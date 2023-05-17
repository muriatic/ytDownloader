import requests
import zipfile
import os
import urllib.request
import shutil

UPXLink = "https://api.github.com/repos/upx/upx/releases/latest"

response = requests.get(UPXLink)

body = response.json()["body"]

UPXFolder = '.venv/upx/'

windowsInstaller = body.split('UPX - X64 Win64 version')[0]
windowsInstaller = windowsInstaller.rsplit('|', 2)[1]
windowsInstaller = windowsInstaller.split('(')[1]
windowsInstallerLink = windowsInstaller.split(')')[0]

# folder name
folderName = windowsInstallerLink.rsplit('/', 1)[1]
folderName = folderName.removesuffix('.zip')

zip_path, _ = urllib.request.urlretrieve(windowsInstallerLink)
zipData = zipfile.ZipFile(zip_path)

with zipfile.ZipFile(zip_path, "r") as f:
    f.extractall()

files = [f for f in os.listdir(folderName)]

for file in files:
    shutil.move(folderName + '/' + file, UPXFolder + file)

try:
    shutil.rmtree(folderName)
    # os.remove
except OSError:
    pass
