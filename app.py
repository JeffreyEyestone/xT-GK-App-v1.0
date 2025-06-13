import streamlit as st
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from data_loader import StatsBombDataLoader
from visualizations import create_pitch, create_radar_chart

# Set page configuration
st.set_page_config(
    page_title="xT-GK Analysis | Interactive Templates",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data loader
@st.cache_resource
def load_data():
    data_loader = StatsBombDataLoader()
    return data_loader

data_loader = load_data()

# Main page content
st.title("xT-GK: Expected Threat for Goalkeepers")
st.subheader("Interactive Analysis Templates")

st.markdown("""
Welcome to the xT-GK Analysis Platform. This interactive tool provides comprehensive templates for analyzing goalkeeper distribution using the Expected Threat for Goalkeepers (xT-GK) framework.

The analysis is powered by real La Liga data from the StatsBomb Open Data project, providing authentic insights into goalkeeper distribution patterns and decision-making.

### What is xT-GK?

xT-GK is a revolutionary framework for properly valuing goalkeeper distribution in the modern game. It extends the Expected Threat (xT) model to specifically evaluate goalkeeper actions, considering:

- Distribution Value (DV): The value created through pass selection and execution
- Pressure Escape Value (PEV): The value of successfully playing through opposition pressure
- Build-up Contribution (BC): The goalkeeper's contribution to sustained possession sequences
- Risk-Adjusted Value (RAV): Accounting for the risk context of each decision

### How to Use This Tool

Select an analysis template from the sidebar to explore different aspects of goalkeeper distribution:

1. **In-Game Decision Making**: Optimize distribution choices based on game state and pressure scenarios
2. **Opposition Analysis (Our GK)**: Prepare your goalkeeper for upcoming opponents
3. **Opposition Analysis (Their GK)**: Exploit opposition goalkeeper tendencies
4. **Team Coordination**: Optimize outfield player positioning for distribution
5. **Training Development**: Design targeted training programs for distribution skills
6. **Goalkeeper Scouting**: Evaluate distribution profiles for recruitment

Each template provides interactive controls and visualizations to help you apply xT-GK principles to your specific context.
""")

# Display data overview
st.header("Data Overview")

# Get sample data
sample_data = data_loader.get_sample_data()
gk_data = sample_data['goalkeeper_data']
match_info = sample_data['match_info']

# Convert to DataFrame for display
import pandas as pd
gk_df = pd.DataFrame(gk_data)
match_df = pd.DataFrame(match_info)

# Display match information
st.subheader("Sample Matches")
st.dataframe(match_df[['match_id', 'home_team', 'away_team', 'competition', 'season']], use_container_width=True)

# Display goalkeeper data
st.subheader("Goalkeeper Distribution Data")
if not gk_df.empty:
    # Select columns to display
    display_cols = ['player_name', 'team_name', 'total_passes', 'success_rate', 
                    'short_pass_pct', 'long_pass_pct', 'pressure_pct']
    
    # Format percentages
    for col in ['success_rate', 'short_pass_pct', 'long_pass_pct', 'pressure_pct']:
        if col in gk_df.columns:
            gk_df[col] = gk_df[col].apply(lambda x: f"{x:.1%}")
    
    st.dataframe(gk_df[display_cols], use_container_width=True)
else:
    st.warning("No goalkeeper data available. Please check the data source.")

# Footer
st.markdown("---")
st.markdown("""
**Created by:** Jeffrey Eyestone | **Email:** j@eyestone.us | **Phone:** +1 (720) 625-2425

This application uses the StatsBomb Open Data for analysis. All visualizations and metrics are based on the xT-GK framework.
""")
