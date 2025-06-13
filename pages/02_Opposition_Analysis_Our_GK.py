import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.data_loader import StatsBombDataLoader
from utils.visualizations import create_pitch, plot_goalkeeper_distribution

st.set_page_config(
    page_title="Opposition Analysis - Our GK",
    page_icon="🧤",
    layout="wide"
)

# Load data
def load_data():
    data_loader = StatsBombDataLoader()
    return data_loader

data_loader = load_data()

# Page title
st.title("Opposition Analysis - Our GK")
st.markdown("Pre-match distribution planning based on opposition pressing patterns")

# Match selection
st.header("Match Selection")

col1, col2 = st.columns(2)

with col1:
    team = st.selectbox("Our Team", ["Real Madrid", "Barcelona", "Atlético Madrid", "Valencia"])
    goalkeeper = st.selectbox("Our Goalkeeper", ["Keylor Navas", "Marc-André ter Stegen", "Jan Oblak", "Jasper Cillessen"])
    
with col2:
    opposition = st.selectbox("Opposition Team", ["Atlético Madrid", "Barcelona", "Real Madrid", "Sevilla"])
    competition = st.selectbox("Competition", ["La Liga", "Champions League", "Copa del Rey"])

# Opposition pressing analysis
st.header("Opposition Pressing Analysis")

# Sample data for demonstration
pressing_patterns = {
    "High Press Frequency": 8,
    "Press Intensity": 7,
    "Pressing Triggers": ["Goalkeeper Receives Ball", "Back Pass to Goalkeeper", "Short Distribution"],
    "Press Structure": "3-2-5",
    "Pressing Traps": ["Force to Flanks", "Block Central Progression"]
}

col1, col2 = st.columns(2)

with col1:
    st.subheader("Pressing Metrics")
    st.metric("High Press Frequency", f"{pressing_patterns['High Press Frequency']}/10")
    st.metric("Press Intensity", f"{pressing_patterns['Press Intensity']}/10")
    
    st.subheader("Pressing Triggers")
    for trigger in pressing_patterns["Pressing Triggers"]:
        st.markdown(f"- {trigger}")
    
    st.subheader("Press Structure")
    st.markdown(f"**Formation:** {pressing_patterns['Press Structure']}")
    
    st.subheader("Pressing Traps")
    for trap in pressing_patterns["Pressing Traps"]:
        st.markdown(f"- {trap}")

with col2:
    st.subheader("Opposition Pressing Pattern")
    
    # Create pitch visualization
    fig = create_pitch(width=600, height=400)
    
    # Sample positions for visualization
    positions = {
        "GK": [10, 50],
        "RCB": [20, 30],
        "LCB": [20, 70],
        "RB": [30, 10],
        "LB": [30, 90],
        "CDM": [40, 50],
        "RM": [60, 20],
        "LM": [60, 80],
        "CAM": [70, 50],
        "ST": [85, 50]
    }
    
    # Opposition positions
    opp_positions = {
        "ST": [25, 50],
        "RW": [35, 30],
        "LW": [35, 70],
        "CM1": [45, 40],
        "CM2": [45, 60],
        "RB": [55, 20],
        "LB": [55, 80],
        "CB1": [65, 40],
        "CB2": [65, 60],
        "GK": [85, 50]
    }
    
    # Add our team
    for position, (x, y) in positions.items():
        if position == "GK":
            fig.add_trace(go.Scatter(
                x=[x],
                y=[y],
                mode='markers',
                marker=dict(size=15, color='cyan'),
                name='Our Goalkeeper'
            ))
        else:
            fig.add_trace(go.Scatter(
                x=[x],
                y=[y],
                mode='markers',
                marker=dict(size=12, color='blue'),
                name=position
            ))
    
    # Add opposition team
    for position, (x, y) in opp_positions.items():
        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers',
            marker=dict(size=12, color='red'),
            name=f"Opp {position}"
        ))
    
    # Add pressing lines
    for opp_pos, (ox, oy) in {"ST": opp_positions["ST"], "RW": opp_positions["RW"], "LW": opp_positions["LW"]}.items():
        # Draw pressing lines from opposition forwards to our defenders
        for our_pos, (dx, dy) in {"GK": positions["GK"], "RCB": positions["RCB"], "LCB": positions["LCB"]}.items():
            if (opp_pos == "ST" and our_pos == "GK") or \
               (opp_pos == "RW" and our_pos == "RCB") or \
               (opp_pos == "LW" and our_pos == "LCB"):
                fig.add_trace(go.Scatter(
                    x=[ox, dx],
                    y=[oy, dy],
                    mode='lines',
                    line=dict(width=2, color='rgba(255, 0, 0, 0.5)', dash='dash'),
                    name=f"Press from {opp_pos}"
                ))
    
    st.plotly_chart(fig, use_container_width=True)

