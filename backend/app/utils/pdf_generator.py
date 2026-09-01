"""
Utilidades para generación de PDFs de colillas
"""
from reportlab.lib.pagesizes import letter, A6
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from io import BytesIO
import base64
from datetime import datetime
from typing import List, Optional
import base64
from app.models.colilla import Colilla


class GeneradorPDFColilla:
    """Generador de PDFs para colillas de confección"""
    
    ANCHO_PAGE = 3.5 * inch  # Ancho de colilla (ticket)
    ALTO_PAGE = 5.5 * inch   # Alto de colilla
    
    @staticmethod
    def generar_colilla_individual(
        colilla: Colilla,
        empresa_nombre: str = "Mi Empresa",
        firma_base64: Optional[str] = None
    ) -> bytes:
        """
        Genera un PDF para una colilla individual
        
        Args:
            colilla: Objeto Colilla de la BD
            empresa_nombre: Nombre de la empresa
            firma_base64: Firma en Base64 para incluir en el PDF
            
        Returns:
            bytes: Contenido del PDF
        """
        buffer = BytesIO()
        
        # Crear documento con tamaño de ticket (aproximadamente)
        doc = SimpleDocTemplate(
            buffer,
            pagesize=(3.5*inch, 5.5*inch),
            rightMargin=0.2*inch,
            leftMargin=0.2*inch,
            topMargin=0.2*inch,
            bottomMargin=0.2*inch
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        titulo_style = ParagraphStyle(
            'titulo',
            parent=styles['Heading1'],
            fontSize=10,
            textColor=colors.HexColor('#000000'),
            spaceAfter=6,
            alignment=1  # Centrado
        )
        
        encabezado_style = ParagraphStyle(
            'encabezado',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.black,
            spaceAfter=2,
        )
        
        valor_style = ParagraphStyle(
            'valor',
            parent=styles['Normal'],
            fontSize=6,
            textColor=colors.black,
        )
        
        # Contenido del documento
        elements = []
        
        # Encabezado
        elements.append(Paragraph(empresa_nombre, titulo_style))
        elements.append(Paragraph("COLILLA DE CONFECCIÓN", titulo_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Información de colilla
        datos = [
            ["Colilla Nº:", f"<b>{colilla.numero_colilla}</b>"],
            ["Fecha:", f"{colilla.fecha_creacion.strftime('%d/%m/%Y')}"],
            ["Taller:", colilla.taller.nombre if colilla.taller else "N/A"],
        ]
        
        table = Table(datos, colWidths=[1.2*inch, 1.8*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Datos del confeccionista
        elements.append(Paragraph("<b>CONFECCIONISTA</b>", encabezado_style))
        conf_data = [
            ["Nombre:", f"<b>{colilla.confeccionista_nombre}</b>"],
            ["Cédula:", colilla.confeccionista_cedula or "---"],
        ]
        
        table2 = Table(conf_data, colWidths=[1.2*inch, 1.8*inch])
        table2.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table2)
        elements.append(Spacer(1, 0.08*inch))
        
        # Detalles del trabajo
        elements.append(Paragraph("<b>DETALLES DEL TRABAJO</b>", encabezado_style))
        detalle_data = [
            ["Tipo:", colilla.tipo_trabajo.value if colilla.tipo_trabajo else "---"],
            ["Referencia:", colilla.referencia or "---"],
            ["Color:", colilla.color or "---"],
            ["Talla:", colilla.talla_id or "---"],
        ]
        
        table3 = Table(detalle_data, colWidths=[1.2*inch, 1.8*inch])
        table3.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table3)
        elements.append(Spacer(1, 0.08*inch))
        
        # Cantidades
        elements.append(Paragraph("<b>CANTIDADES</b>", encabezado_style))
        cant_data = [
            ["A Confeccionar:", f"<b>{colilla.cantidad_prendas}</b>"],
            ["Completadas:", f"{colilla.cantidad_completada}"],
            ["Rechazadas:", f"{colilla.cantidad_rechazada}"],
        ]
        
        table4 = Table(cant_data, colWidths=[1.2*inch, 1.8*inch])
        table4.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#CCCCCC')),
        ]))
        elements.append(table4)
        elements.append(Spacer(1, 0.08*inch))
        
        # Fecha límite
        if colilla.fecha_limite_entrega:
            elements.append(Paragraph(
                f"<b>Fecha Límite: {colilla.fecha_limite_entrega.strftime('%d/%m/%Y')}</b>",
                encabezado_style
            ))
        
        # Estado
        estado_texto = f"<b>Estado: {colilla.estado.value.upper()}</b>"
        elements.append(Paragraph(estado_texto, encabezado_style))
        
        if colilla.observaciones:
            elements.append(Spacer(1, 0.05*inch))
            elements.append(Paragraph("<b>OBSERVACIONES:</b>", encabezado_style))
            elements.append(Paragraph(colilla.observaciones, valor_style))
        
        # Firma
        elements.append(Spacer(1, 0.1*inch))
        # Si la colilla tiene una firma en base64, incrustarla como imagen
        firma_b64 = getattr(colilla, 'firma_base64', None)
        if firma_b64:
            try:
                firma_bytes = base64.b64decode(firma_b64.split(',')[-1])
                img_buf = BytesIO(firma_bytes)
                # Ajustar tamaño de la firma (ancho máximo)
                img = Image(img_buf, width=1.6*inch, height=0.6*inch)
                elements.append(img)
            except Exception:
                elements.append(Paragraph("_" * 30, valor_style))
        else:
            elements.append(Paragraph("_" * 30, valor_style))

        elements.append(Paragraph("Firma del Confeccionista", valor_style))
        
        # Construir el documento
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def generar_colillas_por_confeccionista(
        colillas: List[Colilla],
        empresa_nombre: str = "Mi Empresa"
    ) -> bytes:
        """
        Genera un PDF con múltiples colillas
        """
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        styles = getSampleStyleSheet()
        titulo_style = ParagraphStyle(
            'titulo',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            alignment=1
        )
        
        subtitulo_style = ParagraphStyle(
            'subtitulo',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=8,
            spaceBefore=8,
        )
        
        # Contenido
        elements = []
        elements.append(Paragraph(empresa_nombre, titulo_style))
        elements.append(Paragraph("RESUMEN DE COLILLAS", titulo_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Agrupar por confeccionista
        colillas_por_conf = {}
        for col in colillas:
            if col.confeccionista_nombre not in colillas_por_conf:
                colillas_por_conf[col.confeccionista_nombre] = []
            colillas_por_conf[col.confeccionista_nombre].append(col)
        
        # Crear tabla con resumen
        resumen_data = [["Confeccionista", "Colillas", "Prendas", "Completadas", "Estado", "Firmadas"]]
        
        for conf_nombre, cols in colillas_por_conf.items():
            total_prendas = sum(c.cantidad_prendas for c in cols)
            total_completadas = sum(c.cantidad_completada for c in cols)
            estados = ", ".join(set(c.estado.value for c in cols))
            firmadas = f"{sum(1 for c in cols if getattr(c, 'firma_base64', None))}/{len(cols)}"
            
            resumen_data.append([
                conf_nombre,
                str(len(cols)),
                str(total_prendas),
                str(total_completadas),
                estados,
                firmadas
            ])
        
        resumen_table = Table(resumen_data, colWidths=[2.3*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.2*inch, 0.8*inch])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(resumen_table)
        
        # Construir
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
