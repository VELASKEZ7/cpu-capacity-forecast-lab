$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$inputFile = Join-Path $root "data\cpu_history.csv"
$outputFile = Join-Path $root "out\forecast_report.json"
$entrypoint = Join-Path $root "src\cpu_forecast.py"

python $entrypoint --input $inputFile --output $outputFile --horizon 24

Write-Host "Forecast generado en: $outputFile"
