@echo off
setlocal EnableDelayedExpansion

:: -------------------------------------------------------------
:: Parámetros configurables (valores por defecto)
:: -------------------------------------------------------------
if not "%~1"=="" (
    set "START_TIME=%~1"
) else (
    set "START_TIME=20260101"
)

set "MAG_MIN=0.5"
set "MAG_MAX=999.0"
set "LAT_MIN=5.0"
set "LAT_MAX=14.0"
set "LON_MIN=-74.0"
set "LON_MAX=-58.0"
set "NO_MIN=3"
set "NO_MAX=999"
set "END_TIME="
set "DATABASE=FUNV"
set "AUDIT_SCRIPT=main.py"
set "OUTPUT_FILE=select.out"

echo ==========================================================
echo  Ejecutando SEISAN select.exe
echo  Region: Lat [!LAT_MIN!,!LAT_MAX!] ^| Lon [!LON_MIN!,!LON_MAX!]
echo  Rango Temporal: !START_TIME! -^> !END_TIME!
echo ==========================================================

:: Verificar existencia del script auditor
 if not exist "%AUDIT_SCRIPT%" (
     echo [ERROR] No se encontro el script auditor '%AUDIT_SCRIPT%'.
    exit /b 1
 )

:: Limpiar salida previa si existe
if exist "%OUTPUT_FILE%" (
    del /f /q "%OUTPUT_FILE%"
)

:: -------------------------------------------------------------
:: Ejecución de select.exe canalizando las respuestas
:: Nota: el último 'echo.' simula presionar Enter en blanco
:: -------------------------------------------------------------
(
    echo %DATABASE%
    echo s
    echo %START_TIME%
    echo.
    echo 6
    echo %MAG_MIN%
    echo %MAG_MAX%
    echo 7
    echo %LAT_MIN%
    echo %LAT_MAX%
    echo 8
    echo %LON_MIN%
    echo %LON_MAX%
    echo 11
    echo %NO_MIN%
    echo %NO_MAX%
    echo.
) | select

:: Verificar que select.out existe y no está vacío (tamaño > 0)
if not exist "%OUTPUT_FILE%" (
    echo [ERROR] No se genero '%OUTPUT_FILE%'. Revisa los parametros o catalogo.
    exit /b 1
)

for %%A in ("%OUTPUT_FILE%") do (
    if %%~zA equ 0 (
        echo [ERROR] '%OUTPUT_FILE%' esta vacio. Revisa los parametros de entrada o catalogo.
        exit /b 1
    )
)

:: Limpieza de archivos temporales de SEISAN
if exist "select.inp" del /f /q "select.inp"
if exist "waveform_names.out" del /f /q "waveform_names.out"
if exist "index.out" del /f /q "index.out"

echo [+] Extraccion finalizada en '%OUTPUT_FILE%'.
echo [*] Ejecutando auditoria con %AUDIT_SCRIPT%...

python "%AUDIT_SCRIPT%"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Ocurrio un error al ejecutar %AUDIT_SCRIPT%.
    exit /b %ERRORLEVEL%
)

echo [+] Flujo completado.
endlocal