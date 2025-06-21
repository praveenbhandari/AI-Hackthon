# Safe Route Finder - San Francisco

A comprehensive system that analyzes police incident data to find the safest walking routes in San Francisco. This tool uses real police incident data to calculate safety scores and recommend optimal paths between any two points in the city.

## 🛡️ Features

### Core Functionality
- **Real-time Safety Analysis**: Uses actual San Francisco Police Department incident data
- **Smart Route Optimization**: Finds routes that balance safety and distance
- **Interactive Maps**: Visualize routes with color-coded safety levels
- **Safety Scoring**: Letter grades (A+ to F) based on incident density and severity
- **Time-based Analysis**: Considers day/night incident patterns
- **Incident Severity Weighting**: Different weights for different types of crimes

### Safety Metrics
- **Incident Density**: Number of recent incidents in the area
- **Severity Analysis**: Weighted scoring based on crime type (homicide, robbery, assault, etc.)
- **Time Patterns**: Night incidents weighted more heavily
- **Infrastructure Consideration**: Street lighting and maintenance data
- **Response Time Analysis**: Emergency response efficiency

### User Interface
- **Web-based Interface**: Modern, responsive design
- **Interactive Controls**: Adjustable safety vs. distance preferences
- **Preset Locations**: Quick access to popular San Francisco destinations
- **Real-time Feedback**: Live safety scores and recommendations
- **Visual Analytics**: Charts and statistics for route analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Police incident data CSV file (included)

### Installation

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure the police data file is present**:
   - `Police_Department_Incident_Reports__2018_to_Present_20250621.csv`

### Running the Application

#### Option 1: Web Interface (Recommended)
```bash
python web_interface.py
```
Then open your browser to `http://localhost:5000`

#### Option 2: Command Line Demo
```bash
python safe_route_finder.py
```

## 📊 How It Works

### Data Processing
1. **Load Police Data**: Reads SFPD incident reports from CSV
2. **Data Cleaning**: Removes invalid coordinates and filters recent data
3. **Severity Mapping**: Assigns weights to different crime types
4. **Time Analysis**: Identifies day vs. night incidents

### Safety Grid Creation
1. **Grid Generation**: Creates a spatial grid covering the area
2. **Incident Density**: Calculates incident counts per grid cell
3. **Safety Scoring**: Computes safety scores based on:
   - Number of incidents
   - Average severity
   - Night incident frequency
4. **Score Normalization**: Converts to 0-100 scale

### Route Finding Algorithm
1. **Waypoint Generation**: Creates intermediate points along the route
2. **Cost Calculation**: Combines distance and safety factors
3. **Path Optimization**: Uses Dijkstra's algorithm to find optimal path
4. **Route Analysis**: Calculates statistics and recommendations

### Safety Scoring Formula
```
Safety Score = 100 - (incident_count × 2) - (avg_severity × 3) - (night_incidents × 5)
```

## 🗺️ Usage Examples

### Web Interface
1. **Enter Coordinates**: Input start and end points
2. **Adjust Preferences**: Set safety weight (0-1) and max distance factor
3. **Find Route**: Click "Find Safe Route" to analyze
4. **View Results**: See safety grade, statistics, and recommendations
5. **Interactive Map**: Click "View Interactive Map" for visual route

### Preset Routes
- Golden Gate Park → Fisherman's Wharf
- Mission District → Downtown
- Haight-Ashbury → Castro

### API Usage
```python
from safe_route_finder import SafeRouteFinder

# Initialize
finder = SafeRouteFinder('police_data.csv')

# Find route
route = finder.find_safe_route(
    start_lat=37.7694, start_lng=-122.4862,
    end_lat=37.8087, end_lng=-122.4098,
    safety_weight=0.7
)

# Get analysis
summary = finder.get_route_summary(route)
recommendations = finder.get_safety_recommendations(route)
```

## 📈 Safety Grades

| Grade | Score Range | Description |
|-------|-------------|-------------|
| A+ | 90-100 | Excellent safety, very low incident rate |
| A | 80-89 | Very good safety, low incident rate |
| B | 70-79 | Good safety, moderate incident rate |
| C | 60-69 | Fair safety, some incidents |
| D | 50-59 | Poor safety, high incident rate |
| F | 0-49 | Very poor safety, very high incident rate |

## 🔧 Configuration

### Safety Weight (0-1)
- **0.0**: Prioritize shortest distance
- **0.5**: Balance safety and distance
- **1.0**: Prioritize maximum safety

### Max Distance Factor (1.2-2.0)
- **1.2x**: Route can be 20% longer than direct distance
- **1.5x**: Route can be 50% longer than direct distance
- **2.0x**: Route can be twice the direct distance

## 📁 File Structure

```
safe-route-finder/
├── safe_route_finder.py      # Core route finding logic
├── web_interface.py          # Flask web application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── templates/
│   └── index.html           # Web interface template
├── static/                  # Generated maps and assets
└── Police_Department_Incident_Reports__2018_to_Present_20250621.csv
```

## 🛠️ Technical Details

### Algorithms Used
- **Dijkstra's Algorithm**: For optimal path finding
- **Haversine Formula**: For accurate distance calculations
- **Grid-based Analysis**: For spatial safety scoring
- **Dynamic Programming**: For route optimization

### Data Sources
- **SFPD Incident Reports**: 2018-present police incident data
- **Geographic Boundaries**: San Francisco neighborhood data
- **Time-based Analysis**: Hourly incident patterns

### Performance
- **Grid Resolution**: ~100 meters per cell
- **Data Filtering**: Last 2 years of incidents
- **Real-time Processing**: <5 seconds for typical routes

## 🔒 Safety Considerations

### Limitations
- **Historical Data**: Based on past incidents, not real-time
- **Data Quality**: Depends on police reporting accuracy
- **Geographic Coverage**: Limited to San Francisco
- **Time Sensitivity**: May not reflect current conditions

### Recommendations
- **Use During Day**: Safer conditions in daylight
- **Stay Alert**: Always be aware of surroundings
- **Travel with Others**: Safety in numbers
- **Well-lit Areas**: Prefer illuminated routes at night
- **Emergency Contacts**: Keep emergency numbers handy

## 🤝 Contributing

### Adding New Features
1. **Data Sources**: Integrate additional safety data (street lights, 311 calls)
2. **Algorithms**: Implement alternative routing algorithms
3. **UI Enhancements**: Add mobile app or additional visualizations
4. **Real-time Updates**: Connect to live police data feeds

### Improving Accuracy
1. **Machine Learning**: Train models on incident patterns
2. **Weather Integration**: Consider weather impact on safety
3. **Event Data**: Include special events and their safety impact
4. **Community Feedback**: Incorporate user-reported safety data

## 📞 Support

For questions or issues:
1. Check the documentation above
2. Review the code comments
3. Test with different coordinates
4. Verify data file integrity

## 📄 License

This project is for educational and safety purposes. Please use responsibly and always prioritize personal safety over route optimization.

---

**Disclaimer**: This tool provides safety recommendations based on historical data. Always use common sense and stay alert to your surroundings. The creators are not responsible for any incidents that may occur while using this system. 