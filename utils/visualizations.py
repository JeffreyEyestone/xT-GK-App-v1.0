import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd

def create_pitch(width=600, height=400, pitch_color='#1e3a5f', line_color='white'):
    """
    Create a football pitch visualization using Plotly
    
    Parameters:
    -----------
    width : int
        Width of the pitch in pixels
    height : int
        Height of the pitch in pixels
    pitch_color : str
        Background color of the pitch
    line_color : str
        Color of the pitch lines
    
    Returns:
    --------
    fig : plotly.graph_objects.Figure
        Plotly figure object with the pitch
    """
    fig = go.Figure()
    
    # Set pitch dimensions and scaling
    pitch_length = 105
    pitch_width = 68
    
    # Configure the pitch appearance
    fig.update_layout(
        width=width,
        height=height,
        plot_bgcolor=pitch_color,
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(
            range=[0, pitch_length],
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        yaxis=dict(
            range=[0, pitch_width],
            showgrid=False,
            zeroline=False,
            showticklabels=False
        )
    )
    
    # Draw pitch outline
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=pitch_length, y1=pitch_width,
        line=dict(color=line_color, width=2),
        fillcolor='rgba(0,0,0,0)'
    )
    
    # Draw halfway line
    fig.add_shape(
        type="line",
        x0=pitch_length/2, y0=0, x1=pitch_length/2, y1=pitch_width,
        line=dict(color=line_color, width=2)
    )
    
    # Draw center circle
    fig.add_shape(
        type="circle",
        x0=pitch_length/2-9.15, y0=pitch_width/2-9.15,
        x1=pitch_length/2+9.15, y1=pitch_width/2+9.15,
        line=dict(color=line_color, width=2),
        fillcolor='rgba(0,0,0,0)'
    )
    
    # Draw penalty areas
    # Left penalty area
    fig.add_shape(
        type="rect",
        x0=0, y0=pitch_width/2-20.16, x1=16.5, y1=pitch_width/2+20.16,
        line=dict(color=line_color, width=2),
        fillcolor='rgba(0,0,0,0)'
    )
    
    # Right penalty area
    fig.add_shape(
        type="rect",
        x0=pitch_length-16.5, y0=pitch_width/2-20.16, x1=pitch_length, y1=pitch_width/2+20.16,
        line=dict(color=line_color, width=2),
        fillcolor='rgba(0,0,0,0)'
    )
    
    # Draw goal areas
    # Left goal area
    fig.add_shape(
        type="rect",
        x0=0, y0=pitch_width/2-9.16, x1=5.5, y1=pitch_width/2+9.16,
        line=dict(color=line_color, width=2),
        fillcolor='rgba(0,0,0,0)'
    )
    
    # Right goal area
    fig.add_shape(
        type="rect",
        x0=pitch_length-5.5, y0=pitch_width/2-9.16, x1=pitch_length, y1=pitch_width/2+9.16,
        line=dict(color=line_color, width=2),
        fillcolor='rgba(0,0,0,0)'
    )
    
    # Draw penalty spots
    fig.add_shape(
        type="circle",
        x0=11-0.5, y0=pitch_width/2-0.5, x1=11+0.5, y1=pitch_width/2+0.5,
        line=dict(color=line_color, width=2),
        fillcolor=line_color
    )
    
    fig.add_shape(
        type="circle",
        x0=pitch_length-11-0.5, y0=pitch_width/2-0.5, x1=pitch_length-11+0.5, y1=pitch_width/2+0.5,
        line=dict(color=line_color, width=2),
        fillcolor=line_color
    )
    
    # Draw corner arcs
    # Top left
    fig.add_shape(
        type="path",
        path=f"M 0 {pitch_width-1} Q 1 {pitch_width} {1} {pitch_width}",
        line=dict(color=line_color, width=2)
    )
    
    # Bottom left
    fig.add_shape(
        type="path",
        path="M 0 1 Q 1 0 1 0",
        line=dict(color=line_color, width=2)
    )
    
    # Top right
    fig.add_shape(
        type="path",
        path=f"M {pitch_length} {pitch_width-1} Q {pitch_length-1} {pitch_width} {pitch_length-1} {pitch_width}",
        line=dict(color=line_color, width=2)
    )
    
    # Bottom right
    fig.add_shape(
        type="path",
        path=f"M {pitch_length} 1 Q {pitch_length-1} 0 {pitch_length-1} 0",
        line=dict(color=line_color, width=2)
    )
    
    return fig

