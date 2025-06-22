import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from crewai.tools import BaseTool
from typing import Type, List, Dict
from pydantic import BaseModel, Field
import json
import re
import os

class TransitScheduleProcessor:
    def __init__(self):
        self.transit_df = None
        self.stops_cache = {}
        self.routes_cache = {}
        self.file_path = None
        self.is_loaded = False

    def load_schedule_data(self, file_path: str):
        try:
            self.file_path = file_path
            
            # Check if file exists
            if not os.path.exists(file_path):
                return False
            
            # For large files, read in chunks to avoid memory issues
            print(f"🔄 Loading transit data from: {file_path}")
            
            # Read the first few lines to check format
            sample_df = pd.read_csv(file_path, nrows=10)
            required_columns = ['route_id', 'route_short_name', 'route_long_name', 'trip_id', 'stop_sequence', 'stop_id', 'stop_name', 'arrival_time', 'departure_time']
            missing_columns = [col for col in required_columns if col not in sample_df.columns]
            if missing_columns:
                print(f"❌ Missing required columns: {missing_columns}")
                return False
            
            # Load the full dataset
            print("📊 Loading full dataset...")
            self.transit_df = pd.read_csv(file_path)
            
            # Clean and process the data
            print("🧹 Processing data...")
            
            # Handle time columns - try different formats
            for time_col in ['arrival_time', 'departure_time']:
                if time_col in self.transit_df.columns:
                    # Try to parse times, handle various formats
                    try:
                        self.transit_df[time_col] = pd.to_datetime(self.transit_df[time_col], format='%H:%M:%S', errors='coerce').dt.time
                    except:
                        try:
                            self.transit_df[time_col] = pd.to_datetime(self.transit_df[time_col], format='%H:%M', errors='coerce').dt.time
                        except:
                            # If all else fails, try to parse as string and extract time
                            self.transit_df[time_col] = pd.to_datetime(self.transit_df[time_col], errors='coerce').dt.time
            
            # Clean stop names - remove extra whitespace and normalize
            if 'stop_name' in self.transit_df.columns:
                self.transit_df['stop_name'] = self.transit_df['stop_name'].astype(str).str.strip()
            
            # Build caches
            print("🏗️ Building search caches...")
            self._build_caches()
            
            self.is_loaded = True
            print(f"✅ Successfully loaded {len(self.transit_df):,} records")
            return True
            
        except Exception as e:
            print(f"❌ Error loading schedule data: {e}")
            return False

    def _build_caches(self):
        if self.transit_df is None:
            return
        
        # Build stops cache for faster searching
        print("🔍 Building stops cache...")
        unique_stops = self.transit_df['stop_name'].dropna().unique()
        self.stops_cache = {}
        for stop in unique_stops:
            if isinstance(stop, str) and stop.strip():
                # Create multiple search keys for better matching
                stop_lower = stop.lower().strip()
                self.stops_cache[stop_lower] = stop
                # Also add partial matches
                words = stop_lower.split()
                for word in words:
                    if len(word) > 2:  # Only add meaningful words
                        if word not in self.stops_cache:
                            self.stops_cache[word] = stop
        
        # Build routes cache
        print("🚌 Building routes cache...")
        route_info = self.transit_df.groupby('route_id').agg({
            'route_short_name': 'first', 
            'route_long_name': 'first', 
            'stop_name': 'nunique'
        }).reset_index()
        self.routes_cache = route_info.to_dict('records')
        
        print(f"✅ Built caches: {len(self.stops_cache)} stop entries, {len(self.routes_cache)} routes")

    def get_route_summary(self) -> str:
        if self.transit_df is None:
            return "No data loaded."
        
        total_routes = len(self.transit_df['route_id'].unique())
        total_stops = len(self.transit_df['stop_id'].unique())
        total_trips = len(self.transit_df['trip_id'].unique())
        
        # Get some sample route names
        sample_routes = self.transit_df['route_short_name'].dropna().unique()[:5]
        route_list = ", ".join([str(r) for r in sample_routes])
        
        summary = f"📊 Transit System Summary:\n"
        summary += f"• Total Routes: {total_routes:,}\n"
        summary += f"• Total Stops: {total_stops:,}\n"
        summary += f"• Total Trips: {total_trips:,}\n"
        summary += f"• Sample Routes: {route_list}\n"
        summary += f"• File: {self.file_path}"
        
        return summary

    def find_stops_by_name(self, location_name: str, limit: int = 10) -> List[str]:
        if not self.is_loaded:
            return []
        
        matches = []
        query = location_name.lower().strip()
        
        # Direct match
        if query in self.stops_cache:
            matches.append(self.stops_cache[query])
        
        # Partial matches
        for key, stop in self.stops_cache.items():
            if query in key and stop not in matches:
                matches.append(stop)
            if len(matches) >= limit:
                break
        
        # If no matches found, try fuzzy matching
        if not matches:
            for key, stop in self.stops_cache.items():
                if any(word in key for word in query.split()):
                    if stop not in matches:
                        matches.append(stop)
                if len(matches) >= limit:
                    break
        
        return matches[:limit]

    def get_routes_between_stops(self, origin: str, destination: str, time_str: str, max_routes: int = 5) -> List[Dict]:
        if not self.is_loaded:
            return []
        
        try:
            # Parse departure time
            try:
                dep_time = datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                return []
            
            # Find origin trips
            origin_trips = self.transit_df[
                (self.transit_df['stop_name'].str.contains(origin, case=False, na=False)) &
                (self.transit_df['departure_time'] >= dep_time)
            ].copy()
            
            if origin_trips.empty:
                return []
            
            routes = []
            for _, origin_row in origin_trips.iterrows():
                trip_id = origin_row['trip_id']
                
                # Find destination in the same trip
                dest_match = self.transit_df[
                    (self.transit_df['trip_id'] == trip_id) &
                    (self.transit_df['stop_name'].str.contains(destination, case=False, na=False)) &
                    (self.transit_df['stop_sequence'] > origin_row['stop_sequence'])
                ]
                
                if not dest_match.empty:
                    dest_row = dest_match.iloc[0]
                    
                    # Calculate duration
                    dep_dt = datetime.combine(datetime.today(), origin_row['departure_time'])
                    arr_dt = datetime.combine(datetime.today(), dest_row['arrival_time'])
                    if arr_dt < dep_dt:
                        arr_dt += timedelta(days=1)
                    duration = int((arr_dt - dep_dt).total_seconds() / 60)
                    
                    route = {
                        'route_id': origin_row['route_id'],
                        'route_short_name': origin_row['route_short_name'],
                        'route_long_name': origin_row['route_long_name'],
                        'trip_id': trip_id,
                        'origin_stop': origin_row['stop_name'],
                        'destination_stop': dest_row['stop_name'],
                        'departure_time': origin_row['departure_time'].strftime('%H:%M'),
                        'arrival_time': dest_row['arrival_time'].strftime('%H:%M'),
                        'duration_minutes': duration,
                        'cost': self._estimate_cost(origin_row['route_short_name']),
                        'stop_count': int(dest_row['stop_sequence'] - origin_row['stop_sequence'])
                    }
                    routes.append(route)
                
                if len(routes) >= max_routes:
                    break
            
            return sorted(routes, key=lambda x: x['departure_time'])
            
        except Exception as e:
            print(f"❌ Error finding routes: {e}")
            return []

    def _estimate_cost(self, route_short_name: str) -> float:
        if pd.isna(route_short_name):
            return 2.50
        
        short = str(route_short_name).upper()
        if 'BART' in short or 'BR' in short:
            return 4.95
        elif 'EXPRESS' in short or 'EX' in short:
            return 5.00
        elif any(tag in short for tag in ['BRT', 'RAPID']):
            return 3.50
        else:
            return 2.50

    def get_popular_stops(self, limit: int = 10) -> List[str]:
        """Get the most popular stops based on frequency in the schedule."""
        if not self.is_loaded:
            return []
        
        stop_counts = self.transit_df['stop_name'].value_counts()
        return stop_counts.head(limit).index.tolist()

    def get_route_statistics(self) -> Dict:
        """Get statistics about the transit system."""
        if not self.is_loaded:
            return {}
        
        stats = {
            'total_routes': len(self.transit_df['route_id'].unique()),
            'total_stops': len(self.transit_df['stop_id'].unique()),
            'total_trips': len(self.transit_df['trip_id'].unique()),
            'popular_stops': self.get_popular_stops(5),
            'route_types': self.transit_df['route_short_name'].value_counts().head(10).to_dict()
        }
        
        return stats

