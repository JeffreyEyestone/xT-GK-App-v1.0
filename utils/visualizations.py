import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_pitch(width=700, height=500, pitch_color='#1e3a5f', line_color='white'):
    """
    Create a football pitch visualization using Plotly
    
    Args:
        width: Width of the pitch in pixels
        height: Height of the pitch in pixels
        pitch_color: Background color of the pitch
        line_color: Color of the pitch lines
        
    Returns:
        Plotly figure object with pitch
    """
    # Create figure
    fig = go.Figure()
    
    # Set pitch dimensions (standard pitch is 105x68 meters)
    pitch_length = 105
    pitch_width = 68
    
    # Add pitch outline
    fig.add_shape(
        type="rect", x0=0, y0=0, x1=pitch_length, y1=pitch_width,
        line=dict(color=line_color, width=2),
        fillcolor=pitch_color,
    )
    
    # Add center line
    fig.add_shape(
        type="line", x0=pitch_length/2, y0=0, x1=pitch_length/2, y1=pitch_width,
        line=dict(color=line_color, width=2)
    )
    
    # Add center circle
    fig.add_shape(
        type="circle", x0=pitch_length/2-9.15, y0=pitch_width/2-9.15, 
        x1=pitch_length/2+9.15, y1=pitch_width/2+9.15,
        line=dict(color=line_color, width=2),
        fillcolor=pitch_color,
    )
    
    # Add penalty areas
    # Left penalty area
    fig.add_shape(
        type="rect", x0=0, y0=pitch_width/2-20.16, x1=16.5, y1=pitch_width/2+20.16,
        line=dict(color=line_color, width=2),
        fillcolor=pitch_color,
    )
    
    # Right penalty area
    fig.add_shape(
        type="rect", x0=pitch_length-16.5, y0=pitch_width/2-20.16, 
        x1=pitch_length, y1=pitch_width/2+20.16,
        line=dict(color=line_color, width=2),
        fillcolor=pitch_color,
    )
    
    # Add goal areas
    # Left goal area
    fig.add_shape(
        type="rect", x0=0, y0=pitch_width/2-9.16, x1=5.5, y1=pitch_width/2+9.16,
        line=dict(color=line_color, width=2),
        fillcolor=pitch_color,
    )
    
    # Right goal area
    fig.add_shape(
        type="rect", x0=pitch_length-5.5, y0=pitch_width/2-9.16, 
        x1=pitch_length, y1=pitch_width/2+9.16,
        line=dict(color=line_color, width=2),
        fillcolor=pitch_color,
    )
    
    # Add penalty spots
    fig.add_trace(go.Scatter(
        x=[11, pitch_length-11],
        y=[pitch_width/2, pitch_width/2],
        mode='markers',
        marker=dict(color=line_color, size=8),
        showlegend=False
    ))
    
    # Add goals
    # Left goal
    fig.add_shape(
        type="rect", x0=-2, y0=pitch_width/2-3.66, x1=0, y1=pitch_width/2+3.66,
        line=dict(color=line_color, width=2),
        fillcolor='rgba(0,0,0,0.1)',
    )
    
    # Right goal
    fig.add_shape(
        type="rect", x0=pitch_length, y0=pitch_width/2-3.66, 
        x1=pitch_length+2, y1=pitch_width/2+3.66,
        line=dict(color=line_color, width=2),
        fillcolor='rgba(0,0,0,0.1)',
    )
    
    # Update layout
    fig.update_layout(
        width=width,
        height=height,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(
            range=[-5, pitch_length+5],
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        yaxis=dict(
            range=[-5, pitch_width+5],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            scaleanchor="x",
            scaleratio=1
        ),
        showlegend=True,  # Ensure legend is visible
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def plot_pressure_heatmap(fig, pressure_level, goalkeeper_position=(5, 34)):
    """
    Add a pressure heatmap to the pitch visualization
    
    Args:
        fig: Plotly figure with pitch
        pressure_level: Intensity of pressure (1-10)
        goalkeeper_position: (x, y) coordinates of goalkeeper
        
    Returns:
        Updated Plotly figure
    """
    # Create a grid of points
    x = np.linspace(0, 105, 50)
    y = np.linspace(0, 68, 30)
    X, Y = np.meshgrid(x, y)
    
    # Calculate pressure intensity based on distance from opponents
    # Simulate opponent positions based on pressure level
    if pressure_level <= 3:
        # Low pressure - opponents far away
        opponent_positions = [(25, 34), (30, 20), (30, 48)]
        opponent_roles = ["Forward", "Winger", "Winger"]
    elif pressure_level <= 7:
        # Medium pressure - opponents closer
        opponent_positions = [(15, 34), (20, 20), (20, 48)]
        opponent_roles = ["Forward", "Winger", "Winger"]
    else:
        # High pressure - opponents very close
        opponent_positions = [(8, 34), (12, 20), (12, 48)]
        opponent_roles = ["Forward", "Winger", "Winger"]
    
    # Calculate pressure intensity at each point
    Z = np.zeros_like(X)
    for op_x, op_y in opponent_positions:
        # Distance from opponent to each point
        distance = np.sqrt((X - op_x)**2 + (Y - op_y)**2)
        # Pressure intensity decreases with distance
        intensity = pressure_level * np.exp(-0.05 * distance)
        Z += intensity
    
    # Normalize Z values
    Z = Z / Z.max()
    
    # Add heatmap to figure
    fig.add_trace(go.Contour(
        z=Z,
        x=x,
        y=y,
        colorscale='Hot_r',
        opacity=0.7,
        showscale=False,
        contours=dict(
            start=0,
            end=1,
            size=0.1,
        ),
        name="Pressure Intensity"
    ))
    
    # Add goalkeeper position
    fig.add_trace(go.Scatter(
        x=[goalkeeper_position[0]],
        y=[goalkeeper_position[1]],
        mode='markers+text',
        marker=dict(
            color='cyan',
            size=15,
            symbol='circle',
            line=dict(color='white', width=2)
        ),
        text="GK",
        textposition="top center",
        name='Goalkeeper'
    ))
    
    # Add opponent positions with roles
    for i, (pos, role) in enumerate(zip(opponent_positions, opponent_roles)):
        fig.add_trace(go.Scatter(
            x=[pos[0]],
            y=[pos[1]],
            mode='markers+text',
            marker=dict(
                color='red',
                size=12,
                symbol='x',
                line=dict(color='white', width=1)
            ),
            text=role,
            textposition="top center",
            name=f'Opposition {role}'
        ))
    
    return fig

def plot_distribution_options(fig, options, goalkeeper_position=(5, 34)):
    """
    Add distribution options to the pitch visualization
    
    Args:
        fig: Plotly figure with pitch
        options: List of distribution options with target positions and values
        goalkeeper_position: (x, y) coordinates of goalkeeper
        
    Returns:
        Updated Plotly figure
    """
    # Define target positions (these would normally come from the options)
    target_positions = {
        "Center-Back": (15, 34),
        "Full-Back": (20, 10),
        "Defensive Midfielder": (30, 34),
        "Winger": (40, 10),
        "Striker": (60, 34)
    }
    
    # Add passing lines and targets
    for option in options:
        target = option["target"]
        if target in target_positions:
            target_pos = target_positions[target]
            
            # Calculate color based on risk-adjusted value
            value = option["risk_adj_value"]
            # Color scale from red (low value) to green (high value)
            r = max(0, min(255, int(255 * (1 - value))))
            g = max(0, min(255, int(255 * value)))
            color = f'rgb({r},{g},0)'
            
            # Add passing line
            fig.add_trace(go.Scatter(
                x=[goalkeeper_position[0], target_pos[0]],
                y=[goalkeeper_position[1], target_pos[1]],
                mode='lines',
                line=dict(
                    color=color,
                    width=3,
                    dash='solid' if value > 0.5 else 'dash'
                ),
                name=f'{target} (xT-GK: {value:.2f})'
            ))
            
            # Add target position
            fig.add_trace(go.Scatter(
                x=[target_pos[0]],
                y=[target_pos[1]],
                mode='markers+text',
                marker=dict(
                    color=color,
                    size=12,
                    symbol='circle',
                    line=dict(color='white', width=1)
                ),
                text=target,
                textposition="top center",
                name=target
            ))
    
    return fig

def create_opposition_heatmap(pressing_data):
    """
    Create a heatmap of opposition pressing intensity
    
    Args:
        pressing_data: DataFrame with pressing data
        
    Returns:
        Plotly figure with heatmap
    """
    # Create pitch
    fig = create_pitch()
    
    # Create a grid of points
    x = np.linspace(0, 105, 50)
    y = np.linspace(0, 68, 30)
    X, Y = np.meshgrid(x, y)
    
    # Simulate pressing intensity data
    Z = np.zeros_like(X)
    
    # Add some pressing hotspots
    for i in range(len(X)):
        for j in range(len(X[0])):
            # Higher intensity in wide areas of defensive third
            if X[i][j] < 35:
                if Y[i][j] < 20 or Y[i][j] > 48:
                    Z[i][j] += 0.8
                else:
                    Z[i][j] += 0.4
            # Medium intensity in middle third
            elif X[i][j] < 70:
                Z[i][j] += 0.5
            # Lower intensity in attacking third
            else:
                Z[i][j] += 0.2
    
    # Add some random variation
    Z += np.random.rand(*Z.shape) * 0.3
    
    # Normalize Z values
    Z = Z / Z.max()
    
    # Add heatmap to figure
    fig.add_trace(go.Contour(
        z=Z,
        x=x,
        y=y,
        colorscale='Hot_r',
        opacity=0.7,
        showscale=True,
        contours=dict(
            start=0,
            end=1,
            size=0.1,
        ),
        colorbar=dict(
            title="Pressing<br>Intensity",
            titleside="right",
            titlefont=dict(size=14),
            tickvals=[0, 0.5, 1],
            ticktext=["Low", "Medium", "High"]
        ),
        name="Pressing Intensity"
    ))
    
    return fig

def create_team_coordination_diagram(formation, build_up_pattern):
    """
    Create a diagram showing team coordination for build-up play
    
    Args:
        formation: Team formation (e.g., "4-3-3")
        build_up_pattern: Build-up pattern (e.g., "Wide", "Central")
        
    Returns:
        Plotly figure with team coordination diagram
    """
    # Create pitch
    fig = create_pitch()
    
    # Goalkeeper position
    gk_pos = (5, 34)
    
    # Define player positions based on formation
    if formation == "4-3-3":
        positions = {
            "GK": gk_pos,
            "LB": (20, 10),
            "LCB": (15, 25),
            "RCB": (15, 43),
            "RB": (20, 58),
            "CDM": (30, 34),
            "LCM": (40, 20),
            "RCM": (40, 48),
            "LW": (70, 10),
            "ST": (70, 34),
            "RW": (70, 58)
        }
    elif formation == "4-4-2":
        positions = {
            "GK": gk_pos,
            "LB": (20, 10),
            "LCB": (15, 25),
            "RCB": (15, 43),
            "RB": (20, 58),
            "LM": (45, 15),
            "LCM": (40, 30),
            "RCM": (40, 38),
            "RM": (45, 53),
            "LST": (65, 25),
            "RST": (65, 43)
        }
    else:  # Default to 4-2-3-1
        positions = {
            "GK": gk_pos,
            "LB": (20, 10),
            "LCB": (15, 25),
            "RCB": (15, 43),
            "RB": (20, 58),
            "LDM": (35, 25),
            "RDM": (35, 43),
            "CAM": (50, 34),
            "LW": (60, 15),
            "ST": (65, 34),
            "RW": (60, 53)
        }
    
    # Add player positions
    for role, pos in positions.items():
        color = 'cyan' if role == 'GK' else 'blue'
        fig.add_trace(go.Scatter(
            x=[pos[0]],
            y=[pos[1]],
            mode='markers+text',
            marker=dict(
                color=color,
                size=15,
                symbol='circle',
                line=dict(color='white', width=2)
            ),
            text=role,
            textposition="top center",
            name=role
        ))
    
    # Add build-up patterns
    if build_up_pattern == "Wide":
        # GK to CBs
        fig.add_trace(go.Scatter(
            x=[positions["GK"][0], positions["LCB"][0]],
            y=[positions["GK"][1], positions["LCB"][1]],
            mode='lines+markers',
            line=dict(color='white', width=2, dash='dot'),
            marker=dict(size=0),
            showlegend=False,
            name="Secondary Build-up"
        ))
        fig.add_trace(go.Scatter(
            x=[positions["GK"][0], positions["RCB"][0]],
            y=[positions["GK"][1], positions["RCB"][1]],
            mode='lines+markers',
            line=dict(color='white', width=2, dash='dot'),
            marker=dict(size=0),
            showlegend=False
        ))
        
        # CBs to FBs
        fig.add_trace(go.Scatter(
            x=[positions["LCB"][0], positions["LB"][0]],
            y=[positions["LCB"][1], positions["LB"][1]],
            mode='lines+markers',
            line=dict(color='green', width=3),
            marker=dict(size=0),
            name="Primary Build-up"
        ))
        fig.add_trace(go.Scatter(
            x=[positions["RCB"][0], positions["RB"][0]],
            y=[positions["RCB"][1], positions["RB"][1]],
            mode='lines+markers',
            line=dict(color='green', width=3),
            marker=dict(size=0),
            showlegend=False
        ))
    else:  # Central build-up
        # GK to CBs
        fig.add_trace(go.Scatter(
            x=[positions["GK"][0], positions["LCB"][0]],
            y=[positions["GK"][1], positions["LCB"][1]],
            mode='lines+markers',
            line=dict(color='white', width=2, dash='dot'),
            marker=dict(size=0),
            showlegend=False,
            name="Secondary Build-up"
        ))
        fig.add_trace(go.Scatter(
            x=[positions["GK"][0], positions["RCB"][0]],
            y=[positions["GK"][1], positions["RCB"][1]],
            mode='lines+markers',
            line=dict(color='white', width=2, dash='dot'),
            marker=dict(size=0),
            showlegend=False
        ))
        
        # CBs to midfielders
        if "CDM" in positions:
            fig.add_trace(go.Scatter(
                x=[positions["LCB"][0], positions["CDM"][0]],
                y=[positions["LCB"][1], positions["CDM"][1]],
                mode='lines+markers',
                line=dict(color='green', width=3),
                marker=dict(size=0),
                name="Primary Build-up"
            ))
            fig.add_trace(go.Scatter(
                x=[positions["RCB"][0], positions["CDM"][0]],
                y=[positions["RCB"][1], positions["CDM"][1]],
                mode='lines+markers',
                line=dict(color='green', width=3),
                marker=dict(size=0),
                showlegend=False
            ))
        elif "LDM" in positions:
            fig.add_trace(go.Scatter(
                x=[positions["LCB"][0], positions["LDM"][0]],
                y=[positions["LCB"][1], positions["LDM"][1]],
                mode='lines+markers',
                line=dict(color='green', width=3),
                marker=dict(size=0),
                name="Primary Build-up"
            ))
            fig.add_trace(go.Scatter(
                x=[positions["RCB"][0]
(Content truncated due to size limit. Use line ranges to read in chunks)