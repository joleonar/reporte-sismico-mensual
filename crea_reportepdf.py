# ==========================================
# 1. BIBLIOTECAS ESTÁNDAR DE PYTHON
# ==========================================
import os
import calendar
from datetime import datetime
import pandas as pd

# ==========================================
# 2. LIBRERÍAS PARA ACIÓN PDF (REPORTLAB)
# ==========================================
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, 
    Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from PIL import Image as PILImage


def agregar_cintillos(canvas, doc):
    """Inserta el cintillo superior e inferior en cada página generada."""

    canvas.saveState()
    ancho_pag, alto_pag = letter

    # Cintillo superior (ancho útil de 17.5 cm, centrado)
    cintillo_sup = "cintillo_superior.jpeg"
    if os.path.exists(cintillo_sup):
        canvas.drawImage(cintillo_sup, 2 * cm, alto_pag - 2.8 * cm, width=17.5 * cm, height=2.2 * cm, preserveAspectRatio=True)

    # Cintillo inferior
    cintillo_inf = "cintillo_inferior.png"
    if os.path.exists(cintillo_inf):
        canvas.drawImage(cintillo_inf, 2 * cm, 0.6 * cm, width=17.5 * cm, height=1.8 * cm, preserveAspectRatio=True)

    # Número de página en pie
    num_pag = canvas.getPageNumber()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawRightString(ancho_pag - 2 * cm, 0.8 * cm, f"Pág. {num_pag}")
    canvas.restoreState()

