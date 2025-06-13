import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.data_loader import StatsBombDataLoader
from utils.visualizations import create_pitch, plot_goalkeeper_distribution

st.set_page_config(
    page_title="xT-GK: Expected Threat for Goalkeepers",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
def load_data():
    data_loader = StatsBombDataLoader()
    return data_loader

data_loader = load_data()

# Main page
st.title("xT-GK: Expected Threat for Goalkeepers")
st.markdown("""
This application provides analysis of goalkeeper distribution using the Expected Threat (xT) framework.
Navigate through the pages in the sidebar to explore different aspects of goalkeeper analysis.
""")

# Overview section
st.header("Overview")
st.markdown("""
The xT-GK application helps coaches, analysts, and players make data-driven decisions about goalkeeper distribution patterns.
It provides insights into:

- In-game decision making
- Opposition analysis
- Team coordination
- Training development
- Goalkeeper scouting

Select a page from the sidebar to begin your analysis.
""")

# Sample visualization
st.header("Sample Visualization")
with st.container():
    st.markdown("Below is a sample visualization of goalkeeper distribution patterns:")
    fig = create_pitch(width=700, height=500)
    # Add sample data points
    sample_positions = {
        "GK": [50, 10],
        "RCB": [30, 30],
        "LCB": [30, 70],
        "RB": [40, 15],
        "LB": [40, 85],
        "CDM": [60, 50],
        "RCM": [70, 30],
        "LCM": [70, 70],
        "RW": [80, 20],
        "LW": [80, 80],
        "ST": [85, 50]
    }
    
    # Add sample connections
    connections = [
        ("GK", "RCB", 0.8),
        ("GK", "LCB", 0.7),
        ("GK", "CDM", 0.4),
        ("GK", "RB", 0.3),
        ("GK", "LB", 0.3)
    ]
    
    # Plot connections
    for start, end, width in connections:
        fig.add_trace(go.Scatter(
            x=[sample_positions[start][0], sample_positions[end][0]],
            y=[sample_positions[start][1], sample_positions[end][1]],
            mode='lines',
            line=dict(width=width*5, color='rgba(255, 255, 255, 0.7)'),
            hoverinfo='none',
            showlegend=False
        ))
    
    # Plot positions
    for position, (x, y) in sample_positions.items():
        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers',
            marker=dict(size=12, color='blue' if position != "GK" else 'cyan'),
            name=position,
            hoverinfo='text',
            hovertext=position
        ))
    
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("© 2025 xT-GK Analysis Tool")
