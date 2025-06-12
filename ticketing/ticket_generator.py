from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


def generate_ticket_pdf(products, output_dir="tickets"):
    """Genera ticket en formato PDF profesional"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ticket_name = f"ticket_{timestamp}.pdf"
    ticket_path = os.path.join(output_dir, ticket_name)

    # Crear documento PDF
    doc = SimpleDocTemplate(ticket_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Estilo personalizado para el encabezado
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        textColor=colors.darkblue,
        spaceAfter=6
    )

    # Estilo para subtítulo
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=20
    )

    # Encabezado del ticket
    story.append(Paragraph("FASTSHOP MARKET", header_style))
    story.append(Paragraph("Sistema de Compra Automático", subtitle_style))

    # Información del ticket
    info_data = [
        ['Fecha:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
        ['Ticket N°:', timestamp],
        ['Cajero:', 'Sistema Automático']
    ]

    info_table = Table(info_data, colWidths=[1.5*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    story.append(info_table)
    story.append(Spacer(1, 20))

    # Tabla de productos
    data = [['Producto', 'Cant.', 'Precio Unit.', 'Subtotal']]

    total = 0
    for product in products:
        name = product["name"]
        price = product["price"]
        qty = product["qty"]
        subtotal = price * qty
        total += subtotal

        data.append([
            name,
            str(qty),
            f"${price:.2f}",
            f"${subtotal:.2f}"
        ])

    # Crear tabla de productos
    products_table = Table(
        data, colWidths=[3*inch, 0.8*inch, 1.2*inch, 1.2*inch])
    products_table.setStyle(TableStyle([
        # Encabezado
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

        # Contenido
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),

        # Bordes
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # Alternar colores de filas
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))

    story.append(products_table)
    story.append(Spacer(1, 20))

    # Total
    total_data = [['TOTAL A PAGAR:', f'${total:.2f}']]
    total_table = Table(total_data, colWidths=[4.5*inch, 1.7*inch])
    total_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
        ('BOX', (0, 0), (-1, -1), 2, colors.darkblue),
    ]))

    story.append(total_table)
    story.append(Spacer(1, 30))

    # Pie de página
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey
    )

    story.append(Paragraph("¡Gracias por su compra!", footer_style))
    story.append(
        Paragraph("FastShop - Tecnología al servicio del cliente", footer_style))

    # Generar PDF
    doc.build(story)

    print(f"📄 Ticket PDF generado: {ticket_path}")
    return ticket_path


def generate_ticket(products, output_dir="tickets", format_type="both"):
    """
    Genera ticket en el formato especificado

    Args:
        products: Lista de productos
        output_dir: Directorio de salida
        format_type: "txt", "pdf", o "both"

    Returns:
        dict con las rutas de los archivos generados
    """
    results = {}

    if format_type in ["txt", "both"]:
        txt_path = generate_ticket_txt(products, output_dir)
        results["txt"] = txt_path
        print(f"📄 Ticket TXT generado: {txt_path}")

    if format_type in ["pdf", "both"]:
        try:
            pdf_path = generate_ticket_pdf(products, output_dir)
            results["pdf"] = pdf_path
            print(f"📄 Ticket PDF generado: {pdf_path}")
        except ImportError:
            print("⚠️  ReportLab no está instalado. Solo se generó el ticket en texto.")
            print("   Para instalar: pip install reportlab")

    return results
