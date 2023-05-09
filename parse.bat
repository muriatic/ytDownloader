@echo off
@REM for /f "delims=" %%L in (dependencies.md) do set %%L
@REM echo var1=%Pytube%
@REM echo var2=%var2%
@REM echo var3=%var3%

@REM for /F "eol=; tokens=2,3* delims=," %%i in (dependencies.md) do @echo %%i %%j %%k

@REM for /f "tokens= delims="


for /F "tokens=2,3" %%i in (dependencies.md) do call :process %%i %%j %%k

:process
set VAR1=%1
set VAR2=%2
echo %VAR1%
echo %VAR2%

Set out="."
(
    Echo;pytube==15.0.0
    Echo;moviepy==1.0.3
    Echo;keyboard==0.13.5
    Echo;pyinstaller==5.10.1
) > "%out%\requirements.txt"

@REM set VAR3=%3
@REM set VAR4=%4
@REM @echo %VAR3%
@REM @echo %VAR4%