def plot_goalkeeper_distribution(fig, goalkeeper_position, targets, success_rates=None):
    """
    Add goalkeeper distribution visualization to a pitch figure
    
    Parameters:
    -----------
    fig : plotly.graph_objects.Figure
        Plotly figure with the pitch
    goalkeeper_position : list
        [x, y] coordinates of the goalkeeper
    targets : dict
        Dictionary with target positions {name: [x, y]}
    success_rates : dict, optional
        Dictionary with success rates for each target {name: success_rate}
    
    Returns:
    --------
    fig : plotly.graph_objects.Figure
        Updated Plotly figure with distribution visualization
    """
    # Add goalkeeper position
    fig.add_trace(go.Scatter(
        x=[goalkeeper_position[0]],
        y=[goalkeeper_position[1]],
        mode='markers',
        marker=dict(size=15, color='cyan'),
        name='Goalkeeper'
    ))
    
    # Add target positions and distribution lines
    for name, position in targets.items():
        # Determine line width based on success rate
        line_width = 2
        line_color = 'rgba(255, 255, 255, 0.7)'
        
        if success_rates and name in success_rates:
            line_width = success_rates[name] * 5  # Scale width by success rate
            
            # Color coding based on success rate
            if success_rates[name] > 0.7:
                line_color = 'rgba(0, 255, 0, 0.7)'  # Green for high success
            elif success_rates[name] > 0.5:
                line_color = 'rgba(255, 255, 0, 0.7)'  # Yellow for medium success
            else:
                line_color = 'rgba(255, 0, 0, 0.7)'  # Red for low success
        
        # Add distribution line
        fig.add_trace(go.Scatter(
            x=[goalkeeper_position[0], position[0]],
            y=[goalkeeper_position[1], position[1]],
            mode='lines',
            line=dict(width=line_width, color=line_color),
            name=f'Pass to {name}'
        ))
        
        # Add target position
        fig.add_trace(go.Scatter(
            x=[position[0]],
            y=[position[1]],
            mode='markers',
            marker=dict(size=10, color='blue'),
            name=name
        ))
        
        # Add success rate label if provided
        if success_rates and name in success_rates:
            fig.add_trace(go.Scatter(
                x=[(goalkeeper_position[0] + position[0]) / 2],
                y=[(goalkeeper_position[1] + position[1]) / 2],
                mode='text',
                text=[f'xT: {success_rates[name]:.2f}'],
                textposition='top center',
                textfont=dict(color='white', size=10),
                showlegend=False
            ))
    
    return fig

def create_heatmap(pitch_fig, positions, values):
    """
    Add a heatmap overlay to a pitch figure
    
    Parameters:
    -----------
    pitch_fig : plotly.graph_objects.Figure
        Plotly figure with the pitch
    positions : list
        List of [x, y] coordinates
    values : list
        List of values corresponding to each position
    
    Returns:
    --------
    fig : plotly.graph_objects.Figure
        Updated Plotly figure with heatmap
    """
    # Extract x and y coordinates
    x = [pos[0] for pos in positions]
    y = [pos[1] for pos in positions]
    
    # Add heatmap to figure
    pitch_fig.add_trace(go.Histogram2dContour(
        x=x,
        y=y,
        z=values,
        colorscale='Hot',
        opacity=0.7,
        showscale=True,
        colorbar=dict(
            title='xT Value',
            titleside='right',
            titlefont=dict(size=14),
            tickfont=dict(size=12)
        ),
        hoverinfo='none'
    ))
    
    return pitch_fig

def create_pass_network(fig, positions, connections):
    """
    Add a pass network visualization to a pitch figure
    
    Parameters:
    -----------
    fig : plotly.graph_objects.Figure
        Plotly figure with the pitch
    positions : dict
        Dictionary with player positions {player_name: [x, y]}
    connections : list
        List of tuples (player1, player2, weight)
    
    Returns:
    --------
    fig : plotly.graph_objects.Figure
        Updated Plotly figure with pass network
    """
    # Add player positions
    for player, pos in positions.items():
        fig.add_trace(go.Scatter(
            x=[pos[0]],
            y=[pos[1]],
            mode='markers+text',
            marker=dict(size=12, color='blue'),
            text=[player],
            textposition='bottom center',
            name=player
        ))
    
    # Add connections
    for player1, player2, weight in connections:
        if player1 in positions and player2 in positions:
            fig.add_trace(go.Scatter(
                x=[positions[player1][0], positions[player2][0]],
                y=[positions[player1][1], positions[player2][1]],
                mode='lines',
                line=dict(width=weight*3, color='rgba(255, 255, 255, 0.7)'),
                hoverinfo='text',
                hovertext=f'{player1} → {player2}: {weight:.2f}',
                showlegend=False
            ))
    
    return fig
