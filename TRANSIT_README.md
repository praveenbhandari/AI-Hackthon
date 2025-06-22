# Bay Area Transit CrewAI System

This project integrates transit planning functionality into your CrewAI setup, using Claude AI agents to provide intelligent route planning and analysis for the San Francisco Bay Area public transportation system.

## Features

### 🚌 Transit Planning Agents
- **Transit Planner**: Expert route planning using real schedule data
- **Transit Analyst**: System analysis and pattern recognition
- **Route Optimizer**: Advanced route optimization with multiple criteria

### 🛠️ Transit Tools
- **Load Transit Data**: Load and validate transit schedule CSV files
- **Search Stops**: Find transit stops by location name
- **Find Transit Routes**: Get route options between origin and destination
- **Get Route Info**: Detailed information about specific routes

### 🤖 Claude AI Integration
All transit agents use Claude 3 Haiku for advanced reasoning and analysis, providing:
- Intelligent route recommendations
- Pattern analysis and insights
- Cost-benefit analysis
- Accessibility considerations
- Personalized recommendations

## Quick Start

### 1. Install Dependencies
```bash
cd bc
uv sync
```

### 2. Run Transit System
```bash
# Run the interactive transit system
python -m bc.transit_main

# Or use the script entry point
transit
```

### 3. Choose Your Operation
The system offers four main operations:

1. **Transit Planning**: Route planning with user queries
2. **Transit Analysis**: System insights and pattern analysis
3. **Route Optimization**: Advanced route optimization
4. **Full Transit Crew**: Complete analysis with all agents

## Sample Usage

### Transit Planning Example
```
Enter your transit query: I want to go from CSU East Bay to Hayward BART at 11:00 AM
Enter the path to your transit schedule CSV file: sample_transit_schedule.csv
```

### Route Optimization Example
```
Enter origin location: CSU East Bay
Enter destination location: UC Berkeley
Enter departure time: 08:00
Enter the path to your transit schedule CSV file: sample_transit_schedule.csv
```

## Data Format

The system expects transit schedule data in CSV format with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| route_id | Unique route identifier | 1 |
| route_short_name | Short route name | AC |
| route_long_name | Full route description | AC Transit Express |
| trip_id | Unique trip identifier | 2_001 |
| stop_sequence | Stop order in trip | 1 |
| stop_id | Unique stop identifier | 2001 |
| stop_name | Stop name | CSU East Bay |
| arrival_time | Arrival time (HH:MM:SS) | 07:00:00 |
| departure_time | Departure time (HH:MM:SS) | 07:05:00 |

## File Structure

```
bc/
├── src/bc/
│   ├── tools/
│   │   ├── transport_tools.py    # Transit tools implementation
│   │   └── __init__.py           # Tool exports
│   ├── config/
│   │   ├── agents.yaml           # Agent configurations
│   │   └── tasks.yaml            # Task configurations
│   ├── crew.py                   # Main crew implementation
│   ├── main.py                   # Original main file
│   └── transit_main.py           # Transit-specific main file
├── sample_transit_schedule.csv   # Sample data file
└── TRANSIT_README.md             # This file
```

## Agent Roles

### Transit Planner
- **Role**: Bay Area Transit Route Planner
- **Goal**: Help users find optimal public transit routes
- **Capabilities**: Route planning, schedule analysis, user query processing

### Transit Analyst
- **Role**: Transit Data Analyst
- **Goal**: Analyze transit patterns and provide insights
- **Capabilities**: Pattern recognition, system analysis, trend identification

### Route Optimizer
- **Role**: Route Optimization Specialist
- **Goal**: Find most efficient and cost-effective routes
- **Capabilities**: Multi-criteria optimization, cost analysis, accessibility assessment

## Output Files

The system generates several output files:
- `transit_plan.md`: Route planning results
- `transit_analysis.md`: System analysis insights
- `route_optimization.md`: Optimized route recommendations

## Configuration

### Agent Configuration (`config/agents.yaml`)
Each agent has configurable roles, goals, and backstories that can be customized for specific use cases.

### Task Configuration (`config/tasks.yaml`)
Tasks define the specific operations each agent performs, including descriptions and expected outputs.

## Dependencies

- **crewai**: Core CrewAI framework
- **pandas**: Data processing and analysis
- **numpy**: Numerical computations
- **anthropic/claude-3-haiku**: Claude AI model for reasoning

## Troubleshooting

### Common Issues

1. **CSV File Not Found**: Ensure the transit schedule file exists and is in the correct format
2. **Missing Dependencies**: Run `uv sync` to install all required packages
3. **Invalid Time Format**: Use 24-hour format (HH:MM) for departure times

### Error Messages

- `❌ Failed to load transit data`: Check CSV file path and format
- `❌ No stops found`: Verify stop names in the schedule data
- `❌ No direct routes found`: Try different times or locations

## Contributing

To add new transit features:

1. Add new tools to `tools/transport_tools.py`
2. Update agent configurations in `config/agents.yaml`
3. Add task definitions in `config/tasks.yaml`
4. Update the crew implementation in `crew.py`

## License

This project is part of the BC CrewAI system and follows the same licensing terms. 