import os
import json
import pandas as pd
import numpy as np

class StatsBombDataLoader:
    """
    Utility class for loading and processing StatsBomb open data for xT-GK analysis.
    """
    
    def __init__(self, data_dir='/home/ubuntu/statsbomb_open_data/data'):
        """
        Initialize the data loader with the path to the StatsBomb data directory.
        
        Parameters:
        -----------
        data_dir : str
            Path to the StatsBomb data directory
        """
        self.data_dir = data_dir
        self.competitions = self._load_competitions()
        
    def _load_competitions(self):
        """
        Load the competitions data.
        
        Returns:
        --------
        list
            List of competition dictionaries
        """
        competitions_file = os.path.join(self.data_dir, 'competitions.json')
        with open(competitions_file, 'r', encoding='utf-8') as f:
            competitions = json.load(f)
        return competitions
    
    def get_la_liga_competitions(self):
        """
        Get La Liga competitions from the competitions data.
        
        Returns:
        --------
        list
            List of La Liga competition dictionaries
        """
        la_liga_competitions = [
            comp for comp in self.competitions 
            if comp.get('competition_name') == 'La Liga'
        ]
        return la_liga_competitions
    
    def get_matches(self, competition_id, season_id):
        """
        Get matches for a specific competition and season.
        
        Parameters:
        -----------
        competition_id : int
            Competition ID
        season_id : int
            Season ID
            
        Returns:
        --------
        list
            List of match dictionaries
        """
        matches_file = os.path.join(
            self.data_dir, 'matches', str(competition_id), str(season_id) + '.json'
        )
        
        if not os.path.exists(matches_file):
            return []
        
        with open(matches_file, 'r', encoding='utf-8') as f:
            matches = json.load(f)
        
        return matches
    
    def get_match_events(self, match_id):
        """
        Get events for a specific match.
        
        Parameters:
        -----------
        match_id : int
            Match ID
            
        Returns:
        --------
        list
            List of event dictionaries
        """
        events_file = os.path.join(self.data_dir, 'events', str(match_id) + '.json')
        
        if not os.path.exists(events_file):
            return []
        
        with open(events_file, 'r', encoding='utf-8') as f:
            events = json.load(f)
        
        return events
    
    def get_match_lineups(self, match_id):
        """
        Get lineups for a specific match.
        
        Parameters:
        -----------
        match_id : int
            Match ID
            
        Returns:
        --------
        list
            List of lineup dictionaries
        """
        lineups_file = os.path.join(self.data_dir, 'lineups', str(match_id) + '.json')
        
        if not os.path.exists(lineups_file):
            return []
        
        with open(lineups_file, 'r', encoding='utf-8') as f:
            lineups = json.load(f)
        
        return lineups
    
    def get_goalkeeper_events(self, events, lineups):
        """
        Filter events to include only goalkeeper actions.
        
        Parameters:
        -----------
        events : list
            List of event dictionaries
        lineups : list
            List of lineup dictionaries
            
        Returns:
        --------
        list
            List of goalkeeper event dictionaries
        """
        # Extract goalkeeper player IDs from lineups
        goalkeeper_ids = []
        for team_lineup in lineups:
            for player in team_lineup.get('lineup', []):
                if player.get('position', {}).get('name') == 'Goalkeeper':
                    goalkeeper_ids.append(player.get('player_id'))
        
        # Filter events for goalkeeper actions
        goalkeeper_events = [
            event for event in events 
            if event.get('player', {}).get('id') in goalkeeper_ids
        ]
        
        return goalkeeper_events
    
    def get_goalkeeper_pass_events(self, events, lineups):
        """
        Filter events to include only goalkeeper pass actions.
        
        Parameters:
        -----------
        events : list
            List of event dictionaries
        lineups : list
            List of lineup dictionaries
            
        Returns:
        --------
        list
            List of goalkeeper pass event dictionaries
        """
        goalkeeper_events = self.get_goalkeeper_events(events, lineups)
        
        # Filter for pass events
        goalkeeper_pass_events = [
            event for event in goalkeeper_events 
            if event.get('type', {}).get('name') == 'Pass'
        ]
        
        return goalkeeper_pass_events
    
    def get_goalkeeper_distribution_data(self, competition_id=11, season_id=90, num_matches=5):
        """
        Get goalkeeper distribution data for analysis.
        
        Parameters:
        -----------
        competition_id : int
            Competition ID (default: 11 for La Liga)
        season_id : int
            Season ID (default: 90 for a specific season)
        num_matches : int
            Number of matches to include (default: 5)
            
        Returns:
        --------
        dict
            Dictionary containing goalkeeper distribution data
        """
        matches = self.get_matches(competition_id, season_id)
        
        if not matches:
            return {
                'goalkeeper_data': [],
                'pass_events': [],
                'match_info': []
            }
        
        # Limit to specified number of matches
        matches = matches[:num_matches]
        
        all_goalkeeper_data = []
        all_pass_events = []
        match_info = []
        
        for match in matches:
            match_id = match.get('match_id')
            
            # Get events and lineups
            events = self.get_match_events(match_id)
            lineups = self.get_match_lineups(match_id)
            
            if not events or not lineups:
                continue
            
            # Get goalkeeper pass events
            goalkeeper_pass_events = self.get_goalkeeper_pass_events(events, lineups)
            
            # Process each goalkeeper's data
            for team_lineup in lineups:
                team_id = team_lineup.get('team_id')
                team_name = team_lineup.get('team_name')
                
                for player in team_lineup.get('lineup', []):
                    if player.get('position', {}).get('name') == 'Goalkeeper':
                        player_id = player.get('player_id')
                        player_name = player.get('player_name')
                        
                        # Filter pass events for this goalkeeper
                        gk_passes = [
                            event for event in goalkeeper_pass_events 
                            if event.get('player', {}).get('id') == player_id
                        ]
                        
                        # Calculate basic stats
                        total_passes = len(gk_passes)
                        successful_passes = len([
                            p for p in gk_passes 
                            if not p.get('pass', {}).get('outcome')
                        ])
                        
                        if total_passes > 0:
                            success_rate = successful_passes / total_passes
                        else:
                            success_rate = 0
                        
                        # Categorize passes
                        short_passes = [
                            p for p in gk_passes 
                            if p.get('pass', {}).get('length') and p.get('pass', {}).get('length') < 30
                        ]
                        
                        long_passes = [
                            p for p in gk_passes 
                            if p.get('pass', {}).get('length') and p.get('pass', {}).get('length') >= 30
                        ]
                        
                        short_pass_pct = len(short_passes) / total_passes if total_passes > 0 else 0
                        long_pass_pct = len(long_passes) / total_passes if total_passes > 0 else 0
                        
                        # Calculate pressure stats
                        under_pressure = [
                            p for p in gk_passes 
                            if p.get('under_pressure')
                        ]
                        
                        pressure_pct = len(under_pressure) / total_passes if total_passes > 0 else 0
                        
                        # Store goalkeeper data
                        goalkeeper_data = {
                            'match_id': match_id,
                            'player_id': player_id,
                            'player_name': player_name,
                            'team_id': team_id,
                            'team_name': team_name,
                            'total_passes': total_passes,
                            'successful_passes': successful_passes,
                            'success_rate': success_rate,
                            'short_passes': len(short_passes),
                            'long_passes': len(long_passes),
                            'short_pass_pct': short_pass_pct,
                            'long_pass_pct': long_pass_pct,
                            'under_pressure': len(under_pressure),
                            'pressure_pct': pressure_pct
                        }
                        
                        all_goalkeeper_data.append(goalkeeper_data)
                        all_pass_events.extend(gk_passes)
            
            # Store match info
            match_info.append({
                'match_id': match_id,
                'home_team': match.get('home_team', {}).get('home_team_name'),
                'away_team': match.get('away_team', {}).get('away_team_name'),
                'competition': match.get('competition', {}).get('competition_name'),
                'season': match.get('season', {}).get('season_name')
            })
        
        return {
            'goalkeeper_data': all_goalkeeper_data,
            'pass_events': all_pass_events,
            'match_info': match_info
        }
    
    def get_sample_data(self):
        """
        Get a sample of goalkeeper distribution data for quick testing.
        
        Returns:
        --------
        dict
            Dictionary containing sample goalkeeper distribution data
        """
        # Default to La Liga data
        return self.get_goalkeeper_distribution_data(
            competition_id=11,  # La Liga
            season_id=90,       # 2018/2019 season
            num_matches=3       # First 3 matches
        )