def construir_reporte_pdf(df, figuras):

    #  =================  Define variables a partir del dataframe ===========================
    df_sismos = df.copy()
    total_sismos = len(df_sismos)
    
    sismo_mayor = df_sismos.loc[df_sismos['magnitud'].idxmax()] if total_sismos > 0 else None
    min_mag=df['magnitud'].min()
    max_mag=df['magnitud'].max()
    fecha = df.iloc[0,0]
    meses_es = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    year = fecha.year
    mes_nombre = meses_es[fecha.month]
    _,last_day = calendar.monthrange(year,fecha.month)
    pdf_salida = "reporte_mensual"+'_'+mes_nombre+str(year)+".pdf"

    # =======================================================================================
    
    # Configuración de márgenes para dejar espacio a los cintillos
    doc = SimpleDocTemplate(
        pdf_salida,
        pagesize=letter,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=3.2 * cm,
        bottomMargin=2.4 * cm
    )

    styles = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        'TituloReporte',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#F54927'),
        alignment=1, # Centrado
        spaceAfter=4
    )
    estilo_subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=13,
        textColor=colors.HexColor('#F54927'),
        alignment=1,
        spaceAfter=10
    )
    estilo_cuerpo = ParagraphStyle(
        'Cuerpo',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        alignment=TA_JUSTIFY,
        leading=13,
        textColor=colors.HexColor('#111111')
    )
    estilo_pie_fig = ParagraphStyle(
        'PieFig',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=10,
        alignment=1,
        textColor=colors.HexColor('#111111')
    )

    story = []


    # ==================== PÁGINA 1 ====================
    story.append(Paragraph(f"REPORTE MENSUAL DE ACTIVIDAD SÍSMICA: 1° al {last_day} de {mes_nombre.upper()} {year}", estilo_titulo))
    #story.append(Paragraph(f"Período: {mes_nombre.upper()} {anio}", estilo_subtitulo))

    
    resumen_txt = (f"""
        Durante este mes se registraron <b>{total_sismos}</b> eventos sísmicos por el <b>Servicio Sismológico y de
        Alerta de Tsunamis (SSAT)</b> en la región comprendida entre la latitud 5° a 14° N y la longitud 58° a 74° O
        Las magnitudes de los sismos detectados variaron entre <b>{min_mag}</b> y <b>{max_mag}</b>. En la <b>Tabla 1</b>
        se muestra el número de eventos registrados según su ubicación geográfica y magnitud en tres regiones,
        occidente (longitud 69° a 74° O), centro (longitud 65° a 69°) y oriente (58° a 65° O) del país. En las 
        ilustraciones se muestra la distribución de los sismos por rangos de magnitud (Ilustración 1), número de
        sismos registrados por día (Ilustración 2) y el mapa con la ubicación epicentral discriminados por magnitud.""".replace("\n"," ")
    )
    story.append(Paragraph(resumen_txt, estilo_cuerpo))
    story.append(Spacer(1, 12))

    bins = [-74,-69,-65,-58]
    labels = ['Occidente','Centro','Oriente' ]
    bins_mag = [0,3,4,5,10]
    labels_mag = ['Mag < 3.0','3.0 <= Mag  < 4.0', '4.0 <= Mag <= 5.0', 'Mag >= 5.0']
    df_sismos['Región'] = pd.cut(df_sismos['lon'],bins=bins, labels = labels, right=False)
    df_sismos['Rango Mag']= pd.cut(df_sismos['magnitud'],bins=bins_mag, labels = labels_mag, right=False)
    grupos = df_sismos.groupby(['Región','Rango Mag'])['magnitud'].count()
    df_contingencia = grupos.unstack().fillna(0).astype(int)

   # Estilo de encabezado (negrita, centrado)
    estilo_th = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#111111')
    )
    
    # Estilo de etiquetas de región (Occidente, Centro, Oriente)
    estilo_lbl_region = ParagraphStyle(
        'RegionLabelStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#111111')
    )
    
    # Estilo para los números
    estilo_td = ParagraphStyle(
        'CellNumberStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#222222')
    )

    # 1. Cabecera en UNA SOLA FILA:
    # "Región" en la primera celda, seguida de los nombres de los rangos de magnitud
    fila_cabecera = [Paragraph("<b>Región</b>", estilo_th)]
    for col in df_contingencia.columns:
        # Reemplazar posibles secuencias LaTeX como \leq por el símbolo real ≤
        col_txt = str(col)
        fila_cabecera.append(Paragraph(f"<b>{col_txt}</b>", estilo_th))

    story.append(Paragraph("<b>Tabla 1.</b> Distribución de sismos registrados por región y rango de magnitud.", estilo_pie_fig))
    story.append(Spacer(1, 12))
    matriz_tabla = [fila_cabecera]

    # 2. Filas de datos
    for region, fila in df_contingencia.iterrows():
        fila_celdas = [Paragraph(str(region), estilo_lbl_region)]
        for valor in fila:
            fila_celdas.append(Paragraph(str(int(valor)), estilo_td))
        matriz_tabla.append(fila_celdas)

    # 3. Anchos de columnas ajustados (1 fila para Región y 4 para magnitudes)
    col_widths = [3.5 * cm] + [3.0 * cm] * len(df_contingencia.columns)

    tabla = Table(matriz_tabla, colWidths=col_widths)

    # 4. Estilos visuales: la línea divisoria ahora va debajo de la fila 0
    estilos = [
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),

        # Línea horizontal ENCIMA de la cabecera (fila 0)
        ('LINEABOVE', (0, 0), (-1, 0), 1.0, colors.HexColor('#a0a0a0')),
        
        # Línea horizontal divisoria justo debajo de la cabecera (fila 0)
        ('LINEBELOW', (0, 0), (-1, 0), 0.8, colors.HexColor('#a0a0a0')),

        # Línea horizontal DEBAJO de la ÚLTIMA fila (fila -1)
        ('LINEBELOW', (0, -1), (-1, -1), 1.0, colors.HexColor('#a0a0a0')),
        
        # Fila sombreada suave en 'Centro' (ahora es el índice 2)
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#f6f6f6')),
    ]
    tabla.setStyle(TableStyle(estilos))


    story.append(tabla)
    
 
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>Distribución de Magnitudes</b>", estilo_subtitulo))
    story.append(Spacer(1, 20))
    img_mag = RLImage(figuras["ruta_hist_mag"] ,width=14.5 * cm, height=8.0 * cm)
    story.append(img_mag)
    story.append(Paragraph("<b>Ilustración 1.</b> Distribución de magnitudes.", estilo_pie_fig))
    
    # ==================== PÁGINA 2 ====================
    story.append(PageBreak())

    story.append(Paragraph("<b>Número de sismos por día</b>", estilo_subtitulo))
    story.append(Spacer(1, 6))

    # Gráficos paralelos Matplotlib
    img_diario = RLImage(figuras["ruta_hist_diario"],width=14 * cm, height=8 * cm)
    
    #tabla_graficos = Table([[img_diario, img_mag]], colWidths=[8.5 * cm, 8.5 * cm])
    #tabla_graficos.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(Spacer(1, 20))
    story.append(img_diario)
    story.append(Paragraph("<b>Ilustración 2.</b> Número de sismos por día.", estilo_pie_fig))
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>Mapa de epicentros</b>", estilo_subtitulo))
    # Mapa PyGMT

    story.append(Spacer(1, 20))
    if "ruta_mapa" in figuras and os.path.exists(figuras["ruta_mapa"]):
        with PILImage.open(figuras["ruta_mapa"]) as img:
            ancho_px, alto_px = img.size
        ancho=12
        story.append(RLImage(figuras["ruta_mapa"], width=12 * cm, height=alto_px/ancho_px*ancho * cm))
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Ilustración 3.</b> Ubicación epicentral de los sismos registrados por el SSAT.", estilo_pie_fig))
            


    # Compilar aplicando cintillos en cada hoja
    doc.build(story, onFirstPage=agregar_cintillos, onLaterPages=agregar_cintillos)
    print(f"Creado {pdf_salida}")
