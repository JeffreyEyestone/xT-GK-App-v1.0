import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.visualizations import create_pitch, create_radar_chart
from utils.data_loader import StatsBombDataLoader
from utils.pdf_generator import generate_goalkeeper_scouting_pdf

st.set_page_config(
    page_title="Goalkeeper Scouting | xT-GK",
    page_icon="⚽",
    layout="wide"
)

# Initialize data loader
@st.cache_resource
def load_data():
    data_loader = StatsBombDataLoader()
    return data_loader

data_loader = load_data()

# Get real data
real_data = data_loader.get_sample_data()
gk_data = real_data['goalkeeper_data']
pass_events = real_data['pass_events']
match_info = real_data['match_info']

st.title("Goalkeeper Scouting")
st.subheader("Evaluate goalkeeper distribution profiles for recruitment")

st.markdown("""
This template helps scouts and recruitment teams evaluate goalkeeper distribution profiles by:
- Analyzing distribution patterns and tendencies
- Comparing goalkeepers against specific requirements
- Evaluating fit with team tactical approach
- Identifying high-potential recruitment targets

Using real La Liga data, this tool provides evidence-based scouting insights for goalkeeper recruitment.
""")

# Create two columns for inputs and visualization
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Scouting Parameters")
    
    # Select teams from real data
    available_teams = []
    for match in match_info:
        if match['home_team'] not in available_teams:
            available_teams.append(match['home_team'])
        if match['away_team'] not in available_teams:
            available_teams.append(match['away_team'])
    
    if not available_teams:
        available_teams = ["Team A", "Team B", "Team C"]  # Fallback
    
    # Scouting team (your team)
    scouting_team = st.selectbox(
        "Scouting Team",
        options=available_teams,
        index=0
    )
    
    # Target goalkeepers to scout
    target_teams = st.multiselect(
        "Target Teams",
        options=available_teams,
        default=[available_teams[1] if len(available_teams) > 1 else available_teams[0]]
    )
    
    # Get goalkeepers from selected teams
    target_goalkeepers = []
    for gk in gk_data:
        if gk['team_name'] in target_teams:
            if gk['player_name'] not in target_goalkeepers:
                target_goalkeepers.append(gk['player_name'])
    
    if not target_goalkeepers:
        target_goalkeepers = ["Goalkeeper A", "Goalkeeper B", "Goalkeeper C"]  # Fallback
    
    selected_goalkeepers = st.multiselect(
        "Goalkeepers to Scout",
        options=target_goalkeepers,
        default=[target_goalkeepers[0]] if target_goalkeepers else []
    )
    
    # Scouting criteria
    st.subheader("Scouting Criteria")
    
    primary_criteria = st.selectbox(
        "Primary Distribution Criteria",
        options=["Short Distribution Accuracy", "Long Distribution Accuracy", "Distribution Under Pressure", "Distribution Speed", "Tactical Decision Making"],
        index=0
    )
    
    secondary_criteria = st.multiselect(
        "Secondary Distribution Criteria",
        options=["Short Distribution Accuracy", "Long Distribution Accuracy", "Distribution Under Pressure", "Distribution Speed", "Tactical Decision Making"],
        default=["Long Distribution Accuracy", "Tactical Decision Making"]
    )
    
    # Remove primary criteria from secondary if selected
    if primary_criteria in secondary_criteria:
        secondary_criteria.remove(primary_criteria)
    
    # Team tactical context
    st.subheader("Team Tactical Context")
    
    team_style = st.selectbox(
        "Team Playing Style",
        options=["Possession-Based", "Direct Play", "Counter-Attacking", "High Press", "Balanced"],
        index=0
    )
    
    build_up_preference = st.slider(
        "Build-up Preference",
        min_value=1,
        max_value=10,
        value=7,
        help="1 = Very Direct, 10 = Patient Build-up"
    )
    
    # Advanced options
    with st.expander("Advanced Scouting Options"):
        st.subheader("Detailed Scouting Settings")
        
        age_range = st.slider(
            "Age Range",
            min_value=18,
            max_value=40,
            value=(22, 32)
        )
        
        contract_status = st.multiselect(
            "Contract Status",
            options=["Expiring within 1 year", "Expiring within 2 years", "Long-term contract", "Free agent"],
            default=["Expiring within 1 year", "Expiring within 2 years"]
        )
        
        budget_constraint = st.checkbox("Apply Budget Constraint", value=False)
        
        if budget_constraint:
            max_budget = st.slider(
                "Maximum Transfer Budget (€M)",
                min_value=1,
                max_value=50,
                value=15
            )

