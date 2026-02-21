# CPU Capacity Forecast Lab

Predice demanda de CPU para la siguiente ventana operativa.

## Que hace
- Lee historico en `data/cpu_history.csv`
- Ajusta regresion lineal simple
- Pronostica 24 puntos futuros
- Calcula MAPE contra muestra de validacion
- Genera recomendacion de capacidad en `out/forecast_report.json`

## Ejecutar
```powershell
cd C:\Users\Administrator\portfolio-redes-projects\cpu-capacity-forecast-lab
powershell -ExecutionPolicy Bypass -File .\scripts\main.ps1
```

## Probar
```powershell
cd C:\Users\Administrator\portfolio-redes-projects\cpu-capacity-forecast-lab
python -m unittest tests\test_cpu_forecast.py -v
```
