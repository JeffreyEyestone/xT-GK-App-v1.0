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

st.set_page_config(
    page_title="Training Development | xT-GK",
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

st.title("Training Development")
st.subheader("Design targeted training programs for goalkeeper distribution")

st.markdown("""
This template helps coaches design effective training programs to improve goalkeeper distribution by:
- Identifying specific distribution strengths and weaknesses
- Creating targeted training exercises
- Tracking development progress
- Establishing measurable improvement goals

Using real La Liga data, this tool provides evidence-based training recommendations for goalkeeper distribution development.
""")

# Create two columns for inputs and visualization
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Training Development Parameters")
    
    # Select teams from real data
    available_teams = []
    for match in match_info:
        if match['home_team'] not in available_teams:
            available_teams.append(match['home_team'])
        if match['away_team'] not in available_teams:
            available_teams.append(match['away_team'])
    
    if not available_teams:
        available_teams = ["Team A", "Team B", "Team C"]  # Fallback
    
    team = st.selectbox(
        "Team",
        options=available_teams,
        index=0
    )
    
    # Select goalkeeper
    team_goalkeepers = []
    for gk in gk_data:
        if gk['team_name'] == team:
            team_goalkeepers.append(gk['player_name'])
    
    if not team_goalkeepers:
        team_goalkeepers = ["Team Goalkeeper"]  # Fallback
    
    goalkeeper = st.selectbox(
        "Goalkeeper",
        options=team_goalkeepers,
        index=0
    )
    
    # Training focus
    st.subheader("Training Focus")
    
    primary_focus = st.selectbox(
        "Primary Development Focus",
        options=["Short Distribution Accuracy", "Long Distribution Accuracy", "Decision Making Under Pressure", "Distribution Speed", "Tactical Awareness"],
        index=0
    )
    
    secondary_focus = st.multiselect(
        "Secondary Development Areas",
        options=["Short Distribution Accuracy", "Long Distribution Accuracy", "Decision Making Under Pressure", "Distribution Speed", "Tactical Awareness"],
        default=["Decision Making Under Pressure"]
    )
    
    # Remove primary focus from secondary if selected
    if primary_focus in secondary_focus:
        secondary_focus.remove(primary_focus)
    
    # Training context
    st.subheader("Training Context")
    
    training_phase = st.selectbox(
        "Training Phase",
        options=["Pre-Season", "In-Season", "Recovery Period", "International Break"],
        index=1
    )
    
    training_duration = st.slider(
        "Training Program Duration (weeks)",
        min_value=1,
        max_value=12,
        value=4
    )
    
    sessions_per_week = st.slider(
        "Distribution Sessions Per Week",
        min_value=1,
        max_value=5,
        value=3
    )
    
    # Advanced options
    with st.expander("Advanced Training Options"):
        st.subheader("Detailed Training Settings")
        
        include_team_training = st.checkbox("Include Team-Based Training", value=True)
        
        if include_team_training:
            team_involvement = st.multiselect(
                "Team Members to Include",
                options=["Center Backs", "Full Backs", "Defensive Midfielders", "Central Midfielders", "Forwards"],
                default=["Center Backs", "Full Backs", "Defensive Midfielders"]
            )
        
        include_video_analysis = st.checkbox("Include Video Analysis", value=True)
        
        if include_video_analysis:
            video_focus = st.multiselect(
                "Video Analysis Focus",
                options=["Self-Analysis", "Elite GK Examples", "Opposition Analysis", "Team Pattern Analysis"],
                default=["Self-Analysis", "Elite GK Examples"]
            )
        
        include_metrics_tracking = st.checkbox("Include Metrics Tracking", value=True)

with col2:
    st.subheader("Goalkeeper Development Analysis")
    
    # Display goalkeeper profile
    st.markdown(f"### {goalkeeper} Distribution Profile")
    
    # Create metrics display
    col1_metrics, col2_metrics, col3_metrics = st.columns(3)
    
    # Simulate goalkeeper stats based on selected goalkeeper
    # In a real app, this would use actual data from the database
    gk_success_rate = 0.72
    gk_short_pct = 0.65
    gk_long_pct = 0.35
    gk_pressure_pct = 0.40
    gk_total_passes = 28
    
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
    
    # Goalkeeper strengths and weaknesses
    st.markdown("### Distribution Strengths and Weaknesses")
    
    # Create radar chart data
    gk_data_dict = {
        "Short Accuracy": 0.75,
        "Long Accuracy": 0.60,
        "Decision Making": 0.65,
        "Speed of Release": 0.70,
        "Tactical Awareness": 0.55
    }
    
    # Adjust based on primary focus (simulate a weakness in that area)
    if primary_focus == "Short Distribution Accuracy":
        gk_data_dict["Short Accuracy"] = 0.55
    elif primary_focus == "Long Distribution Accuracy":
        gk_data_dict["Long Accuracy"] = 0.45
    elif primary_focus == "Decision Making Under Pressure":
        gk_data_dict["Decision Making"] = 0.50
    elif primary_focus == "Distribution Speed":
        gk_data_dict["Speed of Release"] = 0.55
    elif primary_focus == "Tactical Awareness":
        gk_data_dict["Tactical Awareness"] = 0.45
    
    # League average for comparison
    league_avg = {
        "Short Accuracy": 0.70,
        "Long Accuracy": 0.55,
        "Decision Making": 0.60,
        "Speed of Release": 0.65,
        "Tactical Awareness": 0.60
    }
    
    # Create radar chart
    radar_fig = create_radar_chart(gk_data_dict, league_avg)
    
    # Update chart title and layout
    radar_fig.update_layout(
        title=f"{goalkeeper} vs. League Average",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True
    )
    
    # Display the radar chart
    st.plotly_chart(radar_fig, use_container_width=True)
    
    # Training program visualization
    st.markdown("### Training Program Visualization")
    
    # Create pitch visualization for training exercises
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
    
    # Add training exercise visualization based on primary focus
    if primary_focus == "Short Distribution Accuracy":
        # Short distribution training setup
        targets = [
            {"pos": (15, 25), "role": "Left CB", "name": "Ramos", "distance": "short"},
            {"pos": (15, 43), "role": "Right CB", "name": "Varane", "distance": "short"},
            {"pos": (20, 15), "role": "Left FB", "name": "Marcelo", "distance": "short"},
            {"pos": (20, 53), "role": "Right FB", "name": "Carvajal", "distance": "short"}
        ]
        
        # Add training cones for accuracy targets
        for i, target in enumerate(targets):
            # Add player position
            pitch_fig.add_trace(go.Scatter(
                x=[target["pos"][0]],
                y=[target["pos"][1]],
                mode='markers+text',
                marker=dict(
                    color='blue',
                    size=12,
                    symbol='circle',
                    line=dict(color='white', width=1)
                ),
                text=f"{target['name']}",
                textposition="top center",
                name=f"{target['role']} ({target['name']})"
            ))
            
            # Add accuracy target zones (cones)
            pitch_fig.add_shape(
                type="circle",
                x0=target["pos"][0] - 2,
                y0=target["pos"][1] - 2,
                x1=target["pos"][0] + 2,
                y1=target["pos"][1] + 2,
                line=dict(color="orange", width=2),
                fillcolor="rgba(255, 165, 0, 0.3)"
            )
            
            # Add passing line
            pitch_fig.add_trace(go.Scatter(
                x=[gk_pos[0], target["pos"][0]],
                y=[gk_pos[1], target["pos"][1]],
                mode='lines',
                line=dict(
                    color='rgba(0, 255, 255, 0.7)',
                    width=2
                ),
                name=f'Pass to {target["role"]}'
            ))
        
        # Add training description annotation
        pitch_fig.add_annotation(
            x=50,
            y=10,
            text="Short Distribution Accuracy Training:<br>Target specific zones with varied pressure",
            showarrow=False,
            font=dict(size=14, color="white"),
            bgcolor="rgba(0, 0, 0, 0.7)",
            bordercolor="white",
            borderwidth=1,
            borderpad=4
        )
        
    elif primary_focus == "Long Distribution Accuracy":
        # Long distribution training setup
        targets = [
            {"pos": (60, 15), "role": "Left Wing", "name": "Vinicius", "distance": "long"},
            {"pos": (70, 34), "role": "Striker", "name": "Benzema", "distance": "long"},
            {"pos": (60, 53), "role": "Right Wing", "name": "Bale", "distance": "long"}
        ]
        
        # Add training targets for long distribution
        for i, target in enumerate(targets):
            # Add player position
            pitch_fig.add_trace(go.Scatter(
                x=[target["pos"][0]],
                y=[target["pos"][1]],
                mode='markers+text',
                marker=dict(
                    color='blue',
                    size=12,
                    symbol='circle',
                    line=dict(color='white', width=1)
                ),
                text=f"{target['name']}",
                textposition="top center",
                name=f"{target['role']} ({target['name']})"
            ))
            
            # Add accuracy target zones (larger for long passes)
            pitch_fig.add_shape(
                type="circle",
                x0=target["pos"][0] - 5,
                y0=target["pos"][1] - 5,
                x1=target["pos"][0] + 5,
                y1=target["pos"][1] + 5,
                line=dict(color="orange", width=2),
                fillcolor="rgba(255, 165, 0, 0.3)"
            )
            
            # Add passing line
            pitch_fig.add_trace(go.Scatter(
                x=[gk_pos[0], target["pos"][0]],
                y=[gk_pos[1], target["pos"][1]],
                mode='lines',
                line=dict(
                    color='rgba(255, 165, 0, 0.7)',
                    width=2,
                    dash='dash'
                ),
                name=f'Long Pass to {target["role"]}'
            ))
        
        # Add training description annotation
        pitch_fig.add_annotation(
            x=50,
            y=10,
            text="Long Distribution Accuracy Training:<br>Target specific zones with varied distances and angles",
            showarrow=False,
            font=dict(size=14, color="white"),
            bgcolor="rgba(0, 0, 0, 0.7)",
            bordercolor="white",
            borderwidth=1,
            borderpad=4
        )
        
    elif primary_focus == "Decision Making Under Pressure":
        # Decision making training setup
        targets = [
            {"pos": (15, 25), "role": "Left CB", "name": "Ramos", "distance": "short"},
            {"pos": (15, 43), "role": "Right CB", "name": "Varane", "distance": "short"},
            {"pos": (60, 15), "role": "Left Wing", "name": "Vinicius", "distance": "long"},
            {"pos": (60, 53), "role": "Right Wing", "name": "Bale", "distance": "long"}
        ]
        
        # Add training targets
        for i, target in enumerate(targets):
            # Add player position
            pitch_fig.add_trace(go.Scatter(
                x=[target["pos"][0]],
                y=[target["pos"][1]],
                mode='markers+text',
                marker=dict(
                    color='blue',
                    size=12,
                    symbol='circle',
                    line=dict(color='white', width=1)
                ),
                text=f"{target['name']}",
                textposition="top center",
                name=f"{target['role']} ({target['name']})"
            ))
            
            # Add passing line
            line_color = 'rgba(0, 255, 255, 0.7)' if target["distance"] == "short" else 'rgba(255, 165, 0, 0.7)'
            line_dash = None if target["distance"] == "short" else 'dash'
            
            pitch_fig.add_trace(go.Scatter(
                x=[gk_pos[0], target["pos"][0]],
                y=[gk_pos[1], target["pos"][1]],
                mode='lines',
                line=dict(
                    color=line_color,
                    width=2,
                    dash=line_dash
                ),
                name=f'{target["distance"].capitalize()} Pass to {target["role"]}'
            ))
        
        # Add pressure players
        pressure_positions = [
            {"pos": (10, 25), "role": "Presser", "name": "Suárez"},
            {"pos": (12, 43), "role": "Presser", "name": "Griezmann"}
        ]
        
        for pressure in pressure_positions:
            pitch_fig.add_trace(go.Scatter(
                x=[pressure["pos"][0]],
                y=[pressure["pos"][1]],
                mode='markers+text',
                marker=dict(
                    color='red',
                    size=12,
                    symbol='x',
                    line=dict(color='white', width=1)
                ),
                text=f"{pressure['name']}",
                textposition="top center",
                name=f"Pressure ({pressure['name']})"
            ))
        
        # Add training description annotation
        pitch_fig.add_annotation(
            x=50,
            y=10,
            text="Decision Making Training:<br>Make optimal distribution choices under varied pressure",
            showarrow=False,
            font=dict(size=14, color="white"),
            bgcolor="rgba(0, 0, 0, 0.7)",
            bordercolor="white",
            borderwidth=1,
            borderpad=4
        )

(Content truncated due to size limit. Use line ranges to read in chunks)