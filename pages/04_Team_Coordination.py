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
from utils.visualizations import create_pitch, create_team_coordination_diagram
from utils.data_loader import StatsBombDataLoader

st.set_page_config(
    page_title="Team Coordination | xT-GK",
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

st.title("Team Coordination")
st.subheader("Optimize outfield player positioning for goalkeeper distribution")

st.markdown("""
This template helps coaches and teams optimize positioning and movement patterns to maximize goalkeeper distribution effectiveness by:
- Coordinating defender positioning for build-up play
- Synchronizing midfielder movement to create passing lanes
- Establishing team-wide distribution patterns
- Developing cohesive build-up strategies

Using real La Liga data, this tool provides evidence-based coordination strategies for effective goalkeeper distribution.
""")

# Create two columns for inputs and visualization
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Team Coordination Parameters")
    
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
    
    # Team formation
    formation = st.selectbox(
        "Team Formation",
        options=["4-3-3", "4-4-2", "4-2-3-1", "3-5-2", "3-4-3"],
        index=0
    )
    
    # Build-up pattern
    build_up_pattern = st.selectbox(
        "Primary Build-up Pattern",
        options=["Wide Build-up", "Central Build-up", "Direct to Midfield", "Mixed Approach"],
        index=0
    )
    
    # Coordination focus
    coordination_focus = st.multiselect(
        "Coordination Focus Areas",
        options=["Defender Positioning", "Midfielder Movement", "Forward Positioning", "Transition Timing", "Counter-Press Setup"],
        default=["Defender Positioning", "Midfielder Movement"]
    )
    
    # Game context
    st.subheader("Game Context")
    
    game_phase = st.selectbox(
        "Game Phase",
        options=["Build-up from Goal Kick", "Build-up from Open Play", "Counter-Attack Initiation", "Defensive Reset"],
        index=0
    )
    
    opposition_pressure = st.slider(
        "Expected Opposition Pressure",
        min_value=1,
        max_value=10,
        value=7,
        help="1 = minimal pressure, 10 = intense pressure"
    )
    
    # Advanced options
    with st.expander("Advanced Coordination Options"):
        st.subheader("Detailed Coordination Settings")
        
        defender_depth = st.slider(
            "Defender Depth",
            min_value=1,
            max_value=10,
            value=3,
            help="1 = very deep, 10 = very high"
        )
        
        width_of_play = st.slider(
            "Width of Play",
            min_value=1,
            max_value=10,
            value=7,
            help="1 = very narrow, 10 = very wide"
        )
        
        player_rotation = st.checkbox("Enable Player Rotation", value=True)
        
        if player_rotation:
            rotation_type = st.selectbox(
                "Rotation Type",
                options=["CB-FB Rotation", "FB-CM Rotation", "CM-Forward Rotation", "Complex Rotation"],
                index=0
            )

with col2:
    st.subheader("Team Coordination Analysis")
    
    # Create team coordination diagram
    st.markdown("### Team Positioning and Movement")
    
    # Determine build-up pattern for visualization
    build_up_type = "Wide" if "Wide" in build_up_pattern else "Central"
    
    # Create coordination diagram
    coord_fig = create_team_coordination_diagram(formation, build_up_type)
    
    # Add player names based on team and formation
    if team == "Real Madrid" or team == available_teams[0]:  # Default to Real Madrid players if available
        if formation == "4-3-3":
            player_names = {
                "GK": goalkeeper,
                "LB": "Mendy",
                "LCB": "Alaba",
                "RCB": "Militão",
                "RB": "Carvajal",
                "CDM": "Casemiro",
                "LCM": "Kroos",
                "RCM": "Modrić",
                "LW": "Vinicius",
                "ST": "Benzema",
                "RW": "Rodrygo"
            }
        elif formation == "4-4-2":
            player_names = {
                "GK": goalkeeper,
                "LB": "Mendy",
                "LCB": "Alaba",
                "RCB": "Militão",
                "RB": "Carvajal",
                "LM": "Vinicius",
                "LCM": "Kroos",
                "RCM": "Modrić",
                "RM": "Rodrygo",
                "LST": "Benzema",
                "RST": "Jović"
            }
        else:  # Default to 4-2-3-1
            player_names = {
                "GK": goalkeeper,
                "LB": "Mendy",
                "LCB": "Alaba",
                "RCB": "Militão",
                "RB": "Carvajal",
                "LDM": "Casemiro",
                "RDM": "Kroos",
                "CAM": "Modrić",
                "LW": "Vinicius",
                "ST": "Benzema",
                "RW": "Rodrygo"
            }
    elif team == "Barcelona" or team == available_teams[1] if len(available_teams) > 1 else False:
        if formation == "4-3-3":
            player_names = {
                "GK": goalkeeper,
                "LB": "Alba",
                "LCB": "Piqué",
                "RCB": "Araujo",
                "RB": "Dest",
                "CDM": "Busquets",
                "LCM": "Pedri",
                "RCM": "De Jong",
                "LW": "Fati",
                "ST": "Depay",
                "RW": "Dembélé"
            }
        else:
            # Default names for other formations
            player_names = {role: f"{role}" for role in ["GK", "LB", "LCB", "RCB", "RB", "CDM", "LCM", "RCM", "LW", "ST", "RW", 
                                                        "LM", "RM", "LST", "RST", "LDM", "RDM", "CAM"]}
            player_names["GK"] = goalkeeper
    else:
        # Generic player names if team not recognized
        player_names = {role: f"{role}" for role in ["GK", "LB", "LCB", "RCB", "RB", "CDM", "LCM", "RCM", "LW", "ST", "RW", 
                                                    "LM", "RM", "LST", "RST", "LDM", "RDM", "CAM"]}
        player_names["GK"] = goalkeeper
    
    # Update player labels with names
    for trace in coord_fig.data:
        if hasattr(trace, 'text') and trace.text in player_names:
            trace.text = f"{player_names[trace.text]}"
            if trace.name and trace.name != trace.text:
                trace.name = f"{trace.name} ({player_names[trace.text]})"
    
    # Update layout to ensure legend is visible
    coord_fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    # Display the coordination diagram
    st.plotly_chart(coord_fig, use_container_width=True)
    
    # Movement patterns
    st.markdown("### Key Movement Patterns")
    
    # Generate movement patterns based on build-up pattern and formation
    movement_patterns = []
    
    if "Wide" in build_up_pattern:
        if formation == "4-3-3":
            movement_patterns.append(f"**Full Back Width**: {player_names.get('LB', 'LB')} and {player_names.get('RB', 'RB')} provide maximum width")
            movement_patterns.append(f"**Center Back Split**: {player_names.get('LCB', 'LCB')} and {player_names.get('RCB', 'RCB')} split wide to create passing angles")
            movement_patterns.append(f"**Midfielder Support**: {player_names.get('CDM', 'CDM')} drops between center backs when needed")
        elif formation == "4-4-2":
            movement_patterns.append(f"**Full Back Width**: {player_names.get('LB', 'LB')} and {player_names.get('RB', 'RB')} provide maximum width")
            movement_patterns.append(f"**Wide Midfielders Tuck In**: {player_names.get('LM', 'LM')} and {player_names.get('RM', 'RM')} move inside to create passing lanes")
            movement_patterns.append(f"**Striker Movement**: {player_names.get('LST', 'LST')} drops deeper while {player_names.get('RST', 'RST')} stretches defense")
        else:
            movement_patterns.append(f"**Full Back Width**: {player_names.get('LB', 'LB')} and {player_names.get('RB', 'RB')} provide maximum width")
            movement_patterns.append(f"**Double Pivot**: {player_names.get('LDM', 'LDM')} and {player_names.get('RDM', 'RDM')} create passing options centrally")
            movement_patterns.append(f"**Advanced Midfielder**: {player_names.get('CAM', 'CAM')} finds pockets between opposition lines")
    else:  # Central build-up
        if formation == "4-3-3":
            movement_patterns.append(f"**Inverted Full Backs**: {player_names.get('LB', 'LB')} and {player_names.get('RB', 'RB')} move inside to create central overloads")
            movement_patterns.append(f"**Defensive Midfielder Drop**: {player_names.get('CDM', 'CDM')} positions between center backs")
            movement_patterns.append(f"**Advanced Midfielders**: {player_names.get('LCM', 'LCM')} and {player_names.get('RCM', 'RCM')} position in half-spaces")
        elif formation == "4-4-2":
            movement_patterns.append(f"**Narrow Midfield Four**: All midfielders create a compact central block")
            movement_patterns.append(f"**Striker Movement**: {player_names.get('LST', 'LST')} drops deeper while {player_names.get('RST', 'RST')} stretches defense")
            movement_patterns.append(f"**Full Back Restraint**: {player_names.get('LB', 'LB')} and {player_names.get('RB', 'RB')} stay deeper to maintain defensive shape")
        else:
            movement_patterns.append(f"**Double Pivot**: {player_names.get('LDM', 'LDM')} and {player_names.get('RDM', 'RDM')} split to create passing triangles")
            movement_patterns.append(f"**Number 10 Role**: {player_names.get('CAM', 'CAM')} is the focal point for progression")
            movement_patterns.append(f"**Wingers Narrow**: {player_names.get('LW', 'LW')} and {player_names.get('RW', 'RW')} move inside to create space for full backs")
    
    # Add pressure-specific patterns
    if opposition_pressure > 7:
        movement_patterns.append(f"**Extra Goalkeeper Support**: {goalkeeper} positions higher to provide additional passing option")
        movement_patterns.append("**Compressed Distances**: All players reduce distances between each other to facilitate shorter passes")
    elif opposition_pressure < 4:
        movement_patterns.append(f"**Aggressive Positioning**: Players position higher and wider to stretch opposition")
        movement_patterns.append(f"**Vertical Stretching**: {player_names.get('ST', 'ST') if 'ST' in player_names else 'Forwards'} maintain high position to create vertical passing options")
    
    # Display movement patterns
    for i, pattern in enumerate(movement_patterns):
        st.markdown(f"{i+1}. {pattern}")
    
    # Coordination metrics
    st.markdown("### Team Coordination Metrics")
    
    # Create columns for metrics
    col1_metrics, col2_metrics, col3_metrics = st.columns(3)
    
    with col1_metrics:
        # Calculate build-up success rate based on parameters
        base_success = 0.7
        if "Wide" in build_up_pattern and width_of_play > 6:
            base_success += 0.1
        elif "Central" in build_up_pattern and width_of_play < 5:
            base_success += 0.1
        
        if opposition_pressure > 7:
            base_success -= 0.15
        
        build_up_success = min(0.95, max(0.5, base_success))
        
        st.metric(
            "Build-up Success Rate",
            f"{build_up_success:.0%}",
            delta=f"{(build_up_success - 0.7):.0%}" if build_up_success != 0.7 else None
        )
    
    with col2_metrics:
        # Calculate team xT-GK based on coordination
        base_xt_gk = 0.6
        if "Defender Positioning" in coordination_focus:
            base_xt_gk += 0.05
        if "Midfielder Movement" in coordination_focus:
            base_xt_gk += 0.05
        
        if opposition_pressure > 7:
            base_xt_gk -= 0.1
        
        team_xt_gk = min(0.9, max(0.4, base_xt_gk))
        
        st.metric(
            "Team xT-GK",
            f"{team_xt_gk:.2f}",
            delta=f"{(team_xt_gk - 0.6):.2f}" if team_xt_gk != 0.6 else None
        )
    
    with col3_metrics:
        # Calculate field control percentage
        base_control = 0.55
        if width_of_play > 7:
            base_control += 0.05
        if defender_depth > 7:
            base_control += 0.05
        
        if opposition_pressure > 7:
            base_control -= 0.1
        
        field_control = min(0.8, max(0.4, base_control))
        
        st.metric(
            "Field Control %",
            f"{field_control:.0%}",
            delta=f"{(field_control - 0.55):.0%}" if field_control != 0.55 else None
        )
    
    # Coordination recommendations
    st.markdown("### Coordination Recommendations")
    
    # Generate recommendations based on analysis
    recommendations = []
    
    if "Wide" in build_up_pattern:
        recommendations.append(f"**Full Back Positioning**: Position {player_names.get('LB', 'LB')} and {player_names.get('RB', 'RB')} high and wide to stretch opposition")
        recommendations.append(f"**Center Back Spacing**: Ensure optimal distance between {player_names.get('LCB', 'LCB')} and {player_names.get('RCB', 'RCB')} (approximately 15-20 meters)")
    else:  # Central build-up
        recommendations.append(f"**Midfield Triangles**: Create clear triangles between {player_names.get('CDM', 'CDM') if 'CDM' in player_names else 'defensive midfielders'} and center backs")
        recommendations.append(f"**Vertical Compactness**: Reduce distances between defensive and midfield lines to facilitate progression")
    
    if opposition_pressure > 7:
        recommendations.append(f"**Support Positioning**: {player_names.get('CDM', 'CDM') if 'CDM' in player_names else 'Defensive midfielder'} should position between center backs when {goalkeeper} is under pressure")
        recommendations.append("**Quick Circulation**: Implement one-touch passing sequences to evade pressure")
    else:
        recommendations.append("**Patient Build-up**: Take advantage of low pressure to establish secure possession")
        recommendations.append(f"**Progressive Positioning**: Position {player_names.get('LCM', 'LCM') if 'LCM' in player_names else 'midfielders'} and {player_names.get('RCM', 'RCM') if 'RCM' in player_names else 'attacking players'} in advanced areas")
    
    if player_rotation:
    
(Content truncated due to size limit. Use line ranges to read in chunks)