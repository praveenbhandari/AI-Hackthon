# BC CrewAI System

A comprehensive AI-powered system using CrewAI agents for research, transit planning, and safety routing with Claude AI integration.

## 🚀 Features

### 🔬 Research & Analysis
- **AI LLMs Research**: Deep analysis of AI language models and trends
- **Claude AI Integration**: Advanced reasoning and insights using Claude 3 Haiku
- **Comprehensive Reporting**: Detailed research reports and analysis

### 🚌 Transit Planning
- **Bay Area Transit**: Real-time route planning using BART and bus schedules
- **Intelligent Routing**: AI-powered route optimization with multiple criteria
- **Schedule Analysis**: Pattern recognition and system insights

### 🛡️ Safety Routing
- **Safety-Aware Routes**: Find safe paths using real incident data
- **Street Network Analysis**: OSMnx integration for accurate routing
- **Safety Scoring**: Location-based safety grades and incident analysis

### 🌐 REST API
- **FastAPI Integration**: Complete REST API for all functionality
- **Structured JSON Responses**: Consistent API responses for frontend integration
- **Comprehensive Testing**: Full test suite for all endpoints

### ⚡ Groq Integration
- **Centralized Configuration**: Easy management of Groq LLM instances
- **Model Selection**: Task-specific and agent-specific LLM optimization
- **Performance Tuning**: Fast, balanced, and powerful model options
- **Error Handling**: Comprehensive validation and status checking

## 📋 Quick Start

### 1. Install Dependencies
```bash
cd bc
uv sync
```

### 2. Set up Groq API Key
```bash
# Option 1: Environment variable
export GROQ_API_KEY="your-groq-api-key-here"

# Option 2: .env file
echo "GROQ_API_KEY=your-groq-api-key-here" > .env
```

### 3. Test Groq Configuration
```bash
python test_groq_config.py
python test_groq_utils.py
python example_groq_usage.py
```

### 4. Start the API Server
```bash
# Method 1: Using launcher script
python run_api.py

# Method 2: Direct execution
python -m bc.api

# Method 3: Using uvicorn
uvicorn bc.api:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Access the System
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Interactive Transit**: `python -m bc.transit_main`

## 🧪 Testing

### Run All Tests
```bash
python test_api.py
```

### Test Individual Components
```bash
# Research crew
python -m bc.main

# Transit crew
python -m bc.main run_transit_crew

# Safety crew
python -m bc.main run_safety_crew

# Full crew
python -m bc.main run_full_crew
```

## 📡 API Endpoints

### Core Endpoints
- **POST** `/research` - AI LLMs research and analysis
- **POST** `/transit` - Bay Area transit planning
- **POST** `/full` - Combined research and transit analysis

### Safety Routing Endpoints
- **POST** `/safety_routes` - Find safe routes between locations
- **POST** `/safety_info` - Get safety information for locations
- **POST** `/incident_data` - Retrieve incident data for visualization
- **POST** `/safety_analysis` - Analyze safety patterns
- **POST** `/route_planning` - Comprehensive route planning

### Information Endpoints
- **GET** `/health` - API health status
- **GET** `/agents` - Agent information
- **GET** `/tasks` - Task information
- **GET** `/tools` - Tool information

## 📁 Project Structure

```
bc/
├── src/bc/
│   ├── api.py                    # Main FastAPI application
│   ├── crew.py                   # CrewAI crew implementations
│   ├── main.py                   # Command-line interface
│   ├── transit_main.py           # Interactive transit system
│   ├── groq_config.py            # Groq LLM configuration
│   ├── groq_utils.py             # Groq utility functions
│   ├── config/
│   │   ├── agents.yaml           # Agent configurations
│   │   └── tasks.yaml            # Task configurations
│   └── tools/
│       ├── transport_tools.py    # Transit planning tools
│       ├── safety_routing_tools.py # Safety routing tools
│       └── custom_tool.py        # Custom tool template
├── run_api.py                    # API launcher script
├── test_api.py                   # Comprehensive test suite
├── test_groq_config.py           # Groq configuration tests
├── test_groq_utils.py            # Groq utilities tests
├── example_groq_usage.py         # Groq usage examples
├── GROQ_CONFIG_README.md         # Detailed Groq documentation
├── pyproject.toml                # Project configuration
└── README.md                     # This file
```

## 🤖 Agents

### Research Agents
- **Researcher**: AI LLMs data research and trend analysis
- **Reporting Analyst**: Report generation and data visualization
- **Claude Agent**: Advanced reasoning and strategic insights

### Transit Agents
- **Transit Planner**: Route planning and schedule analysis
- **Transit Analyst**: Pattern recognition and system insights
- **Route Optimizer**: Multi-criteria route optimization

### Safety Agents
- **Safety Route Finder**: Safe route discovery using incident data
- **Safety Analyst**: Safety pattern analysis and risk assessment
- **Route Planner**: Comprehensive route planning with safety integration

## 🛠️ Tools

### Transit Tools
- **Load Transit Data**: CSV schedule file processing
- **Search Stops**: Location-based stop finding
- **Find Routes**: Route discovery and optimization
- **Get Route Info**: Detailed route information

### Safety Tools
- **Find Safe Route**: Safety-optimized routing with incident data
- **Get Safety Info**: Location safety scoring and analysis
- **Get Incident Data**: Incident data for heatmap visualization

## 📊 Data Files

- **SFO BART Schedule**: `src/sfo_bart_schedule.csv` (34,640+ lines)
- **SFO Bus Schedule**: `src/sfo_bus_schedule.csv`
- **Incident Data**: Police incident reports for safety analysis

## 🔧 Configuration

### Environment Setup
- Python 3.10-3.13
- CrewAI framework
- FastAPI and Uvicorn
- OSMnx for street network analysis
- Pandas for data processing

### Dependencies
```toml
crewai[tools]>=0.130.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
osmnx>=1.3.0
networkx>=3.0
shapely>=2.0.0
pandas>=2.0.0
numpy>=1.24.0
```

## 🚀 Usage Examples

### Research Analysis
```bash
curl -X POST "http://localhost:8000/research" \
  -H "Content-Type: application/json" \
  -d '{"topic": "AI LLMs", "current_year": "2024"}'