with col2:
    st.subheader("Goalkeeper Scouting Analysis")
    
    if not selected_goalkeepers:
        st.warning("Please select at least one goalkeeper to scout.")
    else:
        # Create tabs for each selected goalkeeper
        if len(selected_goalkeepers) > 1:
            tabs = st.tabs(selected_goalkeepers)
        else:
            tabs = [st.container()]  # If only one goalkeeper, use a container instead of tabs
        
        # Store all radar and pitch figures for PDF export
        all_radar_figs = []
        all_pitch_figs = []
        all_strengths = []
        all_weaknesses = []
        all_recommendations = []
        
        for i, goalkeeper in enumerate(selected_goalkeepers):
            # Use the appropriate tab or container
            if len(selected_goalkeepers) > 1:
                tab = tabs[i]
            else:
                tab = tabs[0]
            
            with tab:
                # Display goalkeeper profile
                st.markdown(f"### {goalkeeper} Distribution Profile")
                
                # Create metrics display
                col1_metrics, col2_metrics, col3_metrics = st.columns(3)
                
                # Simulate goalkeeper stats based on selected goalkeeper
                # In a real app, this would use actual data from the database
                gk_success_rate = 0.75 if i == 0 else 0.68 + (i * 0.02)
                gk_short_pct = 0.70 if i == 0 else 0.60 + (i * 0.03)
                gk_long_pct = 0.30 if i == 0 else 0.40 - (i * 0.03)
                gk_pressure_pct = 0.35 if i == 0 else 0.45 - (i * 0.02)
                gk_total_passes = 32 if i == 0 else 25 + i
                
                with col1_metrics:
                    st.metric("Pass Success Rate", f"{gk_success_rate:.1%}")
                    st.metric("Short Pass %", f"{gk_short_pct:.1%}")
                
                with col2_metrics:
                    st.metric("Total Passes", f"{gk_total_passes}")
                    st.metric("Long Pass %", f"{gk_long_pct:.1%}")
                
                with col3_metrics:
                    st.metric("Under Pressure %", f"{gk_pressure_pct:.1%}")
                    
                    # Calculate estimated xT-GK value based on available metrics
                    estimated_xt_gk = (
                        gk_success_rate * 0.6 + 
                        (1 - gk_pressure_pct) * 0.4
                    )
                    st.metric("Est. xT-GK", f"{estimated_xt_gk:.2f}")
                
                # Distribution radar chart
                st.markdown("### Distribution Skill Profile")
                
                # Create radar chart data
                gk_data_dict = {
                    "Short Accuracy": 0.75 if i == 0 else 0.65 + (i * 0.02),
                    "Long Accuracy": 0.65 if i == 0 else 0.70 - (i * 0.02),
                    "Under Pressure": 0.70 if i == 0 else 0.60 + (i * 0.03),
                    "Speed of Release": 0.80 if i == 0 else 0.65 + (i * 0.04),
                    "Tactical Decisions": 0.75 if i == 0 else 0.70 - (i * 0.01)
                }
                
                # Team requirements based on team style
                if team_style == "Possession-Based":
                    team_requirements = {
                        "Short Accuracy": 0.80,
                        "Long Accuracy": 0.60,
                        "Under Pressure": 0.75,
                        "Speed of Release": 0.70,
                        "Tactical Decisions": 0.85
                    }
                elif team_style == "Direct Play":
                    team_requirements = {
                        "Short Accuracy": 0.65,
                        "Long Accuracy": 0.75,
                        "Under Pressure": 0.65,
                        "Speed of Release": 0.80,
                        "Tactical Decisions": 0.70
                    }
                else:  # Balanced or other styles
                    team_requirements = {
                        "Short Accuracy": 0.75,
                        "Long Accuracy": 0.70,
                        "Under Pressure": 0.70,
                        "Speed of Release": 0.75,
                        "Tactical Decisions": 0.75
                    }
                
                # Create radar chart
                radar_fig = create_radar_chart(gk_data_dict, team_requirements)
                
                # Update chart title and layout
                radar_fig.update_layout(
                    title=f"{goalkeeper} vs. {scouting_team} Requirements",
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )
                    ),
                    showlegend=True,
                    legend=dict(
                        title="Distribution Profile",
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                # Display the radar chart
                st.plotly_chart(radar_fig, use_container_width=True)
                all_radar_figs.append(radar_fig)
                
                # Distribution pattern visualization
                st.markdown("### Distribution Pattern Analysis")
                
                # Create pitch visualization
                pitch_fig = create_pitch()
                
                # Add goalkeeper position
                gk_pos = (5, 34)
                pitch_fig.add_trace(go.Scatter(
                    x=[gk_pos[0]],
                    y=[gk_pos[1]],
                    mode='markers+text',
                    marker=dict(
                        color='cyan',
                        size=15,
                        symbol='circle',
                        line=dict(color='white', width=2)
                    ),
                    text=goalkeeper,
                    textposition="top center",
                    name=goalkeeper
                ))
                
                # Add distribution pattern based on goalkeeper style
                # Short distribution targets
                short_targets = [
                    {"pos": (15, 25), "role": "Left CB", "name": "Defender 1", "frequency": 0.25, "success": 0.85},
                    {"pos": (15, 43), "role": "Right CB", "name": "Defender 2", "frequency": 0.20, "success": 0.80},
                    {"pos": (20, 15), "role": "Left FB", "name": "Defender 3", "frequency": 0.15, "success": 0.75},
                    {"pos": (20, 53), "role": "Right FB", "name": "Defender 4", "frequency": 0.15, "success": 0.75}
                ]
                
                # Long distribution targets
                long_targets = [
                    {"pos": (40, 25), "role": "Left CM", "name": "Midfielder 1", "frequency": 0.10, "success": 0.65},
                    {"pos": (40, 43), "role": "Right CM", "name": "Midfielder 2", "frequency": 0.05, "success": 0.60},
                    {"pos": (60, 15), "role": "Left Wing", "name": "Forward 1", "frequency": 0.05, "success": 0.50},
                    {"pos": (60, 53), "role": "Right Wing", "name": "Forward 2", "frequency": 0.05, "success": 0.45}
                ]
                
                # Adjust based on goalkeeper style
                if gk_short_pct > 0.65:  # Short pass preference
                    for target in short_targets:
                        target["frequency"] *= 1.3
                    for target in long_targets:
                        target["frequency"] *= 0.7
                else:  # Long pass preference
                    for target in short_targets:
                        target["frequency"] *= 0.8
                    for target in long_targets:
                        target["frequency"] *= 1.4
                
                # Add all distribution targets
                for target in short_targets + long_targets:
                    # Scale marker size by frequency
                    marker_size = 10 + (target["frequency"] * 100)
                    
                    # Add player position
                    pitch_fig.add_trace(go.Scatter(
                        x=[target["pos"][0]],
                        y=[target["pos"][1]],
                        mode='markers+text',
                        marker=dict(
                            color='blue',
                            size=marker_size,
                            symbol='circle',
                            line=dict(color='white', width=1),
                            opacity=0.7
                        ),
                        text=f"{target['role']}",
                        textposition="top center",
                        name=f"{target['role']} ({target['frequency']:.0%})"
                    ))
                    
                    # Add passing line with width based on frequency
                    line_width = 1 + (target["frequency"] * 10)
                    line_color = 'rgba(0, 255, 255, 0.7)' if target in short_targets else 'rgba(255, 165, 0, 0.7)'
                    line_dash = None if target in short_targets else 'dash'
                    
                    pitch_fig.add_trace(go.Scatter(
                        x=[gk_pos[0], target["pos"][0]],
                        y=[gk_pos[1], target["pos"][1]],
                        mode='lines',
                        line=dict(
                            color=line_color,
                            width=line_width,
                            dash=line_dash
                        ),
                        name=f"Pass to {target['role']} ({target['frequency']:.0%}, {target['success']:.0%} success)"
                    ))
                
                # Add distribution pattern annotation
                pattern_description = "Short Distribution Focused" if gk_short_pct > 0.65 else "Balanced Distribution" if gk_short_pct > 0.5 else "Long Distribution Focused"
                
                pitch_fig.add_annotation(
                    x=50,
                    y=10,
                    text=f"Distribution Pattern: {pattern_description}<br>Primary targets: {short_targets[0]['role']} and {short_targets[1]['role']}" if gk_short_pct > 0.5 else f"Distribution Pattern: {pattern_description}<br>Primary targets: {long_targets[0]['role']} and {long_targets[1]['role']}",
                    showarrow=False,
                    font=dict(size=14, color="white"),
                    bgcolor="rgba(0, 0, 0, 0.7)",
                    bordercolor="white",
                    borderwidth=1,
                    borderpad=4
                )
                
                # Update layout to ensure legend is visible and doesn't over
(Content truncated due to size limit. Use line ranges to read in chunks)