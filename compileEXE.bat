copy ytDownloader.py .venv
copy icon.ico .venv

cd .venv

@echo off
Set "out=."
(
    Echo;pytube==15.0.0
    Echo;moviepy==1.0.3
    Echo;keyboard==0.13.5
) > "%out%\requirements.txt"

echo;requirements.txt created

@echo on
python -m venv ytDownloader

cmd /k "pip install -r requirements.txt"

ytDownloader\Scripts\activate.bat

start /b "python.exe" "pyinstaller ytDownloader.py -F --icon=icon.ico --upx-dir upx"