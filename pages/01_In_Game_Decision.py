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
from utils.visualizations import create_pitch, plot_distribution_options
from utils.data_loader import StatsBombDataLoader
from utils.pdf_generator import generate_in_game_decision_pdf

st.set_page_config(
    page_title="In-Game Decision | xT-GK",
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

st.title("In-Game Decision Making")
st.subheader("Optimize goalkeeper distribution based on game state and pressure")

st.markdown("""
This template helps goalkeepers and coaches make optimal in-game distribution decisions by:
- Analyzing available distribution options
- Evaluating success probability under current pressure
- Considering tactical context and game state
- Providing clear, actionable recommendations

Using real La Liga data, this tool provides evidence-based distribution recommendations for specific match situations.
""")

# Create two columns for inputs and visualization
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Match Situation")
    
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
    
    # Match context
    st.subheader("Match Context")
    
    match_minute = st.slider(
        "Match Minute",
        min_value=1,
        max_value=90,
        value=65
    )
    
    score_state = st.selectbox(
        "Score State",
        options=["Winning", "Drawing", "Losing"],
        index=1
    )
    
    game_state = st.selectbox(
        "Game State",
        options=["Build-up from Goal Kick", "Build-up from Open Play", "Counter-Attack Opportunity", "Defensive Reset"],
        index=0
    )
    
    # Pressure situation
    st.subheader("Pressure Situation")
    
    pressure_level = st.slider(
        "Opposition Pressure Level",
        min_value=1,
        max_value=10,
        value=7,
        help="1 = minimal pressure, 10 = intense pressure"
    )
    
    pressure_type = st.selectbox(
        "Pressure Type",
        options=["Single Striker Press", "Two-Player Press", "Team Press", "No Immediate Pressure"],
        index=1 if pressure_level > 5 else 3
    )
    
    # Advanced options
    with st.expander("Advanced Options"):
        st.subheader("Tactical Considerations")
        
        team_tactical_approach = st.selectbox(
            "Team Tactical Approach",
            options=["Possession-Based", "Direct Play", "Counter-Attacking", "Mixed Approach"],
            index=0
        )
        
        opposition_formation = st.selectbox(
            "Opposition Formation",
            options=["4-3-3", "4-4-2", "4-2-3-1", "3-5-2", "3-4-3"],
            index=0
        )
        
        field_conditions = st.selectbox(
            "Field Conditions",
            options=["Dry", "Wet", "Windy"],
            index=0
        )

with col2:
    st.subheader("Distribution Analysis")
    
    # Create pitch visualization
    st.markdown("### Available Distribution Options")
    
    # Generate distribution options based on inputs
    distribution_options = []
    
    # Short options (always available)
    short_options = [
        {"name": "Left Center Back", "position": (15, 25), "distance": "short", "pressure": "low", "xT_value": 0.65},
        {"name": "Right Center Back", "position": (15, 43), "distance": "short", "pressure": "low", "xT_value": 0.68}
    ]
    
    # Add full backs if in build-up
    if game_state in ["Build-up from Goal Kick", "Build-up from Open Play"]:
        short_options.extend([
            {"name": "Left Full Back", "position": (20, 15), "distance": "short", "pressure": "medium", "xT_value": 0.58},
            {"name": "Right Full Back", "position": (20, 53), "distance": "short", "pressure": "medium", "xT_value": 0.56}
        ])
    
    # Medium options
    medium_options = [
        {"name": "Defensive Midfielder", "position": (30, 34), "distance": "medium", "pressure": "medium", "xT_value": 0.52},
        {"name": "Left Midfielder", "position": (40, 20), "distance": "medium", "pressure": "high", "xT_value": 0.48},
        {"name": "Right Midfielder", "position": (40, 48), "distance": "medium", "pressure": "high", "xT_value": 0.45}
    ]
    
    # Long options
    long_options = [
        {"name": "Left Winger", "position": (60, 15), "distance": "long", "pressure": "high", "xT_value": 0.35},
        {"name": "Striker", "position": (60, 34), "distance": "long", "pressure": "high", "xT_value": 0.32},
        {"name": "Right Winger", "position": (60, 53), "distance": "long", "pressure": "high", "xT_value": 0.30}
    ]
    
    # Adjust options based on game state
    if game_state == "Counter-Attack Opportunity":
        # Prioritize longer options for counter
        distribution_options = short_options[:1] + medium_options[1:] + long_options
    elif game_state == "Defensive Reset":
        # Prioritize safer options
        distribution_options = short_options + medium_options[:1]
    else:
        # Standard build-up
        distribution_options = short_options + medium_options + long_options
    
    # Adjust xT values based on pressure
    pressure_factor = 1.0 - (pressure_level / 20)  # Higher pressure reduces xT
    for option in distribution_options:
        base_xt = option["xT_value"]
        
        # Pressure affects different distances differently
        if option["distance"] == "short" and pressure_level > 7:
            option["xT_value"] = base_xt * (pressure_factor * 0.8)  # Short passes more affected by high pressure
        elif option["distance"] == "long" and pressure_level > 5:
            option["xT_value"] = base_xt * (pressure_factor * 0.9)  # Long passes somewhat affected
        else:
            option["xT_value"] = base_xt * pressure_factor
    
    # Adjust based on tactical approach
    for option in distribution_options:
        if team_tactical_approach == "Possession-Based" and option["distance"] == "short":
            option["xT_value"] *= 1.2  # Boost short options for possession teams
        elif team_tactical_approach == "Direct Play" and option["distance"] == "long":
            option["xT_value"] *= 1.2  # Boost long options for direct play
        elif team_tactical_approach == "Counter-Attacking" and option["distance"] in ["medium", "long"]:
            option["xT_value"] *= 1.15  # Boost medium/long for counter
    
    # Adjust based on score state
    for option in distribution_options:
        if score_state == "Winning" and option["distance"] == "short":
            option["xT_value"] *= 1.1  # Safer options when winning
        elif score_state == "Losing" and option["distance"] == "long":
            option["xT_value"] *= 1.1  # Riskier options when losing
    
    # Create the pitch visualization with distribution options
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
    
    # Add distribution options with player names and xT values
    for option in distribution_options:
        # Determine color based on xT value
        if option["xT_value"] > 0.6:
            color = 'rgba(0, 255, 0, 0.8)'  # Green for high xT
        elif option["xT_value"] > 0.4:
            color = 'rgba(255, 255, 0, 0.8)'  # Yellow for medium xT
        else:
            color = 'rgba(255, 165, 0, 0.8)'  # Orange for low xT
        
        # Determine line style based on distance
        if option["distance"] == "short":
            dash = None
            width = 3
        elif option["distance"] == "medium":
            dash = 'dot'
            width = 2
        else:  # long
            dash = 'dash'
            width = 2
        
        # Add player position
        pitch_fig.add_trace(go.Scatter(
            x=[option["position"][0]],
            y=[option["position"][1]],
            mode='markers+text',
            marker=dict(
                color='blue',
                size=12,
                symbol='circle',
                line=dict(color='white', width=1)
            ),
            text=f"{option['name']}",
            textposition="top center",
            name=f"{option['name']} (xT: {option['xT_value']:.2f})"
        ))
        
        # Add passing line
        pitch_fig.add_trace(go.Scatter(
            x=[gk_pos[0], option["position"][0]],
            y=[gk_pos[1], option["position"][1]],
            mode='lines',
            line=dict(
                color=color,
                width=width,
                dash=dash
            ),
            name=f"{option['distance'].capitalize()} pass to {option['name']}"
        ))
        
        # Add xT value label
        pitch_fig.add_annotation(
            x=option["position"][0],
            y=option["position"][1] - 3,
            text=f"xT: {option['xT_value']:.2f}",
            showarrow=False,
            font=dict(size=10, color="white"),
            bgcolor="rgba(0, 0, 0, 0.7)",
            bordercolor="white",
            borderwidth=1,
            borderpad=2
        )
    
    # Add pressure visualization if high pressure
    if pressure_level > 5:
        if pressure_type == "Single Striker Press":
            pressure_positions = [(8, 34)]
        elif pressure_type == "Two-Player Press":
            pressure_positions = [(8, 30), (8, 38)]
        elif pressure_type == "Team Press":
            pressure_positions = [(8, 30), (8, 38), (12, 25), (12, 43)]
        else:
            pressure_positions = []
        
        for pos in pressure_positions:
            pitch_fig.add_trace(go.Scatter(
                x=[pos[0]],
                y=[pos[1]],
                mode='markers',
                marker=dict(
                    color='red',
                    size=12,
                    symbol='x',
                    line=dict(color='white', width=1)
                ),
                name="Opposition Player"
            ))
    
    # Update layout to ensure legend is visible
    pitch_fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    # Display the pitch visualization
    st.plotly_chart(pitch_fig, use_container_width=True)
    
    # Find best option based on xT value
    best_option = max(distribution_options, key=lambda x: x["xT_value"])
    
    # Distribution recommendation
    st.markdown("### Distribution Recommendation")
    
    # Create recommendation based on analysis
    recommendation = f"**Primary Option**: {best_option['name']} (xT: {best_option['xT_value']:.2f})"
    
    # Add context to recommendation
    if pressure_level > 7:
        recommendation += f"\n\nUnder high pressure ({pressure_level}/10), prioritize ball retention with a {best_option['distance']} pass to {best_option['name']}."
    elif score_state == "Winning" and match_minute > 75:
        recommendation += f"\n\nWith the lead late in the game ({match_minute}'), focus on secure distribution to {best_option['name']} to maintain possession."
    elif score_state == "Losing" and match_minute > 70:
        recommendation += f"\n\nTrailing late in the game ({match_minute}'), this {best_option['distance']} distribution option offers the best balance of risk and reward."
    else:
        recommendation += f"\n\nIn the current {game_state.lower()} situation, distributing to {best_option['name']} provides the highest expected threat value."
    
    # Add tactical context
    if team_tactical_approach == "Possession-Based":
        recommendation += f"\n\nThis aligns with the team's possession-based approach, allowing for controlled build-up play."
    elif team_tactical_approach == "Direct Play":
        recommendation += f"\n\nThis supports the team's direct playing style, bypassing opposition lines efficiently."
    elif team_tactical_approach == "Counter-Attacking":
        recommendation += f"\n\nThis distribution can initiate a quick counter-attack, exploiting space behind the opposition."
    
    # Display recommendation
    st.markdown(recommendation)
    
    # Alternative options
    st.markdown("### Alternative Options")
    
    # Sort remaining options by xT value
    alternative_options = sorted([opt for opt in distribution_options if opt != best_option], 
                                key=lambda x: x["xT_value"], reverse=True)[:2]
    
    for i, option in enumerate(alternative_options):
        st.markdown(f"**Alternative {i+1}**: {option['name']} (xT: {option['xT_value']:.2f})")
        
        # Add context for alternative
        if option["distance"] == "short" and best_option["distance"] != "short":
            st.markdown("*Safer option with lower risk but potentially less reward*")
        elif option["distance"] == "long" and best_option["distance"] != "long":
            st.markdown("*Higher risk option that could bypass more opposition players*")
        else:
            st.markdown(f"*Alternative {option['distance']} distribution option with slightly lower expected value*")

# Download options
st.markdown("---")
st.subheader("Export Analysis")

# Create PDF export functionality
pdf_data = generate_in_game_decision_pdf(
    gk_name=goalkeeper,
    team_name=team,
    match_situation=f"{game_state} ({match_minute}', {score_state})",
    pressure_level=pressure_level,
    distribution_options=[f"{opt['name']} (xT: {opt['xT_value']:.2f})" for opt in distribution_options],
    recommendation=recommendation,
    pitch_fig=pitch_fig
)

col1, col2 = st.columns(2)
with col1:
    st.download_button(
        label="Download Analysis as PDF",
        data=pdf_data,
        file_name="xt_gk_in_game_decision.pdf",
        mime="application/pdf",
    )

with col2:
    st.download_button(
        label="Download Distribution Data",
        data=pd.DataFrame([{
            "Option": opt["name"],
            "Distance": opt["distance"],
            "Pressure": opt["pressure"],
            "xT_Value": opt["xT_value"]
        } for opt in distribution_options]).to_csv(index=False).encode('utf-8'),
        file_name="xt_gk_distribution_options.csv",
        mime="text/csv",
    )