```

### Transit Planning
```bash
curl -X POST "http://localhost:8000/transit" \
  -H "Content-Type: application/json" \
  -d '{
    "user_request": "I want to go from Salesforce Transit Center to Richmond BART at 08:00 AM",
    "origin": "Salesforce Transit Center",
    "destination": "Richmond BART",
    "time": "08:00"
  }'
```

### Safety Routing
```bash
curl -X POST "http://localhost:8000/safety_routes" \
  -H "Content-Type: application/json" \
  -d '{
    "start_lat": 37.7694,
    "start_lng": -122.4862,
    "end_lat": 37.8087,
    "end_lng": -122.4098,
    "safety_weight": 0.7
  }'
```

## 🐛 Troubleshooting

### Common Issues
1. **Module Import Errors**: Ensure you're in the correct directory (`cd bc`)
2. **API Not Starting**: Check if port 8000 is available
3. **Missing Dependencies**: Run `uv sync` to install packages
4. **File Not Found**: Verify CSV files exist in `src/` directory

### Debug Mode
```bash
uvicorn bc.api:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## 📈 Performance

- **Research Analysis**: 30-60 seconds for comprehensive analysis
- **Transit Planning**: 10-30 seconds for route optimization
- **Safety Routing**: 2-5 seconds for route calculation
- **API Response**: <1 second for simple endpoints

## 🤝 Contributing

1. Add new tools to appropriate `tools/` files
2. Update agent configurations in `config/agents.yaml`
3. Add task definitions in `config/tasks.yaml`
4. Update crew implementations in `crew.py`
5. Add tests to `test_api.py`

## 📄 License

This project is part of the BC CrewAI system and follows the same licensing terms.

## ⚡ Groq Configuration

The system includes a centralized Groq configuration system for optimal LLM selection:

### Quick Usage
```python
from bc.groq_config import groq_fast, groq_balanced, groq_powerful
from bc.groq_utils import get_agent_llm_config

# Use pre-configured instances
agent = Agent(llm=groq_fast, ...)

# Get LLM for specific agent
config = get_agent_llm_config('transit_planner')
agent = Agent(llm=config['llm'], ...)
```

### Available Models
- **Fast**: `llama-3.1-8b-instant` (~50ms response)
- **Balanced**: `groq/llama3-8b-8192` (~200ms response)  
- **Powerful**: `groq/llama3-70b-8192` (~500ms response)
- **Advanced**: `mixtral-8x7b-32768` (complex reasoning)

### Testing & Examples
```bash
# Test configuration
python test_groq_config.py
python test_groq_utils.py

# Run examples
python example_groq_usage.py

# Check status
python -c "from bc.groq_utils import print_groq_status; print_groq_status()"
```

📖 **For detailed documentation, see [GROQ_CONFIG_README.md](GROQ_CONFIG_README.md)**
