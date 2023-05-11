@echo off

copy ytDownloader.py .venv

echo ytDownloader.py copied

copy images/icon.ico .venv

echo icon.ico copied

copy dependencies.md .venv

echo dependencies.md copied

cd .venv

Rem create requirement.txt file
setlocal

:: Empty the contents of the file - just for testing this script
type nul >"requirements.txt"

:: Unset the flag if for some reason it's been set beforehand
set dependencies=

:: Tokenize the contents - everything after the first delimiter
:: (in this case space) will be contained in the second token (%%j)
for /f "tokens=1,*" %%i in (dependencies.md) do (
    if "%%~i"=="##" (
        if not defined dependencies (
            set "dependencies=true"
        ) else (
            set "dependencies="
        )
    ) else if defined dependencies if "%%~i"=="-" (
        >>"requirements.txt" echo(%%~j)
    )
)


echo;requirements.txt created

python -m venv ytDownloader

@echo on
pip install -r requirements.txt

call ytDownloader\Scripts\activate.bat

pyinstaller ytDownloader.py -F --icon=icon.ico --upx-dir upx

call ytDownloader\Scripts\deactivate.bat

Rem Cleanup
del ytDownloader.py
echo ytDownloader.py deleted

del icon.ico
echo icon.ico deleted

del requirements.txt
echo requirements.txt deleted

del dependencies.md
echo dependencies.md deleted

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
