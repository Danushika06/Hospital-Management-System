from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os

def generate_prescription_pdf(prescription):
    """Generate a PDF prescription using ReportLab"""
    
    # Create prescriptions directory if it doesn't exist
    os.makedirs('static/prescriptions', exist_ok=True)
    
    # Generate filename
    filename = f'prescription_{prescription.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    filepath = os.path.join('static', 'prescriptions', filename)
    
    # Create the PDF document
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#4b5563'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6
    )
    
    # Hospital Header
    elements.append(Paragraph("City General Hospital", title_style))
    elements.append(Paragraph("123 Medical Center Drive, Healthcare City", subtitle_style))
    elements.append(Paragraph("Phone: +1 (555) 123-4567", subtitle_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Prescription Title
    elements.append(Paragraph("PRESCRIPTION", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Prescription Details
    prescription_data = [
        ['Prescription ID:', str(prescription.id)],
        ['Date:', prescription.created_at.strftime('%Y-%m-%d')],
        ['', '']
    ]
    
    prescription_table = Table(prescription_data, colWidths=[2*inch, 4*inch])
    prescription_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(prescription_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Doctor Information
    elements.append(Paragraph("Doctor Information", heading_style))
    doctor_data = [
        ['Name:', f'Dr. {prescription.doctor.username}'],
        ['Email:', prescription.doctor.email]
    ]
    
    doctor_table = Table(doctor_data, colWidths=[2*inch, 4*inch])
    doctor_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(doctor_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Patient Information
    elements.append(Paragraph("Patient Information", heading_style))
    patient_data = [
        ['Name:', prescription.patient.username],
        ['Email:', prescription.patient.email],
        ['Patient ID:', str(prescription.patient.id)]
    ]
    
    patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Diagnosis
    elements.append(Paragraph("Diagnosis", heading_style))
    elements.append(Paragraph(prescription.diagnosis, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Medicines
    elements.append(Paragraph("Prescribed Medicines", heading_style))
    
    # Parse medicine details
    medicine_lines = prescription.medicine_details.split('\n')
    medicine_table_data = [['#', 'Medicine', 'Instructions']]
    
    for i, medicine in enumerate(medicine_lines, 1):
        if medicine.strip():
            # Split by common delimiters
            parts = medicine.strip().split('-', 1)
            if len(parts) == 2:
                medicine_table_data.append([str(i), parts[0].strip(), parts[1].strip()])
            else:
                medicine_table_data.append([str(i), medicine.strip(), 'As directed'])
    
    medicine_table = Table(medicine_table_data, colWidths=[0.5*inch, 2.5*inch, 3*inch])
    medicine_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    elements.append(medicine_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Signature Section
    elements.append(Spacer(1, 0.3*inch))
    signature_style = ParagraphStyle(
        'Signature',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_RIGHT
    )
    elements.append(Paragraph('_________________________', signature_style))
    elements.append(Paragraph(f'Dr. {prescription.doctor.username}', signature_style))
    elements.append(Paragraph('Digital Signature', signature_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph('This is a digitally generated prescription.', footer_style))
    elements.append(Paragraph('For any queries, please contact City General Hospital.', footer_style))
    
    # Build PDF
    doc.build(elements)
    
    return filepath