# Global instance
schedule_processor = TransitScheduleProcessor()

# Tool Input Schemas
class LoadTransitDataInput(BaseModel):
    file_path: str = Field(..., description="Path to the transit schedule CSV file")

class SearchStopsInput(BaseModel):
    location: str = Field(..., description="Location name to search for stops")

class FindTransitRoutesInput(BaseModel):
    origin: str = Field(..., description="Origin location")
    destination: str = Field(..., description="Destination location")
    time: str = Field(..., description="Departure time in HH:MM format (24-hour)")

class GetRouteInfoInput(BaseModel):
    route: str = Field(..., description="Route name or number to get information about")

class GetSystemStatsInput(BaseModel):
    pass

# Tool Classes
class LoadTransitDataTool(BaseTool):
    name: str = "load_transit_data"
    description: str = "Load transit schedule data from a CSV file and return summary information"
    args_schema: Type[BaseModel] = LoadTransitDataInput

    def _run(self, file_path: str) -> str:
        success = schedule_processor.load_schedule_data(file_path)
        if success:
            summary = schedule_processor.get_route_summary()
            return summary
        else:
            return "❌ Failed to load transit data. Please check the file path and format."

class SearchStopsTool(BaseTool):
    name: str = "search_stops"
    description: str = "Search for transit stops by location name"
    args_schema: Type[BaseModel] = SearchStopsInput

    def _run(self, location: str) -> str:
        if not schedule_processor.is_loaded:
            return "❌ Please load transit data first using load_transit_data tool."
        
        results = schedule_processor.find_stops_by_name(location)
        if results:
            return "\n".join([f"🚏 {stop}" for stop in results])
        else:
            return f"❌ No stops found for '{location}'. Try searching for popular stops like 'BART', 'Transit Center', or 'Station'."

