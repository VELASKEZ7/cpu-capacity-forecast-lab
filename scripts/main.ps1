$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$inputFile = Join-Path $root "data\cpu_history.csv"
$outputFile = Join-Path $root "out\forecast_report.json"
$csvFile = Join-Path $root "out\forecast.csv"
$mdFile = Join-Path $root "out\forecast_report.md"
$entrypoint = Join-Path $root "src\cpu_forecast.py"

python $entrypoint --input $inputFile --output $outputFile --horizon 24 --current-vcpu 8 --csv-output $csvFile --markdown-output $mdFile

Write-Host "Forecast generado en: $outputFile"
Write-Host "CSV generado en: $csvFile"
Write-Host "Markdown generado en: $mdFile"
