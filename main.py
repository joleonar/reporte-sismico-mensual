from funciones_graficos import *
from crea_reportepdf import construir_reporte_pdf

# 1. Procesa SELECT.OUT
df_sismos = parsear_nordic_select("select.out")
print(f"\n Procesado el archivo select.out, se encontraron {len(df_sismos)} eventos sísmicos")


# 2. Genera gráficos y mapa
rutas_fig = generar_graficos(df_sismos)
ruta_map = generate_map(df_sismos)
rutas_fig.update(ruta_map)
print(f"\n Se generaron los gráficos y mapas ")

# 3. Construye el reporte PDF
construir_reporte_pdf(df_sismos, rutas_fig)
print("\n Se generó el reporte PDF con éxito.")