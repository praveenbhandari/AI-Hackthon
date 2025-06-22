#!/usr/bin/env python
"""
BC CrewAI API - FastAPI server for research, transit, and safety routing
"""
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import os
import sys
import json
import time
from datetime import datetime

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from bc.crew import Bc
except ImportError:
    # Try alternative import paths
    try:
        from crew import Bc
    except ImportError:
        # If running from BC directory
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from bc.crew import Bc

# Default SFO BART schedule file path
DEFAULT_SCHEDULE_FILE = "./src/sfo_bart_schedule.csv"

# Initialize FastAPI app
app = FastAPI(
    title="BC CrewAI API",
    description="API endpoints for BC CrewAI agents - Research, Transit, Safety Routing, and Full Crew",
    version="1.0.0"
)

# Pydantic models for request/response
class ResearchRequest(BaseModel):
    topic: str = "AI LLMs"
    current_year: Optional[str] = None

class TransitRequest(BaseModel):
    user_request: str
    origin: Optional[str] = None
    destination: Optional[str] = None
    time: Optional[str] = None
    schedule_file: Optional[str] = None
    topic: str = "Bay Area Transit Planning"
    current_year: Optional[str] = None

class SafetyRouteRequest(BaseModel):
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    safety_weight: float = 0.7
    max_distance_factor: float = 2.0
    topic: str = "Safety Route Planning"
    current_year: Optional[str] = None

class SafetyInfoRequest(BaseModel):
    lat: float
    lng: float
    radius_meters: int = 500

class IncidentDataRequest(BaseModel):
    limit: int = 1000

class SafetyAnalysisRequest(BaseModel):
    safety_analysis_request: str
    topic: str = "Safety Analysis"
    current_year: Optional[str] = None

class RoutePlanningRequest(BaseModel):
    route_planning_request: str
    user_preferences: str = "Safety-focused, walking preferred"
    safety_requirements: str = "Avoid high-crime areas, well-lit routes"
    start_lat: Optional[float] = None
    start_lng: Optional[float] = None
    end_lat: Optional[float] = None
    end_lng: Optional[float] = None
    safety_weight: float = 0.7
    topic: str = "Route Planning"
    current_year: Optional[str] = None

class FullCrewRequest(BaseModel):
    topic: str = "AI LLMs and Transit Planning"
    current_year: Optional[str] = None
    user_request: str
    origin: Optional[str] = None
    destination: Optional[str] = None
    time: Optional[str] = None
    schedule_file: Optional[str] = None

class AgentResponse(BaseModel):
    success: bool
    message: str
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

class SafetyRouteResponse(BaseModel):
    success: bool
    message: str
    routes: List[Dict[str, Any]]
    best_route: Optional[Dict[str, Any]] = None
    total_routes: int
    execution_time: float
    routing_method: Optional[str] = None
    error: Optional[str] = None

class SafetyInfoResponse(BaseModel):
    success: bool
    message: str
    safety_score: float
    safety_grade: str
    nearby_incidents: int
    radius_meters: int
    location: Dict[str, float]
    execution_time: float
    error: Optional[str] = None

class IncidentDataResponse(BaseModel):
    success: bool
    message: str
    incidents: List[Dict[str, float]]
    total_incidents: int
    limit: int
    execution_time: float
    error: Optional[str] = None

class RoutePlanningResponse(BaseModel):
    success: bool
    message: str
    route_plan: Dict[str, Any]
    recommendations: List[str]
    safety_analysis: Dict[str, Any]
    execution_time: float
    error: Optional[str] = None

# Helper function to prepare inputs
def prepare_inputs(request_data: Dict[str, Any], request_type: str) -> Dict[str, Any]:
    """Prepare inputs for crew execution"""
    inputs = {
        'topic': request_data.get('topic', 'AI LLMs'),
        'current_year': request_data.get('current_year', str(datetime.now().year))
    }
    
    if request_type in ['transit', 'full']:
        inputs.update({
            'user_request': request_data.get('user_request', ''),
            'schedule_file': request_data.get('schedule_file', DEFAULT_SCHEDULE_FILE),
            'origin': request_data.get('origin', ''),
            'destination': request_data.get('destination', ''),
            'time': request_data.get('time', '09:00')
        })
    
    return inputs

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "BC CrewAI API",
        "version": "1.0.0",
        "endpoints": {
            "research": "/research - Research crew (AI LLMs analysis)",
            "transit": "/transit - Transit crew (Bay Area transit planning)",
            "safety_routes": "/safety_routes - Find safe routes between locations",
            "safety_info": "/safety_info - Get safety information for a location",
            "incident_data": "/incident_data - Get incident data for visualization",
            "safety_analysis": "/safety_analysis - Analyze safety patterns",
            "route_planning": "/route_planning - Create comprehensive route plans",
            "full": "/full - Full crew (Research + Transit)",
            "health": "/health - Health check",
            "agents": "/agents - Agent information",
            "tasks": "/tasks - Task information",
            "tools": "/tools - Tool information"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "BC CrewAI API",
        "version": "1.0.0"
    }