class FindTransitRoutesTool(BaseTool):
    name: str = "find_transit_routes"
    description: str = "Find transit routes from origin to destination after a given time"
    args_schema: Type[BaseModel] = FindTransitRoutesInput

    def _run(self, origin: str, destination: str, time: str) -> str:
        if not schedule_processor.is_loaded:
            return "❌ Please load transit data first using load_transit_data tool."
        
        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            return "❌ Time format must be HH:MM (24-hour format)"
        
        origins = schedule_processor.find_stops_by_name(origin)
        destinations = schedule_processor.find_stops_by_name(destination)
        
        if not origins or not destinations:
            return f"❌ No stops found near: origin='{origin}', destination='{destination}'\n💡 Try searching for stops first using the search_stops tool."
        
        routes = []
        for o in origins:
            for d in destinations:
                routes.extend(schedule_processor.get_routes_between_stops(o, d, time))
        
        if not routes:
            return "❌ No direct routes found. Try different stops or times."
        
        output = []
        for i, route in enumerate(routes[:5]):
            output.append(
                f"{i+1}. {route['route_short_name']} from {route['origin_stop']} to {route['destination_stop']} - "
                f"Departs {route['departure_time']}, Arrives {route['arrival_time']}, "
                f"Duration {route['duration_minutes']} min, Cost ${route['cost']:.2f}"
            )
        
        return "\n".join(output)

class GetRouteInfoTool(BaseTool):
    name: str = "get_route_info"
    description: str = "Get detailed information about a specific transit route including all stops"
    args_schema: Type[BaseModel] = GetRouteInfoInput

    def _run(self, route: str) -> str:
        if not schedule_processor.is_loaded:
            return "❌ Please load transit data first using load_transit_data tool."
        
        filtered = schedule_processor.transit_df[
            schedule_processor.transit_df['route_short_name'].str.contains(route, case=False, na=False)
        ]
        
        if filtered.empty:
            return f"❌ Route '{route}' not found."
        
        stops = filtered['stop_name'].dropna().unique()[:20]
        return f"🚌 Route {route} stops:\n" + "\n".join([f"{i+1}. {stop}" for i, stop in enumerate(stops)])

class GetSystemStatsTool(BaseTool):
    name: str = "get_system_stats"
    description: str = "Get comprehensive statistics about the transit system"
    args_schema: Type[BaseModel] = GetSystemStatsInput

    def _run(self) -> str:
        if not schedule_processor.is_loaded:
            return "❌ Please load transit data first using load_transit_data tool."
        
        stats = schedule_processor.get_route_statistics()
        
        output = "📊 Transit System Statistics:\n"
        output += f"• Total Routes: {stats['total_routes']:,}\n"
        output += f"• Total Stops: {stats['total_stops']:,}\n"
        output += f"• Total Trips: {stats['total_trips']:,}\n"
        output += f"• Popular Stops:\n"
        for stop in stats['popular_stops']:
            output += f"  - {stop}\n"
        output += f"• Top Route Types:\n"
        for route, count in list(stats['route_types'].items())[:5]:
            output += f"  - {route}: {count:,} trips\n"
        
        return output 