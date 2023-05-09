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

echo;Checksum Created

cd ../


REM remove last line and any spaces
SetLocal DisableDelayedExpansion

Set "SrcFile=readme.md"

If Not Exist "%SrcFile%" Exit /B
Copy /Y "%SrcFile%" "%SrcFile%.bak">Nul 2>&1||Exit /B

(   Set "Line="
    For /F "UseBackQ Delims=" %%A In ("%SrcFile%.bak") Do (
        SetLocal EnableDelayedExpansion
        If Defined Line Echo !Line!
        EndLocal
        Set "Line=%%A"))>"%SrcFile%"
EndLocal

REM add checksum to the end

Set out="."
(
    Echo;%$Value%
) >> %out%\README.md

REM delete the backup since it is unnecessary
del README.md.bak

Exit /B
