import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.data_loader import StatsBombDataLoader
from utils.visualizations import create_pitch, plot_goalkeeper_distribution
from utils.pdf_generator import generate_in_game_decision_pdf

st.set_page_config(
    page_title="In-Game Decision Making",
    page_icon="🧠",
    layout="wide"
)

# Load data
def load_data():
    data_loader = StatsBombDataLoader()
    return data_loader

data_loader = load_data()

# Page title
st.title("In-Game Decision Making")
st.markdown("Analyze goalkeeper distribution decisions during match situations")

# Match situation parameters
st.header("Match Situation")

col1, col2 = st.columns(2)

with col1:
    match_time = st.slider("Match Time (minutes)", 0, 90, 30)
    score_line = st.selectbox("Score Line", ["Winning", "Drawing", "Losing"])
    
with col2:
    pressure_level = st.slider("Opposition Pressure Level", 1, 10, 5)
    field_position = st.selectbox("Field Position", ["Own Box", "Edge of Box", "Middle Third"])

# Distribution options
st.header("Distribution Options")

# Sample data for demonstration
distribution_options = {
    "Short Pass to Center Back": 0.85,
    "Medium Pass to Full Back": 0.75,
    "Long Pass to Striker": 0.45,
    "Medium Pass to Midfielder": 0.65,
    "Long Pass to Winger": 0.55
}

# Display options with success probabilities
col1, col2 = st.columns(2)

with col1:
    st.subheader("Available Options")
    for option, probability in distribution_options.items():
        st.metric(option, f"{probability*100:.0f}% Success Rate")

with col2:
    st.subheader("Visualization")
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
    
    # Add goalkeeper
    fig.add_trace(go.Scatter(
        x=[positions["GK"][0]],
        y=[positions["GK"][1]],
        mode='markers',
        marker=dict(size=15, color='cyan'),
        name='Goalkeeper'
    ))
    
    # Add outfield players
    for position, (x, y) in positions.items():
        if position != "GK":
            fig.add_trace(go.Scatter(
                x=[x],
                y=[y],
                mode='markers',
                marker=dict(size=12, color='blue'),
                name=position
            ))
    
    # Add distribution lines
    for i, (option, probability) in enumerate(distribution_options.items()):
        target = ""
        if "Center Back" in option:
            target = "RCB" if i % 2 == 0 else "LCB"
        elif "Full Back" in option:
            target = "RB" if i % 2 == 0 else "LB"
        elif "Striker" in option:
            target = "ST"
        elif "Midfielder" in option:
            target = "CDM" if i % 2 == 0 else "CAM"
        elif "Winger" in option:
            target = "RM" if i % 2 == 0 else "LM"
        
        if target:
            fig.add_trace(go.Scatter(
                x=[positions["GK"][0], positions[target][0]],
                y=[positions["GK"][1], positions[target][1]],
                mode='lines',
                line=dict(width=probability*5, color='rgba(255, 255, 255, 0.7)'),
                name=option
            ))
    
    st.plotly_chart(fig, use_container_width=True)

# Decision analysis
st.header("Decision Analysis")

selected_option = st.selectbox("Select Distribution Option", list(distribution_options.keys()))

# Calculate xT values based on selected option
if selected_option:
    base_xt = distribution_options[selected_option]
    
    # Adjust for match situation
    if score_line == "Winning":
        situation_factor = 0.9  # Lower risk when winning
    elif score_line == "Losing":
        situation_factor = 1.2  # Higher risk when losing
    else:
        situation_factor = 1.0  # Neutral when drawing
        
    # Adjust for pressure
    pressure_factor = 1.0 - (pressure_level - 1) / 20  # Higher pressure reduces success
    
    # Calculate final xT
    adjusted_xt = base_xt * situation_factor * pressure_factor
    
    # Display analysis
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Base Success Rate", f"{base_xt*100:.1f}%")
    
    with col2:
        st.metric("Adjusted for Match Situation", f"{base_xt*situation_factor*100:.1f}%", 
                 f"{(situation_factor-1)*100:.1f}%" if situation_factor != 1.0 else "0%")
    
    with col3:
        st.metric("Final Success Rate", f"{adjusted_xt*100:.1f}%", 
                 f"{(adjusted_xt-base_xt)*100:.1f}%")
    
    # Recommendation
    st.subheader("Recommendation")
    
    if adjusted_xt > 0.7:
        recommendation = f"**Highly Recommended**: {selected_option} is a safe option with high probability of success."
        recommendation_color = "green"
    elif adjusted_xt > 0.5:
        recommendation = f"**Consider**: {selected_option} has moderate risk but could be effective."
        recommendation_color = "orange"
    else:
        recommendation = f"**Caution**: {selected_option} has high risk in the current match situation."
        recommendation_color = "red"
    
    st.markdown(f"<div style='background-color:{recommendation_color}; padding:10px; border-radius:5px; color:white;'>{recommendation}</div>", unsafe_allow_html=True)

# Generate PDF report
st.header("Generate Report")

if st.button("Generate PDF Report"):
    # Prepare report content
    title = f"In-Game Decision Analysis - {match_time}' ({score_line})"
    
    content = f"""
    # In-Game Decision Analysis
    
    ## Match Situation
    - **Match Time**: {match_time} minutes
    - **Score Line**: {score_line}
    - **Opposition Pressure**: {pressure_level}/10
    - **Field Position**: {field_position}
    
    ## Distribution Options Analysis
    
    | Option | Base Success Rate | Adjusted Success Rate |
    |--------|-------------------|----------------------|
    """
    
    for option, probability in distribution_options.items():
        situation_factor = 0.9 if score_line == "Winning" else 1.2 if score_line == "Losing" else 1.0
        pressure_factor = 1.0 - (pressure_level - 1) / 20
        adjusted = probability * situation_factor * pressure_factor
        content += f"| {option} | {probability*100:.1f}% | {adjusted*100:.1f}% |\n"
    
    content += f"""
    ## Recommendation
    
    The recommended distribution option is **{selected_option}** with an adjusted success rate of {adjusted_xt*100:.1f}%.
    """
    
    # Generate PDF
    pdf_data = generate_in_game_decision_pdf(
        title=title,
        content=content,
        figures=[fig],
        metadata={
            "Match Time": f"{match_time} minutes",
            "Score Line": score_line,
            "Pressure Level": f"{pressure_level}/10",
            "Field Position": field_position
        }
    )
    
    # Provide download link
    st.download_button(
        label="Download PDF Report",
        data=pdf_data,
        file_name="in_game_decision_analysis.pdf",
        mime="application/pdf"
    )