@app.post("/research", response_model=AgentResponse)
async def research_endpoint(request: ResearchRequest):
    """
    Research crew endpoint - Analyzes AI LLMs and provides insights
    """
    start_time = time.time()
    
    try:
        # Prepare inputs
        inputs = prepare_inputs(request.dict(), 'research')
        
        # Execute research crew
        crew_instance = Bc()
        result = crew_instance.crew().kickoff(inputs=inputs)
        
        execution_time = time.time() - start_time
        
        return AgentResponse(
            success=True,
            message="Research crew executed successfully",
            result=str(result),
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return AgentResponse(
            success=False,
            message="Research crew execution failed",
            error=str(e),
            execution_time=execution_time
        )

@app.post("/transit", response_model=AgentResponse)
async def transit_endpoint(request: TransitRequest):
    """
    Transit crew endpoint - Provides Bay Area transit planning and analysis
    """
    start_time = time.time()
    
    try:
        # Validate required fields
        if not request.user_request:
            raise HTTPException(status_code=400, detail="user_request is required")
        
        # Prepare inputs
        inputs = prepare_inputs(request.dict(), 'transit')
        
        # Execute transit crew
        crew_instance = Bc()
        result = crew_instance.transit_crew().kickoff(inputs=inputs)
        
        execution_time = time.time() - start_time
        
        return AgentResponse(
            success=True,
            message="Transit crew executed successfully",
            result=str(result),
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return AgentResponse(
            success=False,
            message="Transit crew execution failed",
            error=str(e),
            execution_time=execution_time
        )

@app.post("/safety_routes", response_model=SafetyRouteResponse)
async def safety_routes_endpoint(request: SafetyRouteRequest):
    """
    Find safe routes between two locations using incident data and street network analysis
    """
    start_time = time.time()
    
    try:
        # Validate coordinates
        if not (-90 <= request.start_lat <= 90) or not (-180 <= request.start_lng <= 180):
            raise HTTPException(status_code=400, detail="Invalid start coordinates")
        if not (-90 <= request.end_lat <= 90) or not (-180 <= request.end_lng <= 180):
            raise HTTPException(status_code=400, detail="Invalid end coordinates")
        if not (0 <= request.safety_weight <= 1):
            raise HTTPException(status_code=400, detail="Safety weight must be between 0 and 1")
        
        # Prepare inputs for safety crew
        inputs = {
            'topic': request.topic,
            'current_year': request.current_year or str(datetime.now().year),
            'start_lat': request.start_lat,
            'start_lng': request.start_lng,
            'end_lat': request.end_lat,
            'end_lng': request.end_lng,
            'safety_weight': request.safety_weight,
            'safety_analysis_request': f"Analyze safety for route from ({request.start_lat}, {request.start_lng}) to ({request.end_lat}, {request.end_lng})",
            'route_planning_request': f"Find safe route from ({request.start_lat}, {request.start_lng}) to ({request.end_lat}, {request.end_lng})",
            'user_preferences': "Safety-focused, walking preferred",
            'safety_requirements': "Avoid high-crime areas, well-lit routes"
        }
        
        # Execute safety crew
        crew_instance = Bc()
        result = crew_instance.safety_crew().kickoff(inputs=inputs)
        
        execution_time = time.time() - start_time
        
        # Try to parse the result as JSON
        try:
            if isinstance(result, str):
                result_data = json.loads(result)
            else:
                result_data = result
            
            return SafetyRouteResponse(
                success=True,
                message="Safe routes found successfully",
                routes=result_data.get('routes', []),
                best_route=result_data.get('best_route'),
                total_routes=result_data.get('total_routes', 0),
                execution_time=execution_time,
                routing_method=result_data.get('routing_method', 'osmnx_safety_optimized')
            )
            
        except (json.JSONDecodeError, TypeError):
            # Fallback response if JSON parsing fails
            return SafetyRouteResponse(
                success=True,
                message="Routes found (parsing limited)",
                routes=[],
                total_routes=0,
                execution_time=execution_time,
                routing_method="crewai_safety_optimized"
            )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return SafetyRouteResponse(
            success=False,
            message="Safety routes execution failed",
            routes=[],
            total_routes=0,
            execution_time=execution_time,
            routing_method="error",
            error=str(e)
        )

@app.post("/safety_info", response_model=SafetyInfoResponse)
async def safety_info_endpoint(request: SafetyInfoRequest):
    """
    Get safety information for a specific location
    """
    start_time = time.time()
    
    try:
        # Validate coordinates
        if not (-90 <= request.lat <= 90) or not (-180 <= request.lng <= 180):
            raise HTTPException(status_code=400, detail="Invalid coordinates")
        if request.radius_meters <= 0:
            raise HTTPException(status_code=400, detail="Radius must be positive")
        
        # Import safety tools directly
        try:
            from bc.tools.safety_routing_tools import GetSafetyInfoTool
        except ImportError:
            # Try alternative import path
            try:
                from tools.safety_routing_tools import GetSafetyInfoTool
            except ImportError:
                # Try alternative import path
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
                from safety_routing_tools import GetSafetyInfoTool
        
        # Create tool and get safety info
        tool = GetSafetyInfoTool()
        result = tool._run(request.lat, request.lng, request.radius_meters)
        
        execution_time = time.time() - start_time
        
        # Parse result
        try:
            result_data = json.loads(result)
            return SafetyInfoResponse(
                success=result_data.get('success', True),
                message="Safety information retrieved successfully",
                safety_score=result_data.get('safety_score', 0.0),
                safety_grade=result_data.get('safety_grade', 'C'),
                nearby_incidents=result_data.get('nearby_incidents', 0),
                radius_meters=result_data.get('radius_meters', request.radius_meters),
                location=result_data.get('location', {'lat': request.lat, 'lng': request.lng}),
                execution_time=execution_time
            )
        except (json.JSONDecodeError, TypeError):
            return SafetyInfoResponse(
                success=False,
                message="Failed to parse safety information",
                safety_score=0.0,
                safety_grade='C',
                nearby_incidents=0,
                radius_meters=request.radius_meters,
                location={'lat': request.lat, 'lng': request.lng},
                execution_time=execution_time,
                error="JSON parsing failed"
            )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return SafetyInfoResponse(
            success=False,
            message="Safety info execution failed",
            safety_score=0.0,
            safety_grade='C',
            nearby_incidents=0,
            radius_meters=request.radius_meters,
            location={'lat': request.lat, 'lng': request.lng},
            execution_time=execution_time,
            error=str(e)
        )

@app.post("/incident_data", response_model=IncidentDataResponse)
async def incident_data_endpoint(request: IncidentDataRequest):
    """
    Get incident data for heatmap visualization
    """
    start_time = time.time()
    
    try:
        if request.limit <= 0:
            raise HTTPException(status_code=400, detail="Limit must be positive")
        if request.limit > 10000:
            raise HTTPException(status_code=400, detail="Limit cannot exceed 10000")
        
        # Import safety tools directly
        try:
            from bc.tools.safety_routing_tools import GetIncidentDataTool
        except ImportError:
            # Try alternative import path
            try:
                from tools.safety_routing_tools import GetIncidentDataTool
            except ImportError:
                # Try alternative import path
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
                from safety_routing_tools import GetIncidentDataTool
        
        # Create tool and get incident data
        tool = GetIncidentDataTool()
        result = tool._run(request.limit)
        
        execution_time = time.time() - start_time
        
        # Parse result
        try:
            result_data = json.loads(result)
            return IncidentDataResponse(
                success=result_data.get('success', True),
                message="Incident data retrieved successfully",
                incidents=result_data.get('incidents', []),
                total_incidents=result_data.get('total_incidents', 0),
                limit=result_data.get('limit', request.limit),
                execution_time=execution_time
            )
        except (json.JSONDecodeError, TypeError):
            return IncidentDataResponse(
                success=False,
                message="Failed to parse incident data",
                incidents=[],
                total_incidents=0,
                limit=request.limit,
                execution_time=execution_time,
                error="JSON parsing failed"
            )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return IncidentDataResponse(
            success=False,
            message="Incident data execution failed",
            incidents=[],
            total_incidents=0,
            limit=request.limit,
            execution_time=execution_time,
            error=str(e)
        )

@app.post("/safety_analysis", response_model=AgentResponse)
async def safety_analysis_endpoint(request: SafetyAnalysisRequest):
    """
    Safety analysis endpoint - Analyze safety patterns
    """
    start_time = time.time()
    
    try:
        # Prepare inputs
        inputs = {
            'topic': request.topic,
            'current_year': request.current_year or str(datetime.now().year),
            'safety_analysis_request': request.safety_analysis_request
        }
        
        # Execute safety crew
        crew_instance = Bc()
        result = crew_instance.safety_crew().kickoff(inputs=inputs)
        
        execution_time = time.time() - start_time
        
        return AgentResponse(
            success=True,
            message="Safety analysis completed successfully",
            result=str(result),
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return AgentResponse(
            success=False,
            message="Safety analysis execution failed",
            error=str(e),
            execution_time=execution_time
        )

@app.post("/route_planning", response_model=RoutePlanningResponse)
async def route_planning_endpoint(request: RoutePlanningRequest):
    """
    Create comprehensive route plans with safety analysis
    """
    start_time = time.time()
    
    try:
        # Validate coordinates if provided
        if request.start_lat is not None and request.start_lng is not None:
            if not (-90 <= request.start_lat <= 90) or not (-180 <= request.start_lng <= 180):
                raise HTTPException(status_code=400, detail="Invalid start coordinates")
        if request.end_lat is not None and request.end_lng is not None:
            if not (-90 <= request.end_lat <= 90) or not (-180 <= request.end_lng <= 180):
                raise HTTPException(status_code=400, detail="Invalid end coordinates")
        if not (0 <= request.safety_weight <= 1):
            raise HTTPException(status_code=400, detail="Safety weight must be between 0 and 1")
        
        # Prepare inputs for safety crew
        inputs = {
            'topic': request.topic,
            'current_year': request.current_year or str(datetime.now().year),
            'route_planning_request': request.route_planning_request,
            'user_preferences': request.user_preferences,
            'safety_requirements': request.safety_requirements,
            'safety_weight': request.safety_weight
        }
        
        # Add coordinates if provided
        if request.start_lat is not None:
            inputs['start_lat'] = request.start_lat
        if request.start_lng is not None:
            inputs['start_lng'] = request.start_lng
        if request.end_lat is not None:
            inputs['end_lat'] = request.end_lat
        if request.end_lng is not None:
            inputs['end_lng'] = request.end_lng
        
        # Execute safety crew
        crew_instance = Bc()
        result = crew_instance.safety_crew().kickoff(inputs=inputs)
        
        execution_time = time.time() - start_time
        
        # Try to parse the result as JSON
        try:
            if isinstance(result, str):
                result_data = json.loads(result)
            else:
                result_data = result
            
            return RoutePlanningResponse(
                success=True,
                message="Route planning completed successfully",
                route_plan=result_data.get('route_plan', {}),
                recommendations=result_data.get('recommendations', []),
                safety_analysis=result_data.get('safety_analysis', {}),
                execution_time=execution_time
            )
            
        except (json.JSONDecodeError, TypeError):
            # Fallback response if JSON parsing fails
            return RoutePlanningResponse(
                success=True,
                message="Route planning completed (parsing limited)",
                route_plan={},
                recommendations=["Use safety-focused routing", "Avoid high-crime areas"],
                safety_analysis={},
                execution_time=execution_time
            )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return RoutePlanningResponse(
            success=False,
            message="Route planning execution failed",
            route_plan={},
            recommendations=[],
            safety_analysis={},
            execution_time=execution_time,
            error=str(e)
        )

@app.post("/full", response_model=AgentResponse)
async def full_crew_endpoint(request: FullCrewRequest):
    """
    Full crew endpoint - Executes both research and transit tasks
    """
    start_time = time.time()
    
    try:
        # Validate required fields
        if not request.user_request:
            raise HTTPException(status_code=400, detail="user_request is required")
        
        # Prepare inputs
        inputs = prepare_inputs(request.dict(), 'full')
        
        # Execute full crew
        crew_instance = Bc()
        result = crew_instance.full_crew().kickoff(inputs=inputs)
        
        execution_time = time.time() - start_time
        
        return AgentResponse(
            success=True,
            message="Full crew executed successfully",
            result=str(result),
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return AgentResponse(
            success=False,
            message="Full crew execution failed",
            error=str(e),
            execution_time=execution_time
        )

@app.get("/agents")
async def get_agents_info():
    """Get information about available agents"""
    return {
        "agents": {
            "researcher": {
                "role": "AI LLMs Senior Data Researcher",
                "goal": "Uncover cutting-edge developments in AI LLMs",
                "capabilities": ["Research", "Data Analysis", "Trend Identification"]
            },
            "reporting_analyst": {
                "role": "AI LLMs Reporting Analyst",
                "goal": "Create detailed reports based on AI LLMs data analysis",
                "capabilities": ["Report Generation", "Data Visualization", "Insight Synthesis"]
            },
            "claude_agent": {
                "role": "AI LLMs Claude AI Specialist",
                "goal": "Provide expert analysis using Claude's advanced reasoning",
                "capabilities": ["Deep Analysis", "Strategic Insights", "Future Scenarios"]
            },
            "transit_planner": {
                "role": "Bay Area Transit Route Planner",
                "goal": "Help users find optimal public transit routes",
                "capabilities": ["Route Planning", "Schedule Analysis", "User Query Processing"]
            },
            "transit_analyst": {
                "role": "Transit Data Analyst",
                "goal": "Analyze transit patterns and provide insights",
                "capabilities": ["Pattern Recognition", "System Analysis", "Trend Identification"]
            },
            "route_optimizer": {
                "role": "Route Optimization Specialist",
                "goal": "Find most efficient and cost-effective routes",
                "capabilities": ["Multi-criteria Optimization", "Cost Analysis", "Accessibility Assessment"]
            },
            "safety_route_finder": {
                "role": "Safety Route Finder",
                "goal": "Find safe routes between locations using incident data and street network analysis",
                "capabilities": ["Route Finding", "Safety Analysis", "Street Network Integration"]
            },
            "safety_analyst": {
                "role": "Safety Data Analyst",
                "goal": "Analyze safety patterns and provide insights about route security",
                "capabilities": ["Pattern Recognition", "Risk Assessment", "Safety Scoring"]
            },
            "route_planner": {
                "role": "Intelligent Route Planner",
                "goal": "Create comprehensive route plans with safety, efficiency, and user preferences",
                "capabilities": ["Route Planning", "Safety Integration", "User Preferences"]
            }
        }
    }

@app.get("/tasks")
async def get_tasks_info():
    """Get information about available tasks"""
    return {
        "tasks": {
            "research": {
                "description": "Conduct thorough research about AI LLMs",
                "output": "List of 10 bullet points with relevant information",
                "agent": "researcher"
            },
            "reporting": {
                "description": "Create detailed reports based on research findings",
                "output": "Comprehensive report in markdown format",
                "agent": "reporting_analyst"
            },
            "claude_analysis": {
                "description": "Deep analysis using Claude's reasoning capabilities",
                "output": "Strategic insights and recommendations",
                "agent": "claude_agent"
            },
            "transit_planning": {
                "description": "Analyze transit requests and find optimal routes",
                "output": "Comprehensive transit plan with multiple options",
                "agent": "transit_planner"
            },
            "transit_analysis": {
                "description": "Analyze transit system patterns and insights",
                "output": "Detailed transit analysis report",
                "agent": "transit_analyst"
            },
            "route_optimization": {
                "description": "Find most efficient transit routes",
                "output": "Optimized route recommendations",
                "agent": "route_optimizer"
            },
            "safety_route_finding": {
                "description": "Find safe routes between locations using incident data and street network analysis",
                "output": "Structured JSON with route options and safety metrics",
                "agent": "safety_route_finder"
            },
            "safety_analysis": {
                "description": "Analyze safety patterns and provide insights about route security",
                "output": "Comprehensive safety analysis with recommendations",
                "agent": "safety_analyst"
            },
            "route_planning": {
                "description": "Create comprehensive route plans with safety, efficiency, and user preferences",
                "output": "Structured JSON with route plans and safety analysis",
                "agent": "route_planner"
            }
        }
    }

@app.get("/tools")
async def get_tools_info():
    """Get information about available tools"""
    return {
        "tools": {
            "find_safe_route": {
                "description": "Find safe routes between two locations using incident data and street network analysis",
                "parameters": ["start_lat", "start_lng", "end_lat", "end_lng", "safety_weight"],
                "output": "JSON with route options and safety metrics"
            },
            "get_safety_info": {
                "description": "Get safety information for a specific location including safety score and nearby incidents",
                "parameters": ["lat", "lng", "radius_meters"],
                "output": "JSON with safety score, grade, and incident count"
            },
            "get_incident_data": {
                "description": "Get incident data for heatmap visualization and analysis",
                "parameters": ["limit"],
                "output": "JSON with incident coordinates for mapping"
            },
            "transit_tools": {
                "description": "Transit schedule analysis and route finding tools",
                "parameters": ["schedule_file", "origin", "destination", "time"],
                "output": "Transit route information and analysis"
            }
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "bc.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 