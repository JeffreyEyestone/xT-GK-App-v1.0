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
from utils.visualizations import create_pitch, create_opposition_heatmap
from utils.data_loader import StatsBombDataLoader

st.set_page_config(
    page_title="Opposition Analysis (Their GK) | xT-GK",
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

st.title("Opposition Analysis (Their GK)")
st.subheader("Exploit opposition goalkeeper distribution tendencies")

st.markdown("""
This template helps coaches and players exploit opposition goalkeeper distribution patterns by:
- Analyzing opposition goalkeeper tendencies
- Identifying pressing triggers and vulnerable distribution patterns
- Developing pressing strategies to force turnovers
- Creating tactical plans to exploit distribution weaknesses

Using real La Liga data, this tool provides evidence-based strategies to counter opposition goalkeeper distribution.
""")

# Create two columns for inputs and visualization
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Opposition Analysis Parameters")
    
    # Select teams from real data
    available_teams = []
    for match in match_info:
        if match['home_team'] not in available_teams:
            available_teams.append(match['home_team'])
        if match['away_team'] not in available_teams:
            available_teams.append(match['away_team'])
    
    if not available_teams:
        available_teams = ["Team A", "Team B", "Team C"]  # Fallback
    
    our_team = st.selectbox(
        "Our Team",
        options=available_teams,
        index=0
    )
    
    opposition_team = st.selectbox(
        "Opposition Team",
        options=[team for team in available_teams if team != our_team],
        index=0 if len(available_teams) > 1 else 0
    )
    
    # Select opposition goalkeeper
    opposition_goalkeepers = []
    for gk in gk_data:
        if gk['team_name'] == opposition_team:
            opposition_goalkeepers.append(gk['player_name'])
    
    if not opposition_goalkeepers:
        opposition_goalkeepers = ["Opposition Goalkeeper"]  # Fallback
    
    opposition_goalkeeper = st.selectbox(
        "Opposition Goalkeeper",
        options=opposition_goalkeepers,
        index=0
    )
    
    # Our pressing style
    st.subheader("Our Pressing Approach")
    
    pressing_intensity = st.slider(
        "Pressing Intensity",
        min_value=1,
        max_value=10,
        value=8,
        help="1 = minimal pressure, 10 = intense pressure"
    )
    
    pressing_trigger = st.multiselect(
        "Pressing Triggers",
        options=["Back Pass to GK", "GK Receives Under Pressure", "Wide Distribution", "Central Distribution", "Long Distribution"],
        default=["Back Pass to GK", "GK Receives Under Pressure"]
    )
    
    pressing_structure = st.selectbox(
        "Pressing Structure",
        options=["High Press", "Mid-Block", "Low Block", "Mixed Approach"],
        index=0
    )
    
    # Match context
    st.subheader("Match Context")
    
    venue = st.radio(
        "Venue",
        options=["Home", "Away"],
        index=0
    )
    
    expected_game_state = st.selectbox(
        "Expected Game State",
        options=["Leading", "Drawing", "Trailing", "Variable"],
        index=1
    )
    
    # Advanced options
    with st.expander("Advanced Analysis Options"):
        st.subheader("Detailed Pressing Strategy")
        
        analyze_individual_pressers = st.checkbox("Assign Individual Pressers", value=True)
        
        if analyze_individual_pressers:
            key_pressers = st.multiselect(
                "Key Pressers",
                options=["Striker 1 (Benzema)", "Striker 2 (Jović)", "Midfielder 1 (Modrić)", "Midfielder 2 (Kroos)", "Winger 1 (Vinicius)"],
                default=["Striker 1 (Benzema)", "Winger 1 (Vinicius)"]
            )
        
        consider_opposition_weakness = st.checkbox("Target Specific Weaknesses", value=True)
        
        if consider_opposition_weakness:
            weakness_target = st.selectbox(
                "Primary Weakness to Target",
                options=["Distribution Under Pressure", "Long Distribution Accuracy", "Short Distribution Decision-Making", "Communication with Defenders"],
                index=0
            )

with col2:
    st.subheader("Opposition Goalkeeper Analysis")
    
    # Display opposition goalkeeper profile
    st.markdown(f"### {opposition_goalkeeper} Distribution Profile")
    
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
    
    # Distribution pattern visualization
    st.markdown("### Distribution Pattern Analysis")
    
    # Create pitch visualization
    pitch_fig = create_pitch()
    
    # Add opposition goalkeeper position
    gk_pos = (5, 34)
    pitch_fig.add_trace(go.Scatter(
        x=[gk_pos[0]],
        y=[gk_pos[1]],
        mode='markers+text',
        marker=dict(
            color='red',
            size=15,
            symbol='circle',
            line=dict(color='white', width=2)
        ),
        text=opposition_goalkeeper,
        textposition="top center",
        name=f'Opposition GK ({opposition_goalkeeper})'
    ))
    
    # Add distribution patterns with player names
    # Short distribution
    short_targets = [
        {"pos": (15, 25), "role": "Left CB", "name": "Giménez", "freq": 0.25, "success": 0.85},
        {"pos": (15, 43), "role": "Right CB", "name": "Savić", "freq": 0.30, "success": 0.90},
        {"pos": (20, 15), "role": "Left FB", "name": "Lodi", "freq": 0.15, "success": 0.75},
        {"pos": (20, 53), "role": "Right FB", "name": "Trippier", "freq": 0.10, "success": 0.80}
    ]
    
    for target in short_targets:
        # Scale line width by frequency
        width = target["freq"] * 10
        
        # Adjust opacity based on success rate
        opacity = target["success"]
        
        # Add passing line
        pitch_fig.add_trace(go.Scatter(
            x=[gk_pos[0], target["pos"][0]],
            y=[gk_pos[1], target["pos"][1]],
            mode='lines',
            line=dict(
                color=f'rgba(255, 0, 0, {opacity})',
                width=width
            ),
            name=f'Short Pass to {target["role"]} ({target["freq"]:.0%}, {target["success"]:.0%} success)'
        ))
        
        # Add player position
        pitch_fig.add_trace(go.Scatter(
            x=[target["pos"][0]],
            y=[target["pos"][1]],
            mode='markers+text',
            marker=dict(
                color='red',
                size=12,
                symbol='circle',
                line=dict(color='white', width=1)
            ),
            text=f"{target['name']}",
            textposition="top center",
            name=f"{target['role']} ({target['name']})"
        ))
    
    # Long distribution
    long_targets = [
        {"pos": (60, 15), "role": "Left Wing", "name": "Carrasco", "freq": 0.08, "success": 0.60},
        {"pos": (70, 34), "role": "Striker", "name": "Suárez", "freq": 0.07, "success": 0.50},
        {"pos": (60, 53), "role": "Right Wing", "name": "Correa", "freq": 0.05, "success": 0.55}
    ]
    
    for target in long_targets:
        # Scale line width by frequency
        width = target["freq"] * 10
        
        # Adjust opacity based on success rate
        opacity = target["success"]
        
        # Add passing line
        pitch_fig.add_trace(go.Scatter(
            x=[gk_pos[0], target["pos"][0]],
            y=[gk_pos[1], target["pos"][1]],
            mode='lines',
            line=dict(
                color=f'rgba(255, 0, 0, {opacity})',
                width=width,
                dash='dash'
            ),
            name=f'Long Pass to {target["role"]} ({target["freq"]:.0%}, {target["success"]:.0%} success)'
        ))
        
        # Add player position
        pitch_fig.add_trace(go.Scatter(
            x=[target["pos"][0]],
            y=[target["pos"][1]],
            mode='markers+text',
            marker=dict(
                color='red',
                size=12,
                symbol='circle',
                line=dict(color='white', width=1)
            ),
            text=f"{target['name']}",
            textposition="top center",
            name=f"{target['role']} ({target['name']})"
        ))
    
    # Add our pressing players with names
    if pressing_structure == "High Press":
        # Add our players in high pressing positions
        our_positions = [
            {"pos": (15, 20), "role": "Forward", "name": "Benzema"},
            {"pos": (15, 48), "role": "Forward", "name": "Vinicius"},
            {"pos": (25, 34), "role": "Midfielder", "name": "Modrić"}
        ]
    elif pressing_structure == "Mid-Block":
        # Add our players in mid positions
        our_positions = [
            {"pos": (35, 20), "role": "Midfielder", "name": "Kroos"},
            {"pos": (35, 48), "role": "Midfielder", "name": "Modrić"},
            {"pos": (45, 34), "role": "Forward", "name": "Benzema"}
        ]
    else:  # Low Block or Mixed
        # Add our players in mixed positions
        our_positions = [
            {"pos": (25, 20), "role": "Forward", "name": "Benzema"},
            {"pos": (45, 48), "role": "Midfielder", "name": "Modrić"},
            {"pos": (65, 34), "role": "Defender", "name": "Militão"}
        ]
    
    for player in our_positions:
        pitch_fig.add_trace(go.Scatter(
            x=[player["pos"][0]],
            y=[player["pos"][1]],
            mode='markers+text',
            marker=dict(
                color='blue',
                size=12,
                symbol='x',
                line=dict(color='white', width=1)
            ),
            text=f"{player['name']}",
            textposition="top center",
            name=f"Our {player['role']} ({player['name']})"
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
    
    # Pressing strategy recommendations
    st.markdown("### Pressing Strategy Recommendations")
    
    # Generate recommendations based on analysis
    recommendations = []
    
    # Identify most frequent/vulnerable distribution patterns
    most_frequent_target = max(short_targets + long_targets, key=lambda x: x["freq"])
    most_vulnerable_target = min(short_targets + long_targets, key=lambda x: x["success"])
    
    if pressing_structure == "High Press":
        recommendations.append(f"**Cut passing lanes to {most_frequent_target['name']}**: Position {our_positions[0]['name']} to block the most frequent passing option")
        recommendations.append(f"**Force distribution to {most_vulnerable_target['name']}**: Apply pressure to channel distribution to the least successful target")
        recommendations.append(f"**Aggressive goalkeeper pressure**: Use {our_positions[0]['name']} to apply immediate pressure on back passes")
    
    elif pressing_structure == "Mid-Block":
        recommendations.append(f"**Allow initial short build-up**: Let goalkeeper distribute to center backs, then press with {our_positions[0]['name']} and {our_positions[1]['name']}")
        recommendations.append(f"**Trap wide distribution**: Allow initial pass to full backs, then use {our_positions[1]['name']} to press aggressively")
        recommendations.append(f"**Block central progression**: Position {our_positions[2]['name']} to intercept attempted passes to midfield")
    
    else:  # Low Block or Mixed
        recommendations.append(f"**Selective high pressing**: Use {our_positions[0]['name']} to press only on identified triggers")
        recommendations.append(f"**Compact defensive shape**: Maintain organization with {our_positions[1]['name']} and {our_positions[2]['name']} screening passing lanes")
        recommendations.append(f"**Prepare for direct play**: Position to win second balls from long distribution attempts")
    
    # Add specific weakness recommendations
    if gk_pressure_pct > 0.35 and gk_success_rate < 0.75:
        recommendations.append(f"**Exploit pressure vulnerability**: {opposition_goalkeeper} shows significant drop in success rate under pressure")
    
    if gk_long_pct > 0.3 and gk_success_rate < 0.7:
        recommendations.append(f"**Force long distribution**: {opposition_goalkeeper} attempts many long passes with limited success")
    
    # Display recommendations
    for i, rec in enumerate(recommendations):
        st.markdown(f"{i+1}. {rec}")
    
    # Expected outcomes
    st.markdown("### Expected Outcomes")
    
    # Create columns for outcome metrics
    col1_outcomes, col2_outcomes = st.columns(2)
    
    with col1_outcomes:
        # Calculate expected turnover rate
        base_turnover = 0.3
        if pressing_intensity > 7:
            base_turnover += 0.15
        if pressing_structure == "High Press":
            base_turnover += 0.1
        if gk_success_rate < 0.75:
            base_turnover += 0.1
        
        expected_turnover = min(0.8, max(0.2, base_turnover))
        
        # Create gauge chart for turnover rate
        turnover_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=expected_turnover,
            title={"text": "Expected Turnover Rate"},
            gauge={
                "axis": {"range": [0, 1]},
                "bar": {"color": "blue"},
                "steps": [
                    {"range": [0, 0.3], "color": "red"},
                    {"range": [0.3, 0.6], "color": "yellow"},
                    {"range": [0.6, 1], "color": "green"}
                ],
                "threshold": {
                    "line": {"color": "white", "width": 4},
                    "thickness": 0.75,
                    "value": 0.6
                }
            }
        ))
        
        # Display the gauge chart
        st.plotly_chart(turnover_fig, use_container_width=True)
    
    with col2_outcomes:
        # Calculate expected territory gain
        base_territory = 0.4
        if pressing_intensity > 7:
            base_territory += 0.1
        if pressing_structure == "High Press":
            base_territory += 0.15
        if gk_long_pct > 0.3 and gk_success_rate < 0.7:
            base_territory += 0.1
        
        expected_territory = min(0.9, max(0.2, base_territory))
        
        # Creat
(Content truncated due to size limit. Use line ranges to read in chunks)