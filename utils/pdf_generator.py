import io
import base64
import pandas as pd
import matplotlib.pyplot as plt
from weasyprint import HTML, CSS
from jinja2 import Template
import plotly.io as pio
import plotly.graph_objects as go
from datetime import datetime

def generate_pdf_report(title, content, figures=None, tables=None, metadata=None):
    """
    Generate a PDF report using WeasyPrint with proper styling and layout.
    
    Parameters:
    -----------
    title : str
        The title of the report
    content : dict
        Dictionary containing sections of content with keys as section titles
        and values as section content (can include HTML)
    figures : list, optional
        List of dictionaries with figure data, each containing:
        - 'figure': Plotly figure object
        - 'caption': Figure caption
    tables : list, optional
        List of dictionaries with table data, each containing:
        - 'data': Pandas DataFrame
        - 'caption': Table caption
    metadata : dict, optional
        Dictionary containing metadata like author, date, etc.
        
    Returns:
    --------
    bytes
        PDF file as bytes
    """
    if metadata is None:
        metadata = {}
    
    # Set default metadata
    if 'author' not in metadata:
        metadata['author'] = 'xT-GK Analyzer'
    if 'date' not in metadata:
        metadata['date'] = datetime.now().strftime('%Y-%m-%d')
    
    # Convert Plotly figures to base64 encoded images
    figure_images = []
    if figures:
        for i, fig_data in enumerate(figures):
            if 'figure' in fig_data:
                fig = fig_data['figure']
                img_bytes = pio.to_image(fig, format='png', width=800, height=500, scale=2)
                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                figure_images.append({
                    'image': f"data:image/png;base64,{img_base64}",
                    'caption': fig_data.get('caption', f'Figure {i+1}')
                })
    
    # Convert Pandas tables to HTML
    table_htmls = []
    if tables:
        for i, table_data in enumerate(tables):
            if 'data' in table_data:
                df = table_data['data']
                table_html = df.to_html(classes='data-table', index=False)
                table_htmls.append({
                    'html': table_html,
                    'caption': table_data.get('caption', f'Table {i+1}')
                })
    
    # HTML template for the report
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{{ title }}</title>
        <style>
            @page {
                size: A4;
                margin: 2.5cm 1.5cm;
                @top-center {
                    content: "xT-GK Analysis";
                    font-size: 10pt;
                    color: #666;
                }
                @bottom-center {
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 10pt;
                    color: #666;
                }
            }
            body {
                font-family: 'Helvetica', 'Arial', sans-serif;
                font-size: 11pt;
                line-height: 1.4;
                color: #333;
            }
            h1 {
                font-size: 24pt;
                color: #1a5276;
                margin-bottom: 0.5cm;
                text-align: center;
                page-break-after: avoid;
            }
            h2 {
                font-size: 16pt;
                color: #2874a6;
                margin-top: 1cm;
                margin-bottom: 0.3cm;
                page-break-after: avoid;
            }
            h3 {
                font-size: 14pt;
                color: #3498db;
                margin-top: 0.8cm;
                margin-bottom: 0.2cm;
                page-break-after: avoid;
            }
            p {
                margin-bottom: 0.3cm;
                text-align: justify;
            }
            .metadata {
                margin-bottom: 1cm;
                text-align: center;
                font-size: 10pt;
                color: #666;
            }
            .figure-container {
                margin: 1cm 0;
                text-align: center;
                page-break-inside: avoid;
            }
            .figure-container img {
                max-width: 100%;
                height: auto;
            }
            .figure-caption {
                font-style: italic;
                font-size: 10pt;
                color: #666;
                margin-top: 0.2cm;
                text-align: center;
            }
            .table-container {
                margin: 1cm 0;
                page-break-inside: avoid;
            }
            .table-caption {
                font-style: italic;
                font-size: 10pt;
                color: #666;
                margin-bottom: 0.2cm;
            }
            .data-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 9pt;
            }
            .data-table th {
                background-color: #f2f2f2;
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            .data-table td {
                border: 1px solid #ddd;
                padding: 6px;
            }
            .data-table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .footer {
                margin-top: 1.5cm;
                text-align: center;
                font-size: 9pt;
                color: #666;
                border-top: 1px solid #ddd;
                padding-top: 0.3cm;
            }
            .page-break {
                page-break-before: always;
            }
        </style>
    </head>
    <body>
        <h1>{{ title }}</h1>
        
        <div class="metadata">
            <p>
                {% if metadata.author %}Author: {{ metadata.author }}{% endif %}
                {% if metadata.date %} | Date: {{ metadata.date }}{% endif %}
                {% if metadata.team %} | Team: {{ metadata.team }}{% endif %}
            </p>
        </div>
        
        {% for section_title, section_content in content.items() %}
            <h2>{{ section_title }}</h2>
            {{ section_content|safe }}
        {% endfor %}
        
        {% if figure_images %}
            <h2>Visualizations</h2>
            {% for figure in figure_images %}
                <div class="figure-container">
                    <img src="{{ figure.image }}" alt="{{ figure.caption }}">
                    <div class="figure-caption">{{ figure.caption }}</div>
                </div>
            {% endfor %}
        {% endif %}
        
        {% if table_htmls %}
            <h2>Data Tables</h2>
            {% for table in table_htmls %}
                <div class="table-container">
                    <div class="table-caption">{{ table.caption }}</div>
                    {{ table.html|safe }}
                </div>
            {% endfor %}
        {% endif %}
        
        <div class="footer">
            <p>Generated by xT-GK Analyzer | Jeffrey Eyestone | j@eyestone.us | +1 (720) 625-2425</p>
        </div>
    </body>
    </html>
    """
    
    # Render the template
    template = Template(html_template)
    html_content = template.render(
        title=title,
        content=content,
        figure_images=figure_images,
        table_htmls=table_htmls,
        metadata=metadata
    )
    
    # Generate PDF
    pdf_bytes = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_bytes)
    pdf_bytes.seek(0)
    
    return pdf_bytes.getvalue()

def generate_in_game_decision_pdf(gk_name, team_name, match_situation, pressure_level, 
                                  distribution_options, recommendation, pitch_fig=None):
    """Generate PDF for In-Game Decision template"""
    
    title = f"In-Game Decision Analysis: {gk_name}"
    
    content = {
        "Match Situation": f"""
            <p>Goalkeeper: <strong>{gk_name}</strong></p>
            <p>Team: <strong>{team_name}</strong></p>
            <p>Match Situation: <strong>{match_situation}</strong></p>
            <p>Pressure Level: <strong>{pressure_level}/10</strong></p>
        """,
        
        "Distribution Options": f"""
            <p>The following distribution options were analyzed:</p>
            <ul>
                {"".join([f"<li><strong>{option}</strong></li>" for option in distribution_options])}
            </ul>
        """,
        
        "Recommendation": f"""
            <p>{recommendation}</p>
        """
    }
    
    figures = []
    if pitch_fig:
        figures.append({
            'figure': pitch_fig,
            'caption': f'Distribution Options for {gk_name} under {pressure_level}/10 Pressure'
        })
    
    metadata = {
        'author': 'xT-GK Analyzer',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'team': team_name
    }
    
    return generate_pdf_report(title, content, figures, metadata=metadata)

def generate_opposition_analysis_pdf(gk_name, team_name, opposition_team, 
                                    analysis_type, key_findings, pitch_fig=None):
    """Generate PDF for Opposition Analysis template"""
    
    if analysis_type == "our_gk":
        title = f"Opposition Analysis: Preparing {gk_name} for {opposition_team}"
        subtitle = f"Analysis of how {team_name}'s goalkeeper should distribute against {opposition_team}"
    else:
        title = f"Opposition Analysis: Exploiting {gk_name} of {opposition_team}"
        subtitle = f"Analysis of how to exploit {opposition_team}'s goalkeeper distribution"
    
    content = {
        "Overview": f"""
            <p>{subtitle}</p>
            <p>Goalkeeper: <strong>{gk_name}</strong></p>
            <p>Team: <strong>{team_name}</strong></p>
            <p>Opposition: <strong>{opposition_team}</strong></p>
        """,
        
        "Key Findings": f"""
            <ul>
                {"".join([f"<li>{finding}</li>" for finding in key_findings])}
            </ul>
        """
    }
    
    figures = []
    if pitch_fig:
        if analysis_type == "our_gk":
            caption = f'Distribution Recommendations for {gk_name} against {opposition_team}'
        else:
            caption = f'Exploitation Opportunities against {gk_name} of {opposition_team}'
        
        figures.append({
            'figure': pitch_fig,
            'caption': caption
        })
    
    metadata = {
        'author': 'xT-GK Analyzer',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'team': team_name
    }
    
    return generate_pdf_report(title, content, figures, metadata=metadata)

def generate_team_coordination_pdf(gk_name, team_name, formation, build_up_pattern,
                                  movement_patterns, recommendations, coord_fig=None):
    """Generate PDF for Team Coordination template"""
    
    title = f"Team Coordination Analysis: {team_name}"
    
    content = {
        "Overview": f"""
            <p>Goalkeeper: <strong>{gk_name}</strong></p>
            <p>Team: <strong>{team_name}</strong></p>
            <p>Formation: <strong>{formation}</strong></p>
            <p>Primary Build-up Pattern: <strong>{build_up_pattern}</strong></p>
        """,
        
        "Key Movement Patterns": f"""
            <ol>
                {"".join([f"<li>{pattern}</li>" for pattern in movement_patterns])}
            </ol>
        """,
        
        "Coordination Recommendations": f"""
            <ol>
                {"".join([f"<li>{rec}</li>" for rec in recommendations])}
            </ol>
        """
    }
    
    figures = []
    if coord_fig:
        figures.append({
            'figure': coord_fig,
            'caption': f'Team Coordination Diagram for {team_name} ({formation})'
        })
    
    metadata = {
        'author': 'xT-GK Analyzer',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'team': team_name
    }
    
    return generate_pdf_report(title, content, figures, metadata=metadata)

def generate_training_development_pdf(gk_name, team_name, primary_focus, secondary_focus,
                                     training_phase, recommendations, pitch_fig=None, radar_fig=None):
    """Generate PDF for Training Development template"""
    
    title = f"Training Development Program: {gk_name}"
    
    content = {
        "Overview": f"""
            <p>Goalkeeper: <strong>{gk_name}</strong></p>
            <p>Team: <strong>{team_name}</strong></p>
            <p>Primary Development Focus: <strong>{primary_focus}</strong></p>
            <p>Secondary Development Areas: <strong>{', '.join(secondary_focus)}</strong></p>
            <p>Training Phase: <strong>{training_phase}</strong></p>
        """,
        
        "Training Recommendations": f"""
            <ol>
                {"".join([f"<li>{rec}</li>" for rec in recommendations])}
            </ol>
        """
    }
    
    figures = []
    if radar_fig:
        figures.append({
            'figure': radar_fig,
            'caption': f'{gk_name} Distribution Profile vs. League Average'
        })
    
    if pitch_fig:
        figures.append({
            'figure': pitch_fig,
            'caption': f'Training Exercise Visualization for {primary_focus}'
        })
    
    metadata = {
        'author': 'xT-GK Analyzer',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'team': team_name
    }
    
    return generate_pdf_report(title, content, figures, metadata=metadata)

def generate_goalkeeper_scouting_pdf(gk_name, team_name, scouting_team, team_style,
                                    strengths, weaknesses, recommendation, radar_fig=None, pitch_fig=None):
    """Generate PDF for Goalkeeper Scouting template"""
    
    title = f"Goalkeeper Scouting Report: {gk_name}"
    
    content = {
        "Overview": f"""
            <p>Goalkeeper: <strong>{gk_name}</strong></p>
            <p>Current Team: <strong>{team_name}</strong></p>
            <p>Scouting Team: <strong>{scouting_team}</strong></p>
            <p>Team Playing Style: <strong>{team_style}</strong></p>
        """,
        
        "Strengths": f"""
            <ul>
                {"".join([f"<li>{strength}</li>" for strength in strengths])}
            </ul>
        """,
        
        "Areas for Development": f"""
            <ul>
                {"".join([f"<li>{weakness}</li>" for weakness in weaknesses])}
            </ul>
        """,
        
        "Recommendation": f"""
            <p>{recommendation}</p>
        """
    }
    
    figures = []
    if radar_fig:
        figures.append({
            'figure': radar_fig,
            'caption': f'{gk_name} Distribution Profile vs. {scouting_team} Requirements'
        })
    
    if pitch_fig:
        figures.append({
            'figure': pitch_fig,
            'caption': f'Distribution Pattern Analysis for {gk_name}'
        })
    
    metadata = {
        'author': 'xT-GK Analyzer',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'team': scouting_team
    }
    
    return generate_pdf_report(title, content, figures, metadata=metadata)
