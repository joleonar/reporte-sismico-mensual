# ==========================================
# 1. BIBLIOTECAS ESTÁNDAR DE PYTHON
# ==========================================
import os
import argparse
from datetime import datetime

# ==========================================
# 2. PROCESAMIENTO DE DATOS Y GRÁFICOS
# ==========================================
import pandas as pd
import numpy as np
import pygmt
import matplotlib.pyplot as plt


# ==========================================
# 2. Función para parsear SELECT.OUT
# ==========================================
def parsear_nordic_select(archivo_select):
    """
    Parsea la cabecera hipocentral (Línea Tipo 1) del formato Nordic de SEISAN.
    """
    eventos = []
    
    if not os.path.exists(archivo_select):
        raise FileNotFoundError(f"No se encontro el archivo: {archivo_select}")

    with open(archivo_select, 'r', encoding='latin-1') as f:
        for linea in f:
            # Una linea tipo 1 tiene al menos 80 caracteres y la posicion 80 suele ser '1' o espacio en cabecera
            if len(linea) >= 70:
                indicador_tipo = linea[79:80] if len(linea) >= 80 else ' '
                if indicador_tipo in ['1', ' ']:
                    try:
                        # Extraer campos segun el estandar Nordic
                        anio = linea[1:5].strip()
                        mes = linea[6:8].strip()
                        dia = linea[8:10].strip()
                        hora = linea[11:13].strip() or '00'
                        minuto = linea[13:15].strip() or '00'
                        seg_str = linea[16:20].strip() or '0.0'
                        seg = int(float(seg_str))

                        lat_str = linea[23:30].strip()
                        lon_str = linea[30:38].strip()
                        prof_str = linea[38:43].strip()
                        mag_str = linea[55:59].strip()
                        tipo_mag = linea[59:60].strip()

                        if not (anio and mes and dia and lat_str and lon_str):
                            continue

                        fecha_dt = datetime(int(anio), int(mes), int(dia), int(hora), int(minuto), seg)
                        lat = float(lat_str)
                        lon = float(lon_str)
                        prof = float(prof_str) if prof_str else 0.0
                        mag = float(mag_str) if mag_str else 0.0

                        eventos.append({
                            "fecha_hora": fecha_dt,
                            "dia": int(dia),
                            "lat": lat,
                            "lon": lon,
                            "profundidad": prof,
                            "magnitud": mag,
                            "tipo_mag": tipo_mag if tipo_mag else "Mw"
                        })
                    except (ValueError, IndexError):
                        continue

    df = pd.DataFrame(eventos)
    return df


# ==========================================
# 4. PROCESAMIENTO DE DATOS Y GRÁFICOS
# ==========================================
def format_grafico(axn):
    #Funcion para dar algunos formatos al grafico
    #Entrada: axes (axn),  etiqueta eje x (labelx), etiqueta eje y (labely)
    axn.spines['top'].set_visible(False)
    axn.spines['right'].set_visible(False)
    axn.spines['left'].set_visible(False)
    axn.tick_params(labelsize=16, labelright=True)
    #axn.get_yaxis().set_visible(False)
    
    axn.yaxis.grid(True, zorder=0, color='lightgray', linestyle='--')
    
    

def generar_graficos(df, out_dir="figuras_reporte"):
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Histograma de Magnitudes
    fig, ax=plt.subplots(figsize=(14,8), dpi=300)
    histo=ax.hist(df['magnitud'], bins=np.arange(1,9,1),edgecolor='k',alpha=1.0,color='darkorange',zorder=2)

    for n in range(len(histo[0])):
        if histo[0][n]!=0:
            ax.text(histo[1][n]+0.5,histo[0][n]+5,str(int(histo[0][n])),ha='center',fontsize=14, weight='bold')
        
    format_grafico(ax)        
    ax.set_xlabel("Magnitud",fontsize=14, fontweight='bold')
    ax.set_ylabel("Número de sismos", fontsize=14, fontweight='bold')

    ruta_hist = os.path.abspath(os.path.join(out_dir, "hist_magnitud.png"))
    fig.savefig(ruta_hist)
    plt.close(fig)

        
     # 2. Histograma Diario (Sismicidad acumulada en el mes)
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    conteo_diario = df.groupby('dia').size()
    bars = ax.bar(conteo_diario.index, conteo_diario.values, color="darkorange", edgecolor='k', width=0.8, zorder=2)
    for bar in bars:
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5, str(int(bar.get_height())),ha='center', color='k',
                fontsize=14)
    format_grafico(ax)
    #ax.set_title("Número de sismos por día", fontsize=14, fontweight="bold", pad=10)
    ax.set_xlabel("Día del mes", fontsize=14)
    #ax.grid(axis='y', linestyle='--', alpha=0.5)
    fig.tight_layout()
    
    ruta_diario = os.path.abspath(os.path.join(out_dir, "eventos_diarios.png"))
    fig.savefig(ruta_diario)
    plt.close(fig)

    return {
        "ruta_hist_mag": ruta_hist,
        "ruta_hist_diario": ruta_diario
    }

