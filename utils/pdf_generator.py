import io
import base64
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle

def generate_in_game_decision_pdf(title, content, figures=None, metadata=None):
    """
    Generate a PDF report for in-game decision analysis
    
    Parameters:
    -----------
    title : str
        Title of the report
    content : str
        Markdown content for the report
    figures : list, optional
        List of plotly figures to include in the report
    metadata : dict, optional
        Dictionary of metadata to include in the report
    
    Returns:
    --------
    bytes
        PDF file as bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Add title
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Add metadata if provided
    if metadata:
        data = [[k, v] for k, v in metadata.items()]
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))
    
    # Add content
    for line in content.split('\n'):
        if line.startswith('# '):
            elements.append(Paragraph(line[2:], styles['Heading1']))
        elif line.startswith('## '):
            elements.append(Paragraph(line[3:], styles['Heading2']))
        elif line.startswith('### '):
            elements.append(Paragraph(line[4:], styles['Heading3']))
        elif line.startswith('- '):
            elements.append(Paragraph('• ' + line[2:], styles['Normal']))
        elif line.startswith('|'):
            # Skip table headers for now - would need more complex parsing
            pass
        elif line.strip() == '':
            elements.append(Spacer(1, 12))
        else:
            elements.append(Paragraph(line, styles['Normal']))
    
    # Add figures if provided
    if figures:
        for i, fig in enumerate(figures):
            # Convert plotly figure to image
            img_bytes = fig.to_image(format="png")
            img = Image(io.BytesIO(img_bytes))
            img.drawHeight = 300
            img.drawWidth = 500
            elements.append(img)
            elements.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

def generate_opposition_analysis_pdf(title, content, figures=None, metadata=None):
    """
    Generate a PDF report for opposition analysis
    
    Parameters:
    -----------
    title : str
        Title of the report
    content : str
        Markdown content for the report
    figures : list, optional
        List of plotly figures to include in the report
    metadata : dict, optional
        Dictionary of metadata to include in the report
    
    Returns:
    --------
    bytes
        PDF file as bytes
    """
    # Reuse the in-game decision PDF generator
    return generate_in_game_decision_pdf(title, content, figures, metadata)

def generate_team_coordination_pdf(title, content, figures=None, metadata=None):
    """
    Generate a PDF report for team coordination analysis
    
    Parameters:
    -----------
    title : str
        Title of the report
    content : str
        Markdown content for the report
    figures : list, optional
        List of plotly figures to include in the report
    metadata : dict, optional
        Dictionary of metadata to include in the report
    
    Returns:
    --------
    bytes
        PDF file as bytes
    """
    # Reuse the in-game decision PDF generator
    return generate_in_game_decision_pdf(title, content, figures, metadata)

def generate_training_development_pdf(title, content, figures=None, metadata=None):
    """
    Generate a PDF report for training development
    
    Parameters:
    -----------
    title : str
        Title of the report
    content : str
        Markdown content for the report
    figures : list, optional
        List of plotly figures to include in the report
    metadata : dict, optional
        Dictionary of metadata to include in the report
    
    Returns:
    --------
    bytes
        PDF file as bytes
    """
    # Reuse the in-game decision PDF generator
    return generate_in_game_decision_pdf(title, content, figures, metadata)

def generate_goalkeeper_scouting_pdf(title, content, figures=None, metadata=None):
    """
    Generate a PDF report for goalkeeper scouting
    
    Parameters:
    -----------
    title : str
        Title of the report
    content : str
        Markdown content for the report
    figures : list, optional
        List of plotly figures to include in the report
    metadata : dict, optional
        Dictionary of metadata to include in the report
    
    Returns:
    --------
    bytes
        PDF file as bytes
    """
    # Reuse the in-game decision PDF generator
    return generate_in_game_decision_pdf(title, content, figures, metadata)
