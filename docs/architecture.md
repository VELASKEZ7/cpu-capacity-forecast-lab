# Arquitectura

Flujo analitico:

1. Cargar serie temporal de CPU desde CSV.
2. Dividir en train/validacion.
3. Ajustar regresion lineal sobre indice temporal.
4. Medir MAPE en validacion.
5. Pronosticar 24 horas y recomendar accion:
   - `scale-up` si pico pronosticado >= 80%
   - `maintain` en caso contrario
