#!/usr/bin/env python
"""
FastAPI endpoints for BC CrewAI crew operations with safety routing integration
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import os
from datetime import datetime
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

from .crew import Bc
from google_maps_router import GoogleMapsRouter

# Initialize FastAPI app
app = FastAPI(
    title="BC CrewAI Crew API",
    description="Crew operations endpoints for BC CrewAI with safety routing integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000","*"],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize the Google Maps router for safety routing
print("Initializing safety router for crew operations...")
safety_router = GoogleMapsRouter('Police_Department_Incident_Reports__2018_to_Present_20250621.csv')
print("Safety router initialized successfully!")

# Pydantic models for request/response
class CrewExecutionRequest(BaseModel):
    topic: str = "AI LLMs"
    current_year: Optional[str] = None
    user_request: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    time: Optional[str] = None
    schedule_file: Optional[str] = None
    crew_type: str = "research"  # research, transit, full
    safety_weight: float = 0.7
    max_distance_factor: float = 2.0

class SafetyRouteRequest(BaseModel):
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    safety_weight: float = 0.7
    max_distance_factor: float = 2.0

class CrewResponse(BaseModel):
    success: bool
    message: str
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    crew_type: Optional[str] = None
    agents_used: Optional[List[str]] = None
    tasks_executed: Optional[List[str]] = None

class SafetyRouteResponse(BaseModel):
    success: bool
    message: str
    route: Optional[Dict[str, Any]] = None
    all_options: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

class CrewStatusResponse(BaseModel):
    crew_type: str
    status: str
    last_execution: Optional[str] = None
    execution_count: int = 0
    total_execution_time: float = 0.0

# Global state for crew execution tracking
crew_execution_history = {}

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    import numpy as np
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "BC CrewAI Crew API",
        "version": "1.0.0",
        "endpoints": {
            "crews": {
                "research": "/crews/research - Research crew (AI LLMs analysis)",
                "transit": "/crews/transit - Transit crew (Bay Area transit planning)",
                "full": "/crews/full - Full crew (Research + Transit)",
                "custom": "/crews/custom - Custom crew with specific agents"
            },
            "safety_routing": {
                "find_route": "/safety/route - Find safe route between two points",
                "safety_info": "/safety/info - Get safety information for location"
            },
            "status": "/status - Get crew execution status",
            "health": "/health - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "BC CrewAI Crew API",
        "safety_router_available": safety_router is not None
    }

@app.get("/status")
async def get_crew_status():
    """Get status of all crews"""
    return {
        "crews": crew_execution_history,
        "total_executions": sum(history.get("execution_count", 0) for history in crew_execution_history.values()),
        "total_execution_time": sum(history.get("total_execution_time", 0.0) for history in crew_execution_history.values()),
        "timestamp": datetime.now().isoformat()
    }

# Crew Execution Endpoints
@app.post("/crews/research", response_model=CrewResponse)
async def research_crew(request: CrewExecutionRequest):
    """Execute the research crew"""
    start_time = time.time()
    
    try:
        # Prepare inputs
        inputs = {
            'topic': request.topic,
            'current_year': request.current_year or str(datetime.now().year)
        }
        
        # Execute research crew
        crew_instance = Bc()
        crew = crew_instance.crew()
        result = crew.kickoff(inputs=inputs)
        
        execution_time = time.time() - start_time
        
        # Update execution history
        crew_type = "research"
        if crew_type not in crew_execution_history:
            crew_execution_history[crew_type] = {
                "execution_count": 0, 
                "last_execution": None,
                "total_execution_time": 0.0
            }
        crew_execution_history[crew_type]["execution_count"] += 1
        crew_execution_history[crew_type]["last_execution"] = datetime.now().isoformat()
        crew_execution_history[crew_type]["total_execution_time"] += execution_time
        
        return CrewResponse(
            success=True,
            message="Research crew executed successfully",
            result=str(result),
            execution_time=execution_time,
            crew_type=crew_type,
            agents_used=["researcher", "reporting_analyst", "claude_agent"],
            tasks_executed=["research_task", "reporting_task", "claude_analysis_task"]
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return CrewResponse(
            success=False,
            message="Research crew execution failed",
            error=str(e),
            execution_time=execution_time,
            crew_type="research"
        )

@app.post("/crews/transit", response_model=CrewResponse)
async def transit_crew(request: CrewExecutionRequest):
    """Execute the transit crew"""
    start_time = time.time()
    
    try:
        # Validate required fields
        if not request.user_request:
            raise HTTPException(status_code=400, detail="user_request is required")
        
        # Prepare inputs
        inputs = {
            'topic': request.topic,
            'current_year': request.current_year or str(datetime.now().year),
            'user_request': request.user_request,
            'schedule_file': request.schedule_file or "./src/sfo_bart_schedule.csv",
            'origin': request.origin or '',
            'destination': request.destination or '',
            'time': request.time or '09:00'
        }
        
        # Execute transit crew
        crew_instance = Bc()
        crew = crew_instance.transit_crew()
        result = crew.kickoff(inputs=inputs)
        
        execution_time = time.time() - start_time
        
        # Update execution history
        crew_type = "transit"
        if crew_type not in crew_execution_history:
            crew_execution_history[crew_type] = {
                "execution_count": 0, 
                "last_execution": None,
                "total_execution_time": 0.0
            }
        crew_execution_history[crew_type]["execution_count"] += 1
        crew_execution_history[crew_type]["last_execution"] = datetime.now().isoformat()
        crew_execution_history[crew_type]["total_execution_time"] += execution_time
        
        return CrewResponse(
            success=True,
            message="Transit crew executed successfully",
            result=str(result),
            execution_time=execution_time,
            crew_type=crew_type,
            agents_used=["transit_planner", "transit_analyst", "route_optimizer"],
            tasks_executed=["transit_planning_task", "transit_analysis_task", "route_optimization_task"]
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return CrewResponse(
            success=False,
            message="Transit crew execution failed",
            error=str(e),
            execution_time=execution_time,
            crew_type="transit"
        )

@app.post("/crews/full", response_model=CrewResponse)
async def full_crew(request: CrewExecutionRequest):
    """Execute the full crew (research + transit)"""
    start_time = time.time()
    
    try:
        # Validate required fields
        if not request.user_request:
            raise HTTPException(status_code=400, detail="user_request is required")
        
        # Prepare inputs
        inputs = {
            'topic': request.topic,
            'current_year': request.current_year or str(datetime.now().year),
            'user_request': request.user_request,
            'schedule_file': request.schedule_file or "./src/sfo_bart_schedule.csv",
            'origin': request.origin or '',
            'destination': request.destination or '',
            'time': request.time or '09:00'
        }
        
        # Execute full crew
        crew_instance = Bc()
        crew = crew_instance.full_crew()
        result = crew.kickoff(inputs=inputs)
        
        execution_time = time.time() - start_time
        
        # Update execution history
        crew_type = "full"
        if crew_type not in crew_execution_history:
            crew_execution_history[crew_type] = {
                "execution_count": 0, 
                "last_execution": None,
                "total_execution_time": 0.0
            }
        crew_execution_history[crew_type]["execution_count"] += 1
        crew_execution_history[crew_type]["last_execution"] = datetime.now().isoformat()
        crew_execution_history[crew_type]["total_execution_time"] += execution_time
        
        return CrewResponse(
            success=True,
            message="Full crew executed successfully",
            result=str(result),
            execution_time=execution_time,
            crew_type=crew_type,
            agents_used=[
                "researcher", "reporting_analyst", "claude_agent",
                "transit_planner", "transit_analyst", "route_optimizer"
            ],
            tasks_executed=[
                "research_task", "reporting_task", "claude_analysis_task",
                "transit_planning_task", "transit_analysis_task", "route_optimization_task"
            ]
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return CrewResponse(
            success=False,
            message="Full crew execution failed",
            error=str(e),
            execution_time=execution_time,
            crew_type="full"
        )

@app.post("/crews/custom", response_model=CrewResponse)
async def custom_crew(request: Dict[str, Any]):
    """Execute a custom crew with specific agents and tasks"""
    start_time = time.time()
    
    try:
        # Validate required fields
        if 'agents' not in request or 'tasks' not in request:
            raise HTTPException(status_code=400, detail="agents and tasks are required")
        
        agents_list = request['agents']
        tasks_list = request['tasks']
        inputs = request.get('inputs', {})
        
        # Validate agents and tasks
        valid_agents = [
            "researcher", "reporting_analyst", "claude_agent",
            "transit_planner", "transit_analyst", "route_optimizer"
        ]
        
        valid_tasks = [
            "research_task", "reporting_task", "claude_analysis_task",
            "transit_planning_task", "transit_analysis_task", "route_optimization_task"
        ]
        
        for agent in agents_list:
            if agent not in valid_agents:
                raise HTTPException(status_code=400, detail=f"Invalid agent: {agent}")
        
        for task in tasks_list:
            if task not in valid_tasks:
                raise HTTPException(status_code=400, detail=f"Invalid task: {task}")
        
        # Create custom crew
        crew_instance = Bc()
        
        # Get requested agents
        crew_agents = []
        for agent_name in agents_list:
            if agent_name == "researcher":
                crew_agents.append(crew_instance.researcher())
            elif agent_name == "reporting_analyst":
                crew_agents.append(crew_instance.reporting_analyst())
            elif agent_name == "claude_agent":
                crew_agents.append(crew_instance.claude_agent())
            elif agent_name == "transit_planner":
                crew_agents.append(crew_instance.transit_planner())
            elif agent_name == "transit_analyst":
                crew_agents.append(crew_instance.transit_analyst())
            elif agent_name == "route_optimizer":
                crew_agents.append(crew_instance.route_optimizer())
        
        # Get requested tasks
        crew_tasks = []
        for task_name in tasks_list:
            if task_name == "research_task":
                crew_tasks.append(crew_instance.research_task())
            elif task_name == "reporting_task":
                crew_tasks.append(crew_instance.reporting_task())
            elif task_name == "claude_analysis_task":
                crew_tasks.append(crew_instance.claude_analysis_task())
            elif task_name == "transit_planning_task":
                crew_tasks.append(crew_instance.transit_planning_task())
            elif task_name == "transit_analysis_task":
                crew_tasks.append(crew_instance.transit_analysis_task())
            elif task_name == "route_optimization_task":
                crew_tasks.append(crew_instance.route_optimization_task())
        
        # Create and execute custom crew
        from crewai import Crew, Process
        custom_crew = Crew(
            agents=crew_agents,
            tasks=crew_tasks,
            process=Process.sequential,
            verbose=True
        )
        
        result = custom_crew.kickoff(inputs=inputs)
        
        execution_time = time.time() - start_time
        
        # Update execution history
        crew_type = "custom"
        if crew_type not in crew_execution_history:
            crew_execution_history[crew_type] = {
                "execution_count": 0, 
                "last_execution": None,
                "total_execution_time": 0.0
            }
        crew_execution_history[crew_type]["execution_count"] += 1
        crew_execution_history[crew_type]["last_execution"] = datetime.now().isoformat()
        crew_execution_history[crew_type]["total_execution_time"] += execution_time
        
        return CrewResponse(
            success=True,
            message="Custom crew executed successfully",
            result=str(result),
            execution_time=execution_time,
            crew_type=crew_type,
            agents_used=agents_list,
            tasks_executed=tasks_list
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return CrewResponse(
            success=False,
            message="Custom crew execution failed",
            error=str(e),
            execution_time=execution_time,
            crew_type="custom"
        )

# Safety Routing Endpoints
@app.post("/safety/route", response_model=SafetyRouteResponse)
async def find_safe_route(request: SafetyRouteRequest):
    """Find a safe route between two points"""
    start_time = time.time()
    
    try:
        print(f"Finding safe route from ({request.start_lat:.4f}, {request.start_lng:.4f}) to ({request.end_lat:.4f}, {request.end_lng:.4f})")
        
        # Find route using safety router
        result = safety_router.find_google_route(
            request.start_lat, request.start_lng, 
            request.end_lat, request.end_lng,
            safety_weight=request.safety_weight,
            max_distance_factor=request.max_distance_factor
        )
        
        execution_time = time.time() - start_time
        
        if not result['success']:
            return SafetyRouteResponse(
                success=False,
                message="Failed to find safe route",
                error=result.get('error', 'Unknown error'),
                execution_time=execution_time
            )
        
        # Convert route data for JSON serialization
        best_route = convert_numpy_types({
            'route_type': result['best_route'].route_type,
            'total_distance': result['best_route'].total_distance,
            'total_duration': result['best_route'].total_duration,
            'avg_safety_score': result['best_route'].avg_safety_score,
            'total_incidents': result['best_route'].total_incidents,
            'safety_grade': result['best_route'].safety_grade,
            'waypoints': result['best_route'].waypoints,
            'route_points': result['best_route'].route_points,
            'steps': [
                {
                    'instruction': step.instruction,
                    'distance': step.distance,
                    'duration': step.duration,
                    'maneuver': step.maneuver,
                    'safety_score': step.safety_score,
                    'incident_count': step.incident_count,
                    'start_location': step.start_location,
                    'end_location': step.end_location
                }
                for step in result['best_route'].steps
            ]
        })
        
        all_options = []
        for option in result['all_options']:
            all_options.append(convert_numpy_types({
                'route_type': option.route_type,
                'total_distance': option.total_distance,
                'total_duration': option.total_duration,
                'avg_safety_score': option.avg_safety_score,
                'total_incidents': option.total_incidents,
                'safety_grade': option.safety_grade,
                'waypoints': option.waypoints,
                'route_points': option.route_points
            }))
        
        return SafetyRouteResponse(
            success=True,
            message="Safe route found successfully",
            route=best_route,
            all_options=all_options,
            execution_time=execution_time
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return SafetyRouteResponse(
            success=False,
            message="Error finding safe route",
            error=str(e),
            execution_time=execution_time
        )

@app.post("/safety/info")
async def get_safety_info(request: Dict[str, float]):
    """Get safety information for a specific location"""
    try:
        lat = request.get('lat')
        lng = request.get('lng')
        
        if lat is None or lng is None:
            raise HTTPException(status_code=400, detail="lat and lng are required")
        
        # Get safety score and nearby incidents
        safety_score = safety_router.get_safety_score(lat, lng)
        nearby_incidents = safety_router._count_nearby_incidents(lat, lng, radius_meters=500)
        
        return {
            'success': True,
            'safety_score': float(safety_score),
            'safety_grade': safety_router.get_safety_grade(safety_score),
            'nearby_incidents': int(nearby_incidents),
            'location': {'lat': lat, 'lng': lng}
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.get("/crews/info")
async def get_crews_info():
    """Get detailed information about all available crews"""
    return {
        "crews": {
            "research": {
                "description": "Research crew for AI LLMs analysis",
                "agents": ["researcher", "reporting_analyst", "claude_agent"],
                "tasks": ["research_task", "reporting_task", "claude_analysis_task"],
                "endpoint": "/crews/research",
                "method": "POST"
            },
            "transit": {
                "description": "Transit crew for Bay Area transit planning",
                "agents": ["transit_planner", "transit_analyst", "route_optimizer"],
                "tasks": ["transit_planning_task", "transit_analysis_task", "route_optimization_task"],
                "endpoint": "/crews/transit",
                "method": "POST"
            },
            "full": {
                "description": "Full crew combining research and transit capabilities",
                "agents": [
                    "researcher", "reporting_analyst", "claude_agent",
                    "transit_planner", "transit_analyst", "route_optimizer"
                ],
                "tasks": [
                    "research_task", "reporting_task", "claude_analysis_task",
                    "transit_planning_task", "transit_analysis_task", "route_optimization_task"
                ],
                "endpoint": "/crews/full",
                "method": "POST"
            },
            "custom": {
                "description": "Custom crew with user-defined agents and tasks",
                "endpoint": "/crews/custom",
                "method": "POST",
                "required_fields": ["agents", "tasks"],
                "optional_fields": ["inputs"]
            }
        },
        "available_agents": [
            "researcher", "reporting_analyst", "claude_agent",
            "transit_planner", "transit_analyst", "route_optimizer"
        ],
        "available_tasks": [
            "research_task", "reporting_task", "claude_analysis_task",
            "transit_planning_task", "transit_analysis_task", "route_optimization_task"
        ],
        "safety_routing": {
            "find_route": {
                "description": "Find safe route between two points",
                "endpoint": "/safety/route",
                "method": "POST"
            },
            "safety_info": {
                "description": "Get safety information for location",
                "endpoint": "/safety/info",
                "method": "POST"
            }
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "bc.crew_fastapi:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    ) 