import yaml
import pandas as pd
from os import path, makedirs
from datetime import datetime

def load_config():
    config_file_path = path.abspath(
        path.join(
            str(path.dirname(__file__)), 
            "config.yml"
        )
    )
    
    with open(config_file_path) as fd:
        config = yaml.safe_load(fd)
    
    return config


class Flights:
    def __init__(
        self, 
        csv_file_path = None, 
        min_duration_time_minutes = None, 
        limit_per_day = None
    ) -> None:
        config = load_config()
        
        self.file_path = csv_file_path or \
            path.abspath(
                path.join(
                    config['source']['directory_path'],
                    config['source']['resource_path']
                )
            )
        
        self.min_duration_time_minutes = \
            min_duration_time_minutes or \
            config['success_conditions']['min_duration_time_minutes']
            
        self.limit_per_day = \
            limit_per_day or \
            config['success_conditions']['limit_per_day']
        
        self._init()
        self._update()
    
    def _init(self):
        if path.exists(self.file_path):
            return
        
        dir_path = path.dirname(self.file_path)
        
        if not path.exists(dir_path):
            makedirs(dir_path)
        
        df = pd.DataFrame(columns=['flight ID', 'Arrival', 'Departure' , 'success'])
        self._save_to_csv(df=df)
    
    def _calc_flight_duration(self, flight):
        arrival_time = datetime.strptime(flight["Arrival"].strip(), "%H:%M")
        departure_time = datetime.strptime(flight["Departure"].strip(), "%H:%M")
        delta = departure_time - arrival_time
        
        return delta.total_seconds() / 60
        
    def _update(self):
        flights = pd.read_csv(self.file_path)
        flights.sort_values("Arrival", inplace = True)
        flights.reset_index(drop = True, inplace = True)
        flights['success'] = False
        
        for index, flight in flights.iterrows():
            df = flights.head(index)
            flight_duration_minutes = self._calc_flight_duration(flight=flight)
            
            prev_success_flights = len(
                df[
                    (df["flight ID"] == flight["flight ID"]) &
                    (df["success"] == True)
                ]
            )
            
            flights.at[index,'success'] = \
                flight_duration_minutes >= self.min_duration_time_minutes and \
                prev_success_flights < self.limit_per_day
                
        self._save_to_csv(flights)
    
    def _save_to_csv(self, df):
        df.to_csv(self.file_path, index=False)
    
    def get_flight_info(self, flight_id):        
        flights = pd.read_csv(self.file_path)
        flights = flights[flights["flight ID"] == flight_id]
        
        return flights.to_dict('records')
    
    def add_new_flights(self, flights):
        flights_df = pd.read_csv(self.file_path)
        
        for flight in flights:
            if any(
                [
                    col_name not in flight for 
                    col_name in ['flight ID', 'Arrival', 'Departure'] \
                ]
            ):
                continue
            
            flights_df.loc[len(flights_df)] = flight
        
        self._save_to_csv(df=flights_df)
        self._update()
        