# ==========================================
# 5. CREACIÓN DE MAPA DE SISMICIDAD (PYGMT)
# ==========================================

def generate_map(df, out_dir="figuras_reporte"):
    
    """
    Genera el mapa de sismicidad mensual con PyGMT para Venezuela y areas adyacentes.
    """
    os.makedirs(out_dir, exist_ok=True)
    datos = df.copy()
    if 'mag' in datos.columns and 'magnitud' not in datos.columns:
        datos['magnitud'] = datos['mag']

    region = [-74.0, -58.0, 5.0, 14.0]

    # Separación por rangos de magnitud
    data_03 = datos[datos['magnitud'] < 3.0]
    data_34 = datos[(datos['magnitud'] >= 3.0) & (datos['magnitud'] < 4.0)]
    data_45 = datos[(datos['magnitud'] >= 4.0) & (datos['magnitud'] < 5.0)]
    data_5 = datos[datos['magnitud'] >= 5.0]

    # Paleta de colores topográfica
    cpt_relief = 'verde.cpt' if os.path.exists('verde.cpt') else 'geo'

    kwargs_grd = dict(
        grid='@earth_relief_15s',
        region=region,
        projection='M14.5c',
        cmap=cpt_relief,
    )

    fig = pygmt.Figure()

    # 1. Topografía sombreada
    fig.grdimage(shading=True, **kwargs_grd)

    # 2. Línea de costa, fronteras y ríos
    fig.coast(
        shorelines="0.5p,black",
        borders=['1/0.8p,gray20', '2/0.5p,gray40'],
        frame='a2f1',
        resolution='f',
        rivers='a/0.4p,deepskyblue4'
    )

    # 3. Rótulo geográfico
    fig.text(
        x=-68.0, 
        y=13.3, 
        text='Mar Caribe', 
        font='18p,Helvetica-Bold,white', 
        justify='MC'
    )

    # 4. Trazado de fallas activas (si existe el archivo en la ruta de trabajo)
    if os.path.exists("fallas2015.txt"):
        fig.plot(data="fallas2015.txt", pen="0.8p,red")

    # 5. Epicentros por rango de magnitud
    if not data_03.empty:
        fig.plot(x=data_03.lon, y=data_03.lat, style="c0.15c", fill='green', pen="0.3p,black")
    if not data_34.empty:
        fig.plot(x=data_34.lon, y=data_34.lat, style="c0.25c", fill='cyan', pen="0.3p,black")
    if not data_45.empty:
        fig.plot(x=data_45.lon, y=data_45.lat, style="c0.35c", fill='yellow', pen="0.4p,black")
    if not data_5.empty:
        fig.plot(x=data_5.lon, y=data_5.lat, style="c0.45c", fill='red', pen="0.5p,black")

    # 6. Leyenda de magnitudes
    ruta_leyenda = "legend_magnitud.txt"
      
    with pygmt.clib.Session() as session:
        session.call_module('gmtset', 'FONT_ANNOT_PRIMARY 7.5p')

    fig.legend(
        spec=ruta_leyenda,
        position='jBR+o0.15c+w3.6c/3.2c',
        box='+gwhite@20+p0.8p,gray30+r'
    )

   
    # 7. Guardar imagen final en alta resolución
    ruta_mapa = os.path.abspath(os.path.join(out_dir, "mapa_venezuela.png"))
    fig.savefig(ruta_mapa, dpi=300)
    #print(f"[OK] Mapa PyGMT generado: {out_png}")
    
    return {"ruta_mapa":ruta_mapa}

