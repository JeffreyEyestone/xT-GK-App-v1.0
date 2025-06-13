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
from utils.visualizations import create_pitch, create_opposition_analysis
from utils.data_loader import StatsBombDataLoader
from utils.pdf_generator import generate_opposition_analysis_pdf

st.set_page_config(
    page_title="Opposition Analysis (Our GK) | xT-GK",
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

st.title("Opposition Analysis (Our GK)")
st.subheader("Prepare your goalkeeper for upcoming opponents' pressing patterns")

st.markdown("""
This template helps coaches prepare their goalkeeper for upcoming opponents by:
- Analyzing opposition pressing patterns and triggers
- Identifying optimal distribution targets against specific opponents
- Developing counter-strategies for opposition pressing
- Creating goalkeeper-specific match plans

Using real La Liga data, this tool provides evidence-based preparation for goalkeeper distribution against specific opponents.
""")

# Create two columns for inputs and visualization
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Match-Up Parameters")
    
    # Select teams from real data
    available_teams = []
    for match in match_info:
        if match['home_team'] not in available_teams:
            available_teams.append(match['home_team'])
        if match['away_team'] not in available_teams:
            available_teams.append(match['away_team'])
    
    if not available_teams:
        available_teams = ["Team A", "Team B", "Team C"]  # Fallback
    
    # Your team
    team = st.selectbox(
        "Your Team",
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
        "Your Goalkeeper",
        options=team_goalkeepers,
        index=0
    )
    
    # Opposition team
    opposition_options = [t for t in available_teams if t != team]
    if not opposition_options:
        opposition_options = ["Opposition Team"]  # Fallback
    
    opposition_team = st.selectbox(
        "Opposition Team",
        options=opposition_options,
        index=0
    )
    
    # Opposition analysis
    st.subheader("Opposition Analysis")
    
    opposition_formation = st.selectbox(
        "Opposition Formation",
        options=["4-3-3", "4-4-2", "4-2-3-1", "3-5-2", "3-4-3"],
        index=0
    )
    
    pressing_intensity = st.slider(
        "Pressing Intensity",
        min_value=1,
        max_value=10,
        value=7,
        help="1 = low intensity, 10 = high intensity"
    )
    
    pressing_triggers = st.multiselect(
        "Pressing Triggers",
        options=["Back Pass to GK", "Horizontal Pass Between CBs", "First Touch Control", "GK Receives Under Pressure", "Slow Build-up"],
        default=["Back Pass to GK", "GK Receives Under Pressure"]
    )
    
    # Match context
    st.subheader("Match Context")
    
    match_venue = st.radio(
        "Match Venue",
        options=["Home", "Away"],
        index=0
    )
    
    expected_game_state = st.selectbox(
        "Expected Game State",
        options=["Balanced Game", "Likely Leading", "Likely Trailing", "Must Win"],
        index=0
    )
    
    # Advanced options
    with st.expander("Advanced Analysis Options"):
        st.subheader("Detailed Analysis Settings")
        
        analyze_by_game_phase = st.checkbox("Analyze by Game Phase", value=True)
        
        if analyze_by_game_phase:
            game_phases = st.multiselect(
                "Game Phases to Analyze",
                options=["Goal Kicks", "Open Play Build-up", "Counter-Attack Initiation", "Defensive Reset"],
                default=["Goal Kicks", "Open Play Build-up"]
            )
        
        analyze_by_score_state = st.checkbox("Analyze by Score State", value=False)
        
        if analyze_by_score_state:
            score_states = st.multiselect(
                "Score States to Analyze",
                options=["When Leading", "When Drawing", "When Trailing"],
                default=["When Drawing"]
            )

with col2:
    st.subheader("Opposition Analysis Results")
    
    # Create opposition analysis visualization
    st.markdown("### Opposition Pressing Pattern")
    
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
    
    # Add opposition pressing pattern based on formation and intensity
    if opposition_formation == "4-3-3":
        # 4-3-3 pressing pattern
        pressing_positions = [
            {"pos": (10, 34), "role": "Striker", "name": "Forward 1"},
            {"pos": (15, 20), "role": "Left Winger", "name": "Forward 2"},
            {"pos": (15, 48), "role": "Right Winger", "name": "Forward 3"},
            {"pos": (25, 34), "role": "Central Midfielder", "name": "Midfielder 1"}
        ]
    elif opposition_formation == "4-4-2":
        # 4-4-2 pressing pattern
        pressing_positions = [
            {"pos": (10, 28), "role": "Left Striker", "name": "Forward 1"},
            {"pos": (10, 40), "role": "Right Striker", "name": "Forward 2"},
            {"pos": (20, 20), "role": "Left Midfielder", "name": "Midfielder 1"},
            {"pos": (20, 48), "role": "Right Midfielder", "name": "Midfielder 2"}
        ]
    else:
        # Default pressing pattern for other formations
        pressing_positions = [
            {"pos": (10, 34), "role": "Striker", "name": "Forward 1"},
            {"pos": (18, 25), "role": "Attacking Midfielder", "name": "Midfielder 1"},
            {"pos": (18, 43), "role": "Attacking Midfielder", "name": "Midfielder 2"}
        ]
    
    # Adjust pressing positions based on intensity
    intensity_factor = pressing_intensity / 5  # Normalize to range around 1.0
    for pos in pressing_positions:
        # Move pressers closer to GK for higher intensity
        original_x = pos["pos"][0]
        original_y = pos["pos"][1]
        
        # Calculate vector from presser to GK
        vector_x = gk_pos[0] - original_x
        vector_y = gk_pos[1] - original_y
        
        # Adjust position based on intensity
        adjusted_x = original_x + (vector_x * (intensity_factor - 1) * 0.5)
        adjusted_y = original_y + (vector_y * (intensity_factor - 1) * 0.5)
        
        pos["pos"] = (adjusted_x, adjusted_y)
    
    # Add opposition pressers
    for pos in pressing_positions:
        pitch_fig.add_trace(go.Scatter(
            x=[pos["pos"][0]],
            y=[pos["pos"][1]],
            mode='markers+text',
            marker=dict(
                color='red',
                size=12,
                symbol='x',
                line=dict(color='white', width=1)
            ),
            text=f"{pos['role']}",
            textposition="top center",
            name=f"Opposition {pos['role']}"
        ))
        
        # Add pressing movement arrows
        pitch_fig.add_trace(go.Scatter(
            x=[pos["pos"][0], gk_pos[0] - 2],  # End slightly before GK
            y=[pos["pos"][1], gk_pos[1] + (pos["pos"][1] - gk_pos[1]) * 0.2],  # Curve toward GK
            mode='lines',
            line=dict(
                color='rgba(255, 0, 0, 0.5)',
                width=2,
                dash='dot'
            ),
            name=f"Press from {pos['role']}"
        ))
    
    # Add distribution options based on opposition pressing
    # Short options
    short_options = []
    
    # Determine if short options are viable based on pressing intensity
    if pressing_intensity < 8:
        short_options = [
            {"pos": (15, 25), "role": "Left Center Back", "name": "Defender 1", "viability": "high" if pressing_intensity < 6 else "medium"},
            {"pos": (15, 43), "role": "Right Center Back", "name": "Defender 2", "viability": "high" if pressing_intensity < 6 else "medium"}
        ]
        
        # Add full backs if not heavily pressed
        if not any(p["role"] in ["Left Midfielder", "Right Midfielder"] for p in pressing_positions) or pressing_intensity < 5:
            short_options.extend([
                {"pos": (20, 15), "role": "Left Full Back", "name": "Defender 3", "viability": "medium"},
                {"pos": (20, 53), "role": "Right Full Back", "name": "Defender 4", "viability": "medium"}
            ])
    
    # Medium options
    medium_options = [
        {"pos": (35, 25), "role": "Left Midfielder", "name": "Midfielder 1", "viability": "medium" if pressing_intensity < 7 else "low"},
        {"pos": (35, 43), "role": "Right Midfielder", "name": "Midfielder 2", "viability": "medium" if pressing_intensity < 7 else "low"}
    ]
    
    # Long options (always viable but with varying success rates)
    long_options = [
        {"pos": (60, 15), "role": "Left Winger", "name": "Forward 1", "viability": "medium" if pressing_intensity > 6 else "low"},
        {"pos": (60, 34), "role": "Striker", "name": "Forward 2", "viability": "medium" if pressing_intensity > 6 else "low"},
        {"pos": (60, 53), "role": "Right Winger", "name": "Forward 3", "viability": "medium" if pressing_intensity > 6 else "low"}
    ]
    
    # Combine all options
    distribution_options = short_options + medium_options + long_options
    
    # Add distribution options to visualization
    for option in distribution_options:
        # Determine color based on viability
        if option["viability"] == "high":
            color = 'rgba(0, 255, 0, 0.8)'  # Green for high viability
        elif option["viability"] == "medium":
            color = 'rgba(255, 255, 0, 0.8)'  # Yellow for medium viability
        else:
            color = 'rgba(255, 165, 0, 0.8)'  # Orange for low viability
        
        # Determine line style based on distance
        if option in short_options:
            dash = None
            width = 3
        elif option in medium_options:
            dash = 'dot'
            width = 2
        else:  # long
            dash = 'dash'
            width = 2
        
        # Add player position
        pitch_fig.add_trace(go.Scatter(
            x=[option["pos"][0]],
            y=[option["pos"][1]],
            mode='markers+text',
            marker=dict(
                color='blue',
                size=12,
                symbol='circle',
                line=dict(color='white', width=1)
            ),
            text=f"{option['role']}",
            textposition="top center",
            name=f"{option['role']} ({option['viability']} viability)"
        ))
        
        # Add passing line
        pitch_fig.add_trace(go.Scatter(
            x=[gk_pos[0], option["pos"][0]],
            y=[gk_pos[1], option["pos"][1]],
            mode='lines',
            line=dict(
                color=color,
                width=width,
                dash=dash
            ),
            name=f"Pass to {option['role']}"
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
    
    # Opposition pressing analysis
    st.markdown("### Opposition Pressing Analysis")
    
    # Create columns for metrics
    col1_metrics, col2_metrics, col3_metrics = st.columns(3)
    
    with col1_metrics:
        # Calculate pressing intensity metrics
        st.metric(
            "Pressing Intensity",
            f"{pressing_intensity}/10",
            delta=f"{pressing_intensity - 5}" if pressing_intensity != 5 else None
        )
    
    with col2_metrics:
        # Calculate pressing success rate based on intensity
        pressing_success = 0.4 + (pressing_intensity * 0.05)
        pressing_success = min(0.85, pressing_success)  # Cap at 85%
        
        st.metric(
            "Pressing Success Rate",
            f"{pressing_success:.0%}",
            delta=f"{(pressing_success - 0.65):.0%}" if pressing_success != 0.65 else None
        )
    
    with col3_metrics:
        # Calculate pressing recovery zone
        if pressing_intensity > 7:
            recovery_zone = "Final Third"
        elif pressing_intensity > 4:
            recovery_zone = "Middle Third"
        else:
            recovery_zone = "Defensive Third"
        
        st.metric(
            "Ball Recovery Zone",
            recovery_zone
        )
    
    # Pressing triggers analysis
    st.markdown("### Pressing Triggers")
    
    # Display pressing triggers with explanations
    for trigger in pressing_triggers:
        if trigger == "Back Pass to GK":
            st.markdown(f"- **{trigger}**: Opposition forwards immediately press goalkeeper when receiving back passes")
        elif trigger == "Horizontal Pass Between CBs":
            st.markdown(f"- **{trigger}**: Opposition initiates press when center backs exchange horizontal passes")
        elif trigger == "First Touch Control":
            st.markdown(f"- **{trigger}**: Opposition times press to coincide with goalkeeper's first touch")
        elif trigger == "GK Receives Under Pressure":
            st.markdown(f"- **{trigger}**: Opposition increases pressing intensity when goalkeeper is already under pressure")
        elif trigger == "Slow Build-up":
            st.markdown(f"- **{trigger}**: Opposition presses when build-up pace is slow or hesitant")
    
    # Distribution recommendations
    st.markdown("### Distribution Recommendations")
    
    # Generate recommendations based on analysis
    recommendations = []
    
    # Recommendations based on pressing intensity
    if pressing_intensity > 7:
        recommendations.append(f"**Avoid Short Build-up**: {opposition_team}'s high-intensity press makes short distribution risky")
        recommendations.append(f"**Target Wide Areas**: Utilize full backs in wider positions to evade central pressing")
        recommendations.append(f"**Long Distribution**: Consider direct distribution to bypass pressing lines")
    elif pressing_intensity > 4:
        recommendations.append(f"**Mixed Distribution Approach**: Balance short and long options based on pressing cues")
        recommendations.append(f"**Quick Circulation**: Increase tempo of build-up play to prevent press from setting")
        recommendations.append(f"**Target Defensive Midfielder**: Use central options when striker press is bypassed")
    else:
        recommendations.append(f"**Controlled Build-up**: {opposition_team}'s low pressing intensity allows for methodical build-up")
        recommendations.append(f"**Center Back Focus**: Prioritize distribution to center backs for controlled progression")
        recommendations.append(f"**Positional Superiority**: Create numerical advantages in build-up phase")
    
    # Recommendations based on pressing triggers
    if "
(Content truncated due to size limit. Use line ranges to read in chunks)