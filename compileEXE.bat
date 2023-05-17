@echo off

@REM copy yt_downloader.py .venv

@REM echo yt_downloader.py copied

@REM copy images\icon.ico .venv

@REM echo icon.ico copied

@REM copy dependencies.md .venv

@REM echo dependencies.md copied

cd .venv

@REM Rem create requirement.txt file
@REM setlocal

@REM :: Empty the contents of the file - just for testing this script
@REM type nul >"requirements.txt"

@REM :: Unset the flag if for some reason it's been set beforehand
@REM set dependencies=

@REM :: Tokenize the contents - everything after the first delimiter
@REM :: (in this case space) will be contained in the second token (%%j)
@REM for /f "tokens=1,*" %%i in (dependencies.md) do (
@REM     if "%%~i"=="##" (
@REM         if not defined dependencies (
@REM             set "dependencies=true"
@REM         ) else (
@REM             set "dependencies="
@REM         )
@REM     ) else if defined dependencies if "%%~i"=="-" (
@REM         >>"requirements.txt" echo(%%~j)
@REM     )
@REM )


@REM echo;requirements.txt created

@REM python -m venv VirtualytDownloader

@REM @echo on
@REM pip install -r requirements.txt

@REM call VirtualytDownloader\Scripts\activate.bat

@REM pyinstaller ytDownloader.py -F --icon=icon.ico

@REM call VirtualytDownloader\Scripts\deactivate.bat

@REM Rem Cleanup
@REM del yt_downloader.py
@REM echo yt_downloader.py deleted

@REM del icon.ico
@REM echo icon.ico deleted

@REM del requirements.txt
@REM echo requirements.txt deleted

@REM del dependencies.md
@REM echo dependencies.md deleted

if exist .\build rmdir .\build /S /Q
if exist .\VirtualytDownloader rmdir .\VirtualytDownloader /S /Q
if exist .\VirtualytDownloader rmdir .\VirtualytDownloader /S /Q
if exist ytDownloader.spec del ytDownloader.spec /S /Q

@REM for /f "delims=" %%a in ('powershell .\SHA256CheckSum.ps1') do Set "$Value=%%a"

@REM echo;Checksum Created

@REM cd ../


@REM REM remove last line and any spaces
@REM SetLocal DisableDelayedExpansion

@REM Set "SrcFile=readme.md"

@REM If Not Exist "%SrcFile%" Exit /B
@REM Copy /Y "%SrcFile%" "%SrcFile%.bak">Nul 2>&1||Exit /B

@REM (   Set "Line="
@REM     For /F "UseBackQ Delims=" %%A In ("%SrcFile%.bak") Do (
@REM         SetLocal EnableDelayedExpansion
@REM         If Defined Line Echo !Line!
@REM         EndLocal
@REM         Set "Line=%%A"))>"%SrcFile%"
@REM EndLocal

@REM REM add checksum to the end

@REM Set out="."
@REM (
@REM     Echo;%$Value%
@REM ) >> %out%\README.md

@REM REM delete the backup since it is unnecessary
@REM del README.md.bak

@REM Exit /B
