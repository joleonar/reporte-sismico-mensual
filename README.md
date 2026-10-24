# Generador Automatizado de Reportes Sísmicos Mensuales

Pipeline en Python y Batch para la extracción de sismicidad desde SEISAN, generación de mapas epicentrales y compilación de boletines mensuales en formato PDF.

## Características

- **Extracción de Catálogo:** Automatización de `select.exe` de SEISAN mediante script por lotes (`run_select.bat`).
- **Cartografía y Análisis:** Generación de mapas epicentrales y gráficos de distribución sismotectónica utilizando PyGMT y Matplotlib.
- **Maquetación Editorial:** Compilación automatizada de reportes en PDF con ReportLab (cálculo dinámico de dimensiones de imagen, tablas de contingencia regional y estilos proporcionales).

## Estructura del Repositorio

- `main.py`: Punto de entrada del flujo de procesamiento y orquestación.
- `crea_reportepdf.py`: Lógica de maquetación y estilos del PDF en ReportLab.
- `funciones_graficos.py`: Rutinas de graficación y cartografía.
- `run_select.bat`: Script de Windows para descargar select.out desde SEISAN filtrado por fechas y coordenadas.
- `Genera_reporte.ipynb`: Cuaderno Jupyter con pruebas interactivas del pipeline.
- `cintillo_*.png` / `cintillo_*.jpeg`: Recursos gráficos institucionales de cabecera y pie de página.
- `fallas2015.txt`: Trazas tectónicas de fallas activas.
- `verde.cpt`: Atchio cpt usado por PyGMT para graficar la topografía 

## Requisitos

- Python 3.x
- SEISAN (con `select.exe` en el PATH)
- Librerías Python: `reportlab`, `pandas`, `pygmt`, `os`, `matplotlib`

## Uso

1. Ejecutar el filtrado y extracción del catálogo:
   ```cmd
   run_select.bat 20260301