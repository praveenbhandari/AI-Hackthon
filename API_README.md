# BC CrewAI FastAPI API

This document describes the FastAPI endpoints for the BC CrewAI system, providing REST API access to the three different crew types: Research, Transit, and Full Crew.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd bc
uv sync
```

### 2. Start the API Server
```bash
# Method 1: Direct execution
python -m bc.api

# Method 2: Using uvicorn
uvicorn bc.api:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access the API
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📋 API Endpoints

### 🔬 Research Endpoint
**POST** `/research`

Analyzes AI LLMs and provides insights using the research crew.

**Request Body:**
```json
{
  "topic": "AI LLMs",
  "current_year": "2024"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Research crew executed successfully",
  "result": "Research analysis results...",
  "execution_time": 45.23
}
```

### 🚌 Transit Endpoint
**POST** `/transit`

Provides Bay Area transit planning and analysis using the transit crew.

**Request Body:**
```json
{
  "user_request": "I want to go from Salesforce Transit Center to Richmond BART at 08:00 AM",
  "origin": "Salesforce Transit Center",
  "destination": "Richmond BART",
  "time": "08:00",
  "topic": "Bay Area Transit Planning",
  "current_year": "2024"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Transit crew executed successfully",
  "result": "Transit planning results...",
  "execution_time": 67.89
}
```

### 🚀 Full Crew Endpoint
**POST** `/full`

Executes both research and transit tasks using the full crew.

**Request Body:**
```json
{
  "topic": "AI LLMs and Transit Planning",
  "user_request": "Analyze AI LLMs and provide insights about the current state of the technology",
  "origin": "AI Research",
  "destination": "Machine Learning",
  "time": "09:00",
  "current_year": "2024"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Full crew executed successfully",
  "result": "Combined research and transit results...",
  "execution_time": 120.45
}
```

### 🏥 Health Check
**GET** `/health`

Returns the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.123456",
  "service": "BC CrewAI API"
}
```

### 🤖 Agents Information
**GET** `/agents`

Returns information about all available agents.

**Response:**
```json
{
  "agents": {
    "researcher": {
      "role": "AI LLMs Senior Data Researcher",
      "goal": "Uncover cutting-edge developments in AI LLMs",
      "capabilities": ["Research", "Data Analysis", "Trend Identification"]
    },
    "transit_planner": {
      "role": "Bay Area Transit Route Planner",
      "goal": "Help users find optimal public transit routes",
      "capabilities": ["Route Planning", "Schedule Analysis", "User Query Processing"]
    }
    // ... more agents
  }
}
```

### 📋 Tasks Information
**GET** `/tasks`

Returns information about all available tasks.

**Response:**
```json
{
  "tasks": {
    "research": {
      "description": "Conduct thorough research about AI LLMs",
      "output": "List of 10 bullet points with relevant information",
      "agent": "researcher"
    },
    "transit_planning": {
      "description": "Analyze transit requests and find optimal routes",
      "output": "Comprehensive transit plan with multiple options",
      "agent": "transit_planner"
    }
    // ... more tasks
  }
}
```

## 🧪 Testing the API

### Using the Test Script
```bash
cd bc
python test_api.py
```

### Using curl

#### Research Endpoint
```bash
curl -X POST "http://localhost:8000/research" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI LLMs",
    "current_year": "2024"
  }'
```

#### Transit Endpoint
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

#### Full Crew Endpoint
```bash
curl -X POST "http://localhost:8000/full" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI LLMs and Transit Planning",
    "user_request": "Analyze AI LLMs and provide insights about the current state of the technology",
    "origin": "AI Research",
    "destination": "Machine Learning",
    "time": "09:00"
  }'
```

## 📊 Response Format

All endpoints return a standardized response format:

```json
{
  "success": boolean,
  "message": string,
  "result": string | null,
  "error": string | null,
  "execution_time": float | null
}
```

### Response Fields:
- **success**: Whether the operation was successful
- **message**: Human-readable status message
- **result**: The actual result from the crew execution (if successful)
- **error**: Error message (if failed)
- **execution_time**: Time taken to execute the crew in seconds

## 🔧 Configuration

### Environment Variables
- `DEFAULT_SCHEDULE_FILE`: Path to the SFO BART schedule file (default: `./src/sfo_bart_schedule.csv`)

### Server Configuration
- **Host**: 0.0.0.0 (accessible from any IP)
- **Port**: 8000
- **Reload**: Enabled for development
- **Log Level**: info

## 🚨 Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid request parameters
- **500 Internal Server Error**: Crew execution failures
- **Validation Errors**: Automatic Pydantic validation
- **Timeout Handling**: Long-running operations

## 📈 Performance

- **Research Crew**: Typically 30-60 seconds
- **Transit Crew**: Typically 60-120 seconds (includes data loading)
- **Full Crew**: Typically 120-300 seconds

## 🔒 Security Considerations

- Input validation using Pydantic models
- Error message sanitization
- Request size limits
- Execution time monitoring

## 🛠️ Development

### Adding New Endpoints
1. Add new Pydantic models for request/response
2. Create endpoint function with proper error handling
3. Add to the API documentation
4. Update test script

### Debugging
- Enable debug logging: `uvicorn bc.api:app --log-level debug`
- Check crew execution logs in the response
- Monitor execution times for performance issues

## 📚 Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **CrewAI**: Core AI framework
- **Pandas**: Data processing
- **Requests**: HTTP client (for testing)

## 🤝 Contributing

1. Follow FastAPI best practices
2. Add proper error handling
3. Include comprehensive tests
4. Update documentation
5. Maintain backward compatibility 