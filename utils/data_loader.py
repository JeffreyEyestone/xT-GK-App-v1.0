import os
import json
import pandas as pd
import numpy as np

class StatsBombDataLoader:
    """
    Class for loading and processing StatsBomb data for goalkeeper distribution analysis.
    """
    
    def __init__(self, data_dir='data/statsbomb_data'):
        """
        Initialize the data loader with the path to the StatsBomb data directory.
        
        Parameters:
        -----------
        data_dir : str
            Path to the StatsBomb data directory
        """
        self.data_dir = data_dir
        # Create directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        # Try to load competitions, but use empty list if file doesn't exist
        self.competitions = self._load_competitions()
    
    def _load_competitions(self):
        """
        Load competitions data from StatsBomb open data.
        
        Returns:
        --------
        list
            List of competition dictionaries
        """
        competitions_file = os.path.join(self.data_dir, 'competitions.json')
        
        if os.path.exists(competitions_file):
            with open(competitions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Return sample competition data if file doesn't exist
            return [
                {
                    "competition_id": 11,
                    "season_id": 26,
                    "country_name": "Spain",
                    "competition_name": "La Liga",
                    "season_name": "2015/2016"
                }
            ]
    
    def get_matches(self, competition_id=11, season_id=26):
        """
        Get matches for a specific competition and season.
        
        Parameters:
        -----------
        competition_id : int
            ID of the competition
        season_id : int
            ID of the season
        
        Returns:
        --------
        list
            List of match dictionaries
        """
        matches_file = os.path.join(self.data_dir, f'matches_{competition_id}_{season_id}.json')
        
        if os.path.exists(matches_file):
            with open(matches_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Return sample match data if file doesn't exist
            return [
                {
                    "match_id": 1,
                    "match_date": "2015-08-23",
                    "kick_off": "19:30:00.000",
                    "competition": {
                        "competition_id": 11,
                        "country_name": "Spain",
                        "competition_name": "La Liga"
                    },
                    "season": {
                        "season_id": 26,
                        "season_name": "2015/2016"
                    },
                    "home_team": {
                        "home_team_id": 217,
                        "home_team_name": "Real Madrid"
                    },
                    "away_team": {
                        "away_team_id": 218,
                        "away_team_name": "Atlético Madrid"
                    },
                    "home_score": 2,
                    "away_score": 1,
                    "stadium_name": "Santiago Bernabéu"
                }
            ]
    
    def get_events(self, match_id):
        """
        Get events for a specific match.
        
        Parameters:
        -----------
        match_id : int
            ID of the match
        
        Returns:
        --------
        list
            List of event dictionaries
        """
        events_file = os.path.join(self.data_dir, f'events_{match_id}.json')
        
        if os.path.exists(events_file):
            with open(events_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Return sample event data if file doesn't exist
            return self.get_sample_data()['pass_events']
    
    def get_goalkeeper_distribution_data(self, competition_id=11, season_id=26):
        """
        Get goalkeeper distribution data for a specific competition and season.
        
        Parameters:
        -----------
        competition_id : int
            ID of the competition
        season_id : int
            ID of the season
        
        Returns:
        --------
        dict
            Dictionary containing goalkeeper distribution data
        """
        try:
            # Get matches for the competition and season
            matches = self.get_matches(competition_id, season_id)
            
            # Initialize data structures
            goalkeeper_data = []
            all_pass_events = []
            match_info = []
            
            # Process each match
            for match in matches[:5]:  # Limit to 5 matches for performance
                match_id = match['match_id']
                
                # Get events for the match
                events = self.get_events(match_id)
                
                # Extract goalkeeper pass events
                gk_pass_events = [
                    event for event in events 
                    if event.get('type', {}).get('name') == 'Pass' and 
                    event.get('position', {}).get('name') == 'Goalkeeper'
                ]
                
                # Process goalkeeper data
                for player_id, player_events in self._group_by_player(gk_pass_events):
                    player_name = player_events[0].get('player', {}).get('name', 'Unknown')
                    team_id = player_events[0].get('team', {}).get('id')
                    team_name = player_events[0].get('team', {}).get('name', 'Unknown')
                    
                    # Calculate pass statistics
                    total_passes = len(player_events)
                    successful_passes = sum(1 for e in player_events if not e.get('pass', {}).get('outcome'))
                    success_rate = successful_passes / total_passes if total_passes > 0 else 0
                    
                    # Categorize passes
                    short_passes = sum(1 for e in player_events if e.get('pass', {}).get('length') < 30)
                    long_passes = total_passes - short_passes
                    short_pass_pct = short_passes / total_passes if total_passes > 0 else 0
                    long_pass_pct = long_passes / total_passes if total_passes > 0 else 0
                    
                    # Pressure analysis
                    under_pressure = sum(1 for e in player_events if e.get('under_pressure'))
                    pressure_pct = under_pressure / total_passes if total_passes > 0 else 0
                    
                    # Add to goalkeeper data
                    goalkeeper_data.append({
                        'match_id': match_id,
                        'player_id': player_id,
                        'player_name': player_name,
                        'team_id': team_id,
                        'team_name': team_name,
                        'total_passes': total_passes,
                        'successful_passes': successful_passes,
                        'success_rate': success_rate,
                        'short_passes': short_passes,
                        'long_passes': long_passes,
                        'short_pass_pct': short_pass_pct,
                        'long_pass_pct': long_pass_pct,
                        'under_pressure': under_pressure,
                        'pressure_pct': pressure_pct
                    })
                
                # Add pass events and match info
                all_pass_events.extend(gk_pass_events)
                match_info.append({
                    'match_id': match_id,
                    'home_team': match['home_team']['home_team_name'],
                    'away_team': match['away_team']['away_team_name'],
                    'competition': match['competition']['competition_name'],
                    'season': match['season']['season_name']
                })
            
            return {
                'goalkeeper_data': goalkeeper_data,
                'pass_events': all_pass_events,
                'match_info': match_info
            }
        
        except Exception as e:
            print(f"Error loading goalkeeper distribution data: {e}")
            # Return sample data if there's an error
            return self.get_sample_data()
    
    def _group_by_player(self, events):
        """
        Group events by player ID.
        
        Parameters:
        -----------
        events : list
            List of event dictionaries
        
        Returns:
        --------
        list
            List of (player_id, player_events) tuples
        """
        player_events = {}
        
        for event in events:
            player_id = event.get('player', {}).get('id')
            if player_id:
                if player_id not in player_events:
                    player_events[player_id] = []
                player_events[player_id].append(event)
        
        return player_events.items()
    
    def get_sample_data(self):
        """
        Get a sample of goalkeeper distribution data for quick testing.
        
        Returns:
        --------
        dict
            Dictionary containing sample goalkeeper distribution data
        """
        # Create sample data for testing
        sample_goalkeeper_data = [
            {
                'match_id': 1,
                'player_id': 5246,
                'player_name': 'Keylor Navas',
                'team_id': 217,
                'team_name': 'Real Madrid',
                'total_passes': 35,
                'successful_passes': 28,
                'success_rate': 0.8,
                'short_passes': 20,
                'long_passes': 15,
                'short_pass_pct': 0.57,
                'long_pass_pct': 0.43,
                'under_pressure': 12,
                'pressure_pct': 0.34
            },
            {
                'match_id': 1,
                'player_id': 5247,
                'player_name': 'Jan Oblak',
                'team_id': 218,
                'team_name': 'Atlético Madrid',
                'total_passes': 28,
                'successful_passes': 20,
                'success_rate': 0.71,
                'short_passes': 10,
                'long_passes': 18,
                'short_pass_pct': 0.36,
                'long_pass_pct': 0.64,
                'under_pressure': 15,
                'pressure_pct': 0.54
            }
        ]
        
        sample_match_info = [
            {
                'match_id': 1,
                'home_team': 'Real Madrid',
                'away_team': 'Atlético Madrid',
                'competition': 'La Liga',
                'season': '2015/2016'
            }
        ]
        
        # Return sample data directly without trying to load real data
        return {
            'goalkeeper_data': sample_goalkeeper_data,
            'pass_events': [],
            'match_info': sample_match_info
        }
