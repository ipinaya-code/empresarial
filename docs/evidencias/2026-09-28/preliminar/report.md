# Resultados medidos

Cada fila es una ejecución; valores de latencia en ms.

| Variante | VU | Repetición | p50 | p95 | p99 | req/s | Errores | Checks | Salida k6 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 50 | 1 | 5.06 | 57.90 | 85.31 | 48.96 | 0.00% | 100.00% | 0 |
| baseline | 200 | 1 | 7.35 | 118.97 | 336.02 | 190.92 | 0.00% | 100.00% | 0 |
| baseline | 500 | 1 | 51.65 | 285.74 | 852.21 | 444.54 | 0.00% | 100.00% | 99 |
| refactored | 50 | 1 | 4.34 | 60.08 | 103.88 | 49.17 | 0.00% | 100.00% | 0 |
| refactored | 200 | 1 | 6.31 | 108.92 | 301.99 | 192.38 | 0.00% | 100.00% | 0 |
| refactored | 500 | 1 | 11.65 | 295.59 | 787.39 | 459.94 | 0.00% | 100.00% | 99 |
| refactored | 50 | 2 | 4.16 | 58.45 | 101.45 | 49.23 | 0.00% | 100.00% | 0 |
| refactored | 200 | 2 | 5.45 | 120.91 | 290.01 | 192.85 | 0.00% | 100.00% | 0 |
| refactored | 500 | 2 | 9.01 | 248.37 | 763.65 | 463.64 | 0.00% | 100.00% | 99 |
| baseline | 50 | 2 | 4.84 | 49.29 | 82.58 | 49.12 | 0.00% | 100.00% | 0 |
| baseline | 200 | 2 | 6.72 | 108.56 | 337.79 | 190.48 | 0.00% | 100.00% | 0 |
| baseline | 500 | 2 | 58.69 | 366.28 | 875.05 | 438.74 | 0.00% | 100.00% | 99 |
| baseline | 50 | 3 | 4.88 | 45.09 | 82.62 | 49.07 | 0.00% | 100.00% | 0 |
| baseline | 200 | 3 | 6.67 | 121.32 | 325.58 | 189.90 | 0.00% | 100.00% | 0 |
| baseline | 500 | 3 | 49.24 | 337.77 | 879.38 | 442.41 | 0.00% | 100.00% | 99 |
| refactored | 50 | 3 | 4.64 | 38.78 | 82.72 | 49.28 | 0.00% | 100.00% | 0 |
| refactored | 200 | 3 | 6.21 | 113.18 | 318.39 | 192.30 | 0.00% | 100.00% | 0 |
| refactored | 500 | 3 | 12.09 | 282.89 | 799.08 | 458.67 | 0.00% | 100.00% | 99 |

Medianas de p95 entre repeticiones (no percentil agregado de todas las solicitudes):

| VU | Baseline p95 | Refactor p95 | Cambio relativo |
|---|---:|---:|---:|
| 50 | 49.29 | 58.45 | -18.6% |
| 200 | 118.97 | 113.18 | 4.9% |
| 500 | 337.77 | 282.89 | 16.2% |

Salida 99 significa umbral incumplido; 0 indica todos los umbrales satisfechos.
Un porcentaje positivo representa reducción de la mediana de p95 en este experimento.
Generador y servicio comparten host. No extrapolar a tráfico institucional o disponibilidad mensual.
