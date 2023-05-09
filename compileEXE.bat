copy ytDownloader.py .venv
copy icon.ico .venv

cd .venv

@echo off
Set out="."
(
    Echo;pytube==15.0.0
    Echo;moviepy==1.0.3
    Echo;keyboard==0.13.5
    Echo;pyinstaller==5.10.1
) > "%out%\requirements.txt"

echo;requirements.txt created

@echo on
python -m venv ytDownloader

pip install -r requirements.txt

call ytDownloader\Scripts\activate.bat

pyinstaller ytDownloader.py -F --icon=icon.ico --upx-dir upx

call ytDownloader\Scripts\deactivate.bat

Rem Cleanup
del ytDownloader.py
del icon.ico
del requirements.txt

for /f "delims=" %%a in ('powershell .\SHA256CheckSum.ps1') do Set "$Value=%%a"

cd ../

Set out="."
(
    Echo;# SHA-256 Checksum:
    Echo;%$Value%
) > %out%\checksum.md

echo;checksum.md created