# CPU Capacity Forecast Lab

Predice demanda de CPU para la siguiente ventana operativa.

## Que hace
- Lee historico en `data/cpu_history.csv`
- Compara modelos: regresion lineal vs moving average
- Pronostica 24 puntos futuros
- Selecciona automaticamente el modelo con menor MAPE
- Calcula recomendacion de capacidad (vCPU)
- Genera recomendacion de capacidad en `out/forecast_report.json`
- Exporta tambien `out/forecast.csv` y `out/forecast_report.md`

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