# Distribution recommendations
st.header("Distribution Recommendations")

# Sample data for demonstration
distribution_options = {
    "Short Pass to Right Center Back": {
        "success_rate": 0.65,
        "recommendation": "Avoid - High Risk",
        "explanation": "Opposition right winger presses aggressively, cutting passing lane to RCB"
    },
    "Short Pass to Left Center Back": {
        "success_rate": 0.75,
        "recommendation": "Consider - Medium Risk",
        "explanation": "Opposition left winger less aggressive in pressing, but still applies pressure"
    },
    "Medium Pass to Defensive Midfielder": {
        "success_rate": 0.45,
        "recommendation": "Avoid - High Risk",
        "explanation": "Opposition striker and midfielders block central progression effectively"
    },
    "Long Pass to Right Winger": {
        "success_rate": 0.60,
        "recommendation": "Recommended - Medium Risk",
        "explanation": "Opposition left back often pushes high, creating space behind"
    },
    "Long Pass to Striker": {
        "success_rate": 0.55,
        "recommendation": "Consider - Medium Risk",
        "explanation": "Can bypass opposition press entirely, but lower completion percentage"
    }
}

# Display distribution options
st.subheader("Distribution Options Analysis")

for option, details in distribution_options.items():
    col1, col2, col3 = st.columns([2, 1, 3])
    
    with col1:
        st.markdown(f"**{option}**")
    
    with col2:
        if "Avoid" in details["recommendation"]:
            color = "red"
        elif "Consider" in details["recommendation"]:
            color = "orange"
        else:
            color = "green"
        
        st.markdown(f"<span style='color:{color};'>{details['recommendation']}</span>", unsafe_allow_html=True)
    
    with col3:
        st.markdown(details["explanation"])
    
    st.markdown("---")

# Visualization of recommended distribution
st.subheader("Recommended Distribution Pattern")

# Create pitch visualization
fig = create_pitch(width=600, height=400)

# Add our team
for position, (x, y) in positions.items():
    if position == "GK":
        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers',
            marker=dict(size=15, color='cyan'),
            name='Our Goalkeeper'
        ))
    else:
        fig.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers',
            marker=dict(size=12, color='blue'),
            name=position
        ))

# Add distribution lines
distribution_targets = {
    "Long Pass to Right Winger": ("GK", "RM", 0.60, "green"),
    "Long Pass to Striker": ("GK", "ST", 0.55, "orange"),
    "Short Pass to Left Center Back": ("GK", "LCB", 0.75, "orange")
}

for option, (start, end, weight, color) in distribution_targets.items():
    fig.add_trace(go.Scatter(
        x=[positions[start][0], positions[end][0]],
        y=[positions[start][1], positions[end][1]],
        mode='lines',
        line=dict(width=weight*5, color=color),
        name=option
    ))

st.plotly_chart(fig, use_container_width=True)

# Case study
st.header("Case Study: Keylor Navas Preparing for Atlético Madrid")

st.markdown("""
This case study demonstrates how Real Madrid's coaching staff used xT-GK analysis to prepare Keylor Navas for optimal distribution against Atlético Madrid's aggressive pressing system. By combining data analysis with practical coaching, the team developed a targeted distribution strategy that maximized possession retention while creating progressive opportunities.
""")

# Key findings
st.subheader("Key Findings")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Pre-Match Analysis:**
    - Atlético's pressing triggers identified: back passes to goalkeeper and short distribution attempts
    - Press intensity highest in central areas
    - Numerical advantage on right flank when bypassing first line of press
    """)

with col2:
    st.markdown("""
    **Match Implementation:**
    - 68% success rate on distribution (15% above season average)
    - 8 progressive passes leading to attacking opportunities
    - Effectively bypassed Atlético's first line of press in 75% of distributions
    """)

# Download report
st.header("Generate Report")

if st.button("Generate PDF Report"):
    st.success("Report generated! Click below to download.")
    
    # Provide download link (this would normally generate a real PDF)
    st.download_button(
        label="Download Opposition Analysis Report",
        data=b"Sample PDF content",  # This would be actual PDF data
        file_name="opposition_analysis_report.pdf",
        mime="application/pdf"
    )
