```python
# xT-GK Analyzer - Python Implementation
# © 2025 xT-GK Project

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle, Arc
import json
import os
from typing import Dict, List, Tuple, Optional, Union

class XtGkAnalyzer:
    """
    A comprehensive analyzer for calculating and visualizing xT-GK metrics
    for goalkeeper offensive contributions.
    """
    
    def __init__(self, pitch_dimensions: Tuple[int, int] = (105, 68)):
        """
        Initialize the xT-GK analyzer.
        
        Parameters:
        -----------
        pitch_dimensions : tuple
            Dimensions of the pitch in meters (length, width)
        """
        self.pitch_dimensions = pitch_dimensions
        self.zone_grid = self._create_zone_grid(12, 8)  # 12x8 grid for pitch zones
        self.base_values = self._initialize_base_values()
        
    def _create_zone_grid(self, length_zones: int, width_zones: int) -> np.ndarray:
        """
        Create a grid of zones for the pitch.
        
        Parameters:
        -----------
        length_zones : int
            Number of zones along the length of the pitch
        width_zones : int
            Number of zones along the width of the pitch
            
        Returns:
        --------
        np.ndarray
            Grid of zones
        """
        return np.zeros((length_zones, width_zones))
    
    def _initialize_base_values(self) -> np.ndarray:
        """
        Initialize base xT values for each zone on the pitch.
        Higher values in attacking third, lower in defensive third.
        
        Returns:
        --------
        np.ndarray
            Base xT values for each zone
        """
        base_values = np.zeros_like(self.zone_grid)
        
        # Simplified base values - in a real implementation, these would be
        # derived from extensive data analysis
        for i in range(base_values.shape[0]):
            for j in range(base_values.shape[1]):
                # Higher values as we move toward attacking third
                base_values[i, j] = 0.01 + (i / base_values.shape[0]) * 0.1
                
                # Central zones slightly more valuable
                central_factor = 1 - (abs(j - base_values.shape[1]/2) / (base_values.shape[1]/2)) * 0.3
                base_values[i, j] *= central_factor
        
        return base_values
    
    def load_event_data(self, file_path: str) -> pd.DataFrame:
        """
        Load event data from a JSON file.
        
        Parameters:
        -----------
        file_path : str
            Path to the JSON file containing event data
            
        Returns:
        --------
        pd.DataFrame
            DataFrame containing event data
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to DataFrame for easier manipulation
        events = pd.DataFrame(data)
        return events
    
    def filter_goalkeeper_events(self, events: pd.DataFrame) -> pd.DataFrame:
        """
        Filter events to include only goalkeeper actions.
        
        Parameters:
        -----------
        events : pd.DataFrame
            DataFrame containing all event data
            
        Returns:
        --------
        pd.DataFrame
            DataFrame containing only goalkeeper events
        """
        # This is a simplified implementation - in reality, would need more
        # sophisticated filtering based on player positions and event types
        gk_events = events[events['position.name'] == 'Goalkeeper'].copy()
        return gk_events
    
    def calculate_distribution_value(self, pass_event: Dict) -> float:
        """
        Calculate the Distribution Value component of xT-GK.
        
        Parameters:
        -----------
        pass_event : dict
            Dictionary containing pass event data
            
        Returns:
        --------
        float
            Distribution Value
        """
        # Extract pass data
        start_x = pass_event.get('location', [0, 0])[0] / self.pitch_dimensions[0]
        start_y = pass_event.get('location', [0, 0])[1] / self.pitch_dimensions[1]
        
        end_x = pass_event.get('pass', {}).get('end_location', [0, 0])[0] / self.pitch_dimensions[0]
        end_y = pass_event.get('pass', {}).get('end_location', [0, 0])[1] / self.pitch_dimensions[1]
        
        # Calculate base value based on start and end zones
        start_zone_x = min(int(start_x * self.base_values.shape[0]), self.base_values.shape[0] - 1)
        start_zone_y = min(int(start_y * self.base_values.shape[1]), self.base_values.shape[1] - 1)
        
        end_zone_x = min(int(end_x * self.base_values.shape[0]), self.base_values.shape[0] - 1)
        end_zone_y = min(int(end_y * self.base_values.shape[1]), self.base_values.shape[1] - 1)
        
        # Value difference between zones
        value_diff = self.base_values[end_zone_x, end_zone_y] - self.base_values[start_zone_x, start_zone_y]
        
        # Progression factor - reward forward passes more
        progression_factor = 1.0
        if end_x > start_x:  # Forward pass
            progression_factor = 1.5
        elif end_x < start_x:  # Backward pass
            # In traditional xT, backward passes are penalized
            # In xT-GK, we recognize their value in maintaining possession
            progression_factor = 0.8
        
        # Outcome factor - successful passes have full value, unsuccessful are negative
        outcome_factor = 1.0
        if pass_event.get('pass', {}).get('outcome', {}).get('name', '') in ['Incomplete', 'Out']:
            outcome_factor = -0.5
        
        # Pressure factor - passes under pressure are more valuable
        pressure_factor = 1.0
        if pass_event.get('under_pressure', False):
            pressure_factor = 1.3
        
        # Calculate final distribution value
        distribution_value = max(0, value_diff) * progression_factor * outcome_factor * pressure_factor
        
        return distribution_value
    
    def calculate_pressure_escape_value(self, event: Dict) -> float:
        """
        Calculate the Pressure Escape Value component of xT-GK.
        
        Parameters:
        -----------
        event : dict
            Dictionary containing event data
            
        Returns:
        --------
        float
            Pressure Escape Value
        """
        # Simplified implementation
        if not event.get('under_pressure', False):
            return 0.0
        
        # Base value for escaping pressure
        base_escape_value = 0.05
        
        # Success factor
        success_factor = 1.0
        if event.get('type', {}).get('name', '') == 'Pass':
            if event.get('pass', {}).get('outcome', {}).get('name', '') in ['Incomplete', 'Out']:
                success_factor = 0.0
        
        # Calculate pressure escape value
        pressure_escape_value = base_escape_value * success_factor
        
        return pressure_escape_value
    
    def calculate_build_up_contribution(self, event: Dict, sequence_data: Optional[Dict] = None) -> float:
        """
        Calculate the Build-up Contribution component of xT-GK.
        
        Parameters:
        -----------
        event : dict
            Dictionary containing event data
        sequence_data : dict, optional
            Dictionary containing possession sequence data
            
        Returns:
        --------
        float
            Build-up Contribution
        """
        # Simplified implementation without sequence data
        if sequence_data is None:
            # Base contribution value
            base_contribution = 0.02
            
            # Event type factor
            event_type_factor = 1.0
            if event.get('type', {}).get('name', '') == 'Pass':
                # Passes contribute more to build-up
                event_type_factor = 1.5
            
            # Calculate build-up contribution
            build_up_contribution = base_contribution * event_type_factor
            
            return build_up_contribution
        else:
            # More sophisticated implementation would use sequence data
            # to track possession sequences and their outcomes
            pass
    
    def calculate_risk_adjusted_value(self, action_value: float, event: Dict) -> float:
        """
        Calculate the Risk-Adjusted Value component of xT-GK.
        
        Parameters:
        -----------
        action_value : float
            Combined value of the action (DV + PEV + BC)
        event : dict
            Dictionary containing event data
            
        Returns:
        --------
        float
            Risk-Adjusted Value
        """
        # Extract location data
        x = event.get('location', [0, 0])[0] / self.pitch_dimensions[0]
        
        # Risk increases as we get closer to our own goal
        risk_factor = 1.0 + (1.0 - x) * 0.5
        
        # Pressure increases risk
        if event.get('under_pressure', False):
            risk_factor *= 1.2
        
        # Calculate risk-adjusted value
        # Higher risk means potential value is discounted more
        risk_adjusted_value = action_value / risk_factor
        
        return risk_adjusted_value
    
    def calculate_xt_gk(self, event: Dict, sequence_data: Optional[Dict] = None) -> float:
        """
        Calculate the comprehensive xT-GK value for a goalkeeper action.
        
        Parameters:
        -----------
        event : dict
            Dictionary containing event data
        sequence_data : dict, optional
            Dictionary containing possession sequence data
            
        Returns:
        --------
        float
            xT-GK value
        """
        # Calculate component values
        distribution_value = 0.0
        if event.get('type', {}).get('name', '') == 'Pass':
            distribution_value = self.calculate_distribution_value(event)
        
        pressure_escape_value = self.calculate_pressure_escape_value(event)
        build_up_contribution = self.calculate_build_up_contribution(event, sequence_data)
        
        # Combined action value
        action_value = distribution_value + pressure_escape_value + build_up_contribution
        
        # Apply risk adjustment
        xt_gk = self.calculate_risk_adjusted_value(action_value, event)
        
        return xt_gk
    
    def process_match_events(self, events: pd.DataFrame) -> pd.DataFrame:
        """
        Process all events in a match to calculate xT-GK values.
        
        Parameters:
        -----------
        events : pd.DataFrame
            DataFrame containing event data
            
        Returns:
        --------
        pd.DataFrame
            DataFrame with added xT-GK values
        """
        # Filter goalkeeper events
        gk_events = self.filter_goalkeeper_events(events)
        
        # Calculate xT-GK for each event
        gk_events['xt_gk'] = gk_events.apply(
            lambda row: self.calculate_xt_gk(row.to_dict()), axis=1
        )
        
        return gk_events
    
    def aggregate_goalkeeper_performance(self, gk_events: pd.DataFrame) -> Dict:
        """
        Aggregate goalkeeper performance metrics.
        
        Parameters:
        -----------
        gk_events : pd.DataFrame
            DataFrame containing goalkeeper events with xT-GK values
            
        Returns:
        --------
        dict
            Dictionary containing aggregated performance metrics
        """
        # Group by goalkeeper
        gk_performance = {}
        
        for player_id, player_events in gk_events.groupby('player.id'):
            player_name = player_events['player.name'].iloc[0]
            team_name = player_events['team.name'].iloc[0]
            
            # Calculate metrics
            total_xt_gk = player_events['xt_gk'].sum()
            avg_xt_gk = player_events['xt_gk'].mean()
            num_actions = len(player_events)
            
            # Pass completion rate
            pass_events = player_events[player_events['type.name'] == 'Pass']
            if len(pass_events) > 0:
                completed_passes = pass_events[
                    ~pass_events['pass.outcome.name'].isin(['Incomplete', 'Out'])
                ]
                pass_completion_rate = len(completed_passes) / len(pass_events)
            else:
                pass_completion_rate = 0.0
            
            # Store metrics
            gk_performance[player_id] = {
                'player_name': player_name,
                'team_name': team_name,
                'total_xt_gk': total_xt_gk,
                'avg_xt_gk': avg_xt_gk,
                'num_actions': num_actions,
                'pass_completion_rate': pass_completion_rate
            }
        
        return gk_performance
    
    def plot_pitch(self, ax: plt.Axes = None, figsize: Tuple[int, int] = (12, 8)) -> Tuple[plt.Figure, plt.Axes]:
        """
        Plot a football pitch.
        
        Parameters:
        -----------
        ax : plt.Axes, optional
            Axes to plot on
        figsize : tuple, optional
            Figure size
            
        Returns:
        --------
        tuple
            Figure and Axes objects
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.figure
        
        # Pitch dimensions
        pitch_length, pitch_width = self.pitch_dimensions
        
        # Draw pitch outline
        ax.add_patch(Rectangle((0, 0), pitch_length, pitch_width, fill=False, color='black'))
        
        # Draw halfway line
        ax.plot([pitch_length/2, pitch_length/2], [0, pitch_width], color='black')
        
        # Draw center circle
        center_circle = plt.Circle((pitch_length/2, pitch_width/2), 9.15, fill=False, color='black')
        ax.add_patch(center_circle)
        
        # Draw penalty areas
        ax.add_patch(Rectangle((0, pitch_width/2 - 20.16), 16.5, 40.32, fill=False, color='black'))
        ax.add_patch(Rectangle((pitch_length - 16.5, pitch_width/2 - 20.16), 16.5, 40.32, fill=False, color='black'))
        
        # Draw goal areas
        ax.add_patch(Rectangle((0, pitch_width/2 - 9.16), 5.5, 18.32, fill=False, color='black'))
        ax.add_patch(Rectangle((pitch_length - 5.5, pitch_width/2 - 9.16), 5.5, 18.32, fill=False, color='black'))
        
        # Draw penalty spots
        ax.plot([11, 11], [pitch_width/2, pitch_width/2], 'o', color='black')
        ax.plot([pitch_length - 11, pitch_length - 11], [pitch_width/2, pitch_width/2], 'o', color='black')
        
        # Draw penalty arcs
        left_arc = Arc((11, pitch_width/2), 18.3, 18.3, theta1=310, theta2=50, color='black')
        right_arc = Arc((pitch_length - 11, pitch_width/2), 18.3, 18.3, theta1=130, theta2=230, color='black')
        ax.add_patch(left_arc)
        ax.add_patch(right_arc)
        
        # Set axis limits
        ax.set_xlim(-5, pitch_length + 5)
        ax.set_ylim(-5, pitch_width + 5)
        
        # Remove axis ticks
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Equal aspect ratio
        ax.set_aspect('equal')
        
        return fig, ax
    
    def plot_xt_gk_heatmap(self, gk_events: pd.DataFrame, player_id: Optional[int] = None) -> plt.Figure:
        """
        Create a heatmap visualization of xT-GK values across the pitch.
        
        Parameters:
        -----------
        gk_events : pd.DataFrame
            DataFrame containing goalkeeper events with xT-GK values
        player_id : int, optional
            Player ID to filter events for a specific goalkeeper
            
        Returns:
        --------
        plt.Figure
            Heatm
(Content truncated due to size limit. Use line ranges to read in chunks)