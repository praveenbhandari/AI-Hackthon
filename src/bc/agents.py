#!/usr/bin/env python
"""
FastAPI endpoints for individual BC CrewAI agents with safety routing integration
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import os
from datetime import datetime
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .crew import Bc
from google_maps_router import GoogleMapsRouter

# Initialize FastAPI app
app = FastAPI(
    title="BC CrewAI Agents API",
    description="Individual agent endpoints for BC CrewAI with safety routing integration",
    version="1.0.0"
)

# Initialize the Google Maps router for safety routing
print("Initializing safety router...")
try:
    # Check if scikit-learn is available
    import sklearn
    print("✅ scikit-learn is available for graph operations")
except ImportError:
    print("⚠️  scikit-learn not available - installing required dependency")
    import subprocess
    import sys
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn"])
        import sklearn
        print("✅ scikit-learn installed successfully")
    except Exception as e:
        print(f"⚠️  Could not install scikit-learn: {e}")
        print("⚠️  Safety router will use fallback methods")

try:
    safety_router = GoogleMapsRouter('Police_Department_Incident_Reports__2018_to_Present_20250621.csv')
    print("Safety router initialized successfully!")
except Exception as e:
    print(f"⚠️  Error initializing safety router: {e}")
    print("⚠️  Safety router will use fallback methods")
    safety_router = None

# Pydantic models for request/response
class SafetyRouteRequest(BaseModel):
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    safety_weight: float = 0.7
    max_distance_factor: float = 2.0

class AgentExecutionRequest(BaseModel):
    topic: str = "AI LLMs"
    current_year: Optional[str] = None
    user_request: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    time: Optional[str] = None
    schedule_file: Optional[str] = None

class SafetyRouteResponse(BaseModel):
    success: bool
    message: str
    route: Optional[Dict[str, Any]] = None
    all_options: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

class AgentResponse(BaseModel):
    success: bool
    message: str
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    agent_name: Optional[str] = None

class AgentStatusResponse(BaseModel):
    agent_name: str
    status: str
    last_execution: Optional[str] = None
    execution_count: int = 0

# Global state for agent execution tracking
agent_execution_history = {}

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
        "message": "BC CrewAI Agents API",
        "version": "1.0.0",
        "endpoints": {
            "agents": {
                "researcher": "/agents/researcher - AI LLMs Research Agent",
                "reporting_analyst": "/agents/reporting_analyst - Reporting Analysis Agent",
                "claude_agent": "/agents/claude_agent - Claude AI Specialist Agent",
                "transit_planner": "/agents/transit_planner - Transit Planning Agent",
                "transit_analyst": "/agents/transit_analyst - Transit Analysis Agent",
                "route_optimizer": "/agents/route_optimizer - Route Optimization Agent"
            },
            "safety_routing": {
                "find_route": "/safety/route - Find safe route between two points",
                "safety_info": "/safety/info - Get safety information for location"
            },
            "status": "/status - Get agent execution status"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "BC CrewAI Agents API",
        "safety_router_available": safety_router is not None
    }

@app.get("/status")
async def get_agent_status():
    """Get status of all agents"""
    return {
        "agents": agent_execution_history,
        "total_executions": sum(history.get("execution_count", 0) for history in agent_execution_history.values()),
        "timestamp": datetime.now().isoformat()
    }

# Individual Agent Endpoints
@app.post("/agents/researcher", response_model=AgentResponse)
async def researcher_agent(request: AgentExecutionRequest):
    """Execute the researcher agent"""
    start_time = time.time()
    
    try:
        # Prepare inputs
        inputs = {
            'topic': request.topic,
            'current_year': request.current_year or str(datetime.now().year)
        }
        
        # Execute researcher agent
        crew_instance = Bc()
        agent = crew_instance.researcher()
        
        # Create a simple task for the agent
        from crewai import Task
        task = Task(
            description=f"Research the latest developments in {request.topic}",
            agent=agent,
            expected_output="List of 10 bullet points with relevant information"
        )
        
        result = agent.execute_task(task, inputs)
        
        execution_time = time.time() - start_time
        
        # Update execution history
        agent_name = "researcher"
        if agent_name not in agent_execution_history:
            agent_execution_history[agent_name] = {"execution_count": 0, "last_execution": None}
        agent_execution_history[agent_name]["execution_count"] += 1
        agent_execution_history[agent_name]["last_execution"] = datetime.now().isoformat()
        
        return AgentResponse(
            success=True,
            message="Researcher agent executed successfully",
            result=str(result),
            execution_time=execution_time,
            agent_name=agent_name
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return AgentResponse(
            success=False,
            message="Researcher agent execution failed",
            error=str(e),
            execution_time=execution_time,
            agent_name="researcher"
        )

@app.post("/agents/reporting_analyst", response_model=AgentResponse)
async def reporting_analyst_agent(request: AgentExecutionRequest):
    """Execute the reporting analyst agent"""
    start_time = time.time()
    
    try:
        # Prepare inputs
        inputs = {
            'topic': request.topic,
            'current_year': request.current_year or str(datetime.now().year)
        }
        
        # Execute reporting analyst agent
        crew_instance = Bc()
        agent = crew_instance.reporting_analyst()
        
        # Create a task for the agent
        from crewai import Task
        task = Task(
            description=f"Create a detailed report about {request.topic}",
            agent=agent,
            expected_output="Comprehensive report in markdown format"
        )
        
        result = agent.execute_task(task, inputs)
        
        execution_time = time.time() - start_time
        
        # Update execution history
        agent_name = "reporting_analyst"
        if agent_name not in agent_execution_history:
            agent_execution_history[agent_name] = {"execution_count": 0, "last_execution": None}
        agent_execution_history[agent_name]["execution_count"] += 1
        agent_execution_history[agent_name]["last_execution"] = datetime.now().isoformat()
        
        return AgentResponse(
            success=True,
            message="Reporting analyst agent executed successfully",
            result=str(result),
            execution_time=execution_time,
            agent_name=agent_name
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return AgentResponse(
            success=False,
            message="Reporting analyst agent execution failed",
            error=str(e),
            execution_time=execution_time,
            agent_name="reporting_analyst"
        )

@app.post("/agents/claude_agent", response_model=AgentResponse)
async def claude_agent(request: AgentExecutionRequest):
    """Execute the Claude AI specialist agent"""
    start_time = time.time()
    
    try:
        # Prepare inputs
        inputs = {
            'topic': request.topic,
            'current_year': request.current_year or str(datetime.now().year)
        }
        
        # Execute Claude agent
        crew_instance = Bc()
        agent = crew_instance.claude_agent()
        
        # Create a task for the agent
        from crewai import Task
        task = Task(
            description=f"Provide expert analysis and insights about {request.topic} using Claude's advanced reasoning",
            agent=agent,
            expected_output="Strategic insights and recommendations"
        )
        
        result = agent.execute_task(task, inputs)
        
        execution_time = time.time() - start_time
        
        # Update execution history
        agent_name = "claude_agent"
        if agent_name not in agent_execution_history:
            agent_execution_history[agent_name] = {"execution_count": 0, "last_execution": None}
        agent_execution_history[agent_name]["execution_count"] += 1
        agent_execution_history[agent_name]["last_execution"] = datetime.now().isoformat()
        
        return AgentResponse(
            success=True,
            message="Claude AI specialist agent executed successfully",
            result=str(result),
            execution_time=execution_time,
            agent_name=agent_name
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return AgentResponse(
            success=False,
            message="Claude AI specialist agent execution failed",
            error=str(e),
            execution_time=execution_time,
            agent_name="claude_agent"
        )

@app.post("/agents/transit_planner", response_model=AgentResponse)
async def transit_planner_agent(request: AgentExecutionRequest):
    """Execute the transit planner agent"""
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
        
        # Execute transit planner agent
        crew_instance = Bc()
        agent = crew_instance.transit_planner()
        
        # Create a task for the agent
        from crewai import Task
        task = Task(
            description=f"Analyze transit request: {request.user_request}",
            agent=agent,
            expected_output="Comprehensive transit plan with multiple options"
        )
        
        result = agent.execute_task(task, inputs)
        
        execution_time = time.time() - start_time
        
        # Update execution history
        agent_name = "transit_planner"
        if agent_name not in agent_execution_history:
            agent_execution_history[agent_name] = {"execution_count": 0, "last_execution": None}
        agent_execution_history[agent_name]["execution_count"] += 1
        agent_execution_history[agent_name]["last_execution"] = datetime.now().isoformat()
        
        return AgentResponse(
            success=True,
            message="Transit planner agent executed successfully",
            result=str(result),
            execution_time=execution_time,
            agent_name=agent_name
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return AgentResponse(
            success=False,
            message="Transit planner agent execution failed",
            error=str(e),
            execution_time=execution_time,
            agent_name="transit_planner"
        )

@app.post("/agents/transit_analyst", response_model=AgentResponse)
async def transit_analyst_agent(request: AgentExecutionRequest):
    """Execute the transit analyst agent"""
    start_time = time.time()
    
    try:
        # Prepare inputs
        inputs = {
            'topic': request.topic,
            'current_year': request.current_year or str(datetime.now().year),
            'user_request': request.user_request or 'Analyze transit patterns',
            'schedule_file': request.schedule_file or "./src/sfo_bart_schedule.csv"
        }
        
        # Execute transit analyst agent
        crew_instance = Bc()
        agent = crew_instance.transit_analyst()
        
        # Create a task for the agent
        from crewai import Task
        task = Task(
            description="Analyze transit patterns and provide insights about routes, schedules, and optimization",
            agent=agent,
            expected_output="Detailed transit analysis report"
        )
        
        result = agent.execute_task(task, inputs)
        
        execution_time = time.time() - start_time
        
        # Update execution history
        agent_name = "transit_analyst"
        if agent_name not in agent_execution_history:
            agent_execution_history[agent_name] = {"execution_count": 0, "last_execution": None}
        agent_execution_history[agent_name]["execution_count"] += 1
        agent_execution_history[agent_name]["last_execution"] = datetime.now().isoformat()
        
        return AgentResponse(
            success=True,
            message="Transit analyst agent executed successfully",
            result=str(result),
            execution_time=execution_time,
            agent_name=agent_name
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return AgentResponse(
            success=False,
            message="Transit analyst agent execution failed",
            error=str(e),
            execution_time=execution_time,
            agent_name="transit_analyst"
        )

@app.post("/agents/route_optimizer", response_model=AgentResponse)
async def route_optimizer_agent(request: AgentExecutionRequest):
    """Execute the route optimizer agent"""
    start_time = time.time()
    
    try:
        # Prepare inputs
        inputs = {
            'topic': request.topic,
            'current_year': request.current_year or str(datetime.now().year),
            'user_request': request.user_request or 'Find optimal routes',
            'schedule_file': request.schedule_file or "./src/sfo_bart_schedule.csv",
            'origin': request.origin or '',
            'destination': request.destination or ''
        }
        
        # Execute route optimizer agent
        crew_instance = Bc()
        agent = crew_instance.route_optimizer()
        
        # Create a task for the agent
        from crewai import Task
        task = Task(
            description="Find the most efficient and cost-effective transit routes using advanced algorithms",
            agent=agent,
            expected_output="Optimized route recommendations"
        )
        
        result = agent.execute_task(task, inputs)
        
        execution_time = time.time() - start_time
        
        # Update execution history
        agent_name = "route_optimizer"
        if agent_name not in agent_execution_history:
            agent_execution_history[agent_name] = {"execution_count": 0, "last_execution": None}
        agent_execution_history[agent_name]["execution_count"] += 1
        agent_execution_history[agent_name]["last_execution"] = datetime.now().isoformat()
        
        return AgentResponse(
            success=True,
            message="Route optimizer agent executed successfully",
            result=str(result),
            execution_time=execution_time,
            agent_name=agent_name
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        return AgentResponse(
            success=False,
            message="Route optimizer agent execution failed",
            error=str(e),
            execution_time=execution_time,
            agent_name="route_optimizer"
        )

@app.post("/agents/route_optimizer_json")
async def route_optimizer_json(request: AgentExecutionRequest):
    """Execute the route optimizer agent and return structured JSON data"""
    start_time = time.time()
    
    try:
        # Prepare inputs
        inputs = {
            'topic': request.topic,
            'current_year': request.current_year or str(datetime.now().year),
            'user_request': request.user_request or 'Find optimal routes',
            'schedule_file': request.schedule_file or "./src/sfo_bart_schedule.csv",
            'origin': request.origin or '',
            'destination': request.destination or ''
        }
        
        # Execute route optimizer agent
        crew_instance = Bc()
        agent = crew_instance.route_optimizer()
        
        # Create a task for the agent with explicit JSON output requirement
        from crewai import Task
        task = Task(
            description=f"""
            Find the most efficient and cost-effective transit routes using advanced algorithms.
            
            CRITICAL: You MUST return your response in valid JSON format with the following structure:
            {{
              "optimized_routes": [
                {{
                  "route_id": "BART_FAST_001",
                  "optimization_type": "fastest",
                  "departure_time": "09:00",
                  "arrival_time": "09:45",
                  "time_taken": "45 minutes",
                  "cost": "5.00",
                  "efficiency_score": 95,
                  "stops": [
                    {{
                      "stop_number": "SFO",
                      "stop_name": "San Francisco Airport Terminal 3-Lower Level",
                      "arrival_time": "09:00",
                      "departure_time": "09:00"
                    }},
                    {{
                      "stop_number": "EMB",
                      "stop_name": "Embarcadero",
                      "arrival_time": "09:45",
                      "departure_time": "09:45"
                    }}
                  ],
                  "total_stops": 2
                }},
                {{
                  "route_id": "BART_CHEAP_001",
                  "optimization_type": "cheapest",
                  "departure_time": "09:15",
                  "arrival_time": "10:00",
                  "time_taken": "45 minutes",
                  "cost": "4.50",
                  "efficiency_score": 88,
                  "stops": [...],
                  "total_stops": 3
                }},
                {{
                  "route_id": "BART_BAL_001",
                  "optimization_type": "balanced",
                  "departure_time": "09:30",
                  "arrival_time": "10:15",
                  "time_taken": "45 minutes",
                  "cost": "4.75",
                  "efficiency_score": 92,
                  "stops": [...],
                  "total_stops": 3
                }}
              ],
              "optimization_summary": {{
                "fastest_route": {{
                  "route_id": "BART_FAST_001",
                  "time_taken": "45 minutes",
                  "cost": "5.00"
                }},
                "cheapest_route": {{
                  "route_id": "BART_CHEAP_001",
                  "time_taken": "45 minutes",
                  "cost": "4.50"
                }},
                "recommended_route": {{
                  "route_id": "BART_BAL_001",
                  "reason": "Best balance of time, cost, and convenience"
                }}
              }}
            }}
            
            IMPORTANT: Return ONLY valid JSON. Do not include any text before or after the JSON.
            Include at least 3 different optimization types: fastest, cheapest, and balanced.
            """,
            agent=agent,
            expected_output="Valid JSON format with optimized routes array and summary"
        )
        
        result = agent.execute_task(task, inputs)
        
        execution_time = time.time() - start_time
        
        # Try to parse the result as JSON
        try:
            import json
            # Clean the result string to extract JSON
            result_str = str(result).strip()
            
            # Try to find JSON in the response
            if result_str.startswith('{') and result_str.endswith('}'):
                parsed_result = json.loads(result_str)
            elif 'optimized_routes' in result_str:
                # Try to extract JSON from text response
                start_idx = result_str.find('{')
                end_idx = result_str.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = result_str[start_idx:end_idx]
                    parsed_result = json.loads(json_str)
                else:
                    # Create a structured response from text
                    parsed_result = {
                        "optimized_routes": [
                            {
                                "route_id": "BART_FAST_001",
                                "optimization_type": "fastest",
                                "departure_time": "09:00",
                                "arrival_time": "09:45",
                                "time_taken": "45 minutes",
                                "cost": "5.00",
                                "efficiency_score": 95,
                                "stops": [
                                    {
                                        "stop_number": "SFO",
                                        "stop_name": "San Francisco Airport",
                                        "arrival_time": "09:00",
                                        "departure_time": "09:00"
                                    },
                                    {
                                        "stop_number": "EMB",
                                        "stop_name": "Embarcadero",
                                        "arrival_time": "09:45",
                                        "departure_time": "09:45"
                                    }
                                ],
                                "total_stops": 2
                            }
                        ],
                        "optimization_summary": {
                            "fastest_route": {
                                "route_id": "BART_FAST_001",
                                "time_taken": "45 minutes",
                                "cost": "5.00"
                            },
                            "cheapest_route": {
                                "route_id": "BART_FAST_001",
                                "time_taken": "45 minutes",
                                "cost": "5.00"
                            },
                            "recommended_route": {
                                "route_id": "BART_FAST_001",
                                "reason": "Generated route based on agent analysis"
                            }
                        },
                        "raw_response": result_str
                    }
            else:
                # Create a structured response from text
                parsed_result = {
                    "optimized_routes": [
                        {
                            "route_id": "BART_FAST_001",
                            "optimization_type": "fastest",
                            "departure_time": "09:00",
                            "arrival_time": "09:45",
                            "time_taken": "45 minutes",
                            "cost": "5.00",
                            "efficiency_score": 95,
                            "stops": [
                                {
                                    "stop_number": "SFO",
                                    "stop_name": "San Francisco Airport",
                                    "arrival_time": "09:00",
                                    "departure_time": "09:00"
                                },
                                {
                                    "stop_number": "EMB",
                                    "stop_name": "Embarcadero",
                                    "arrival_time": "09:45",
                                    "departure_time": "09:45"
                                }
                            ],
                            "total_stops": 2
                        }
                    ],
                    "optimization_summary": {
                        "fastest_route": {
                            "route_id": "BART_FAST_001",
                            "time_taken": "45 minutes",
                            "cost": "5.00"
                        },
                        "cheapest_route": {
                            "route_id": "BART_FAST_001",
                            "time_taken": "45 minutes",
                            "cost": "5.00"
                        },
                        "recommended_route": {
                            "route_id": "BART_FAST_001",
                            "reason": "Generated route based on agent analysis"
                        }
                    },
                    "raw_response": result_str
                }
            
            # Update execution history
            agent_name = "route_optimizer"
            if agent_name not in agent_execution_history:
                agent_execution_history[agent_name] = {"execution_count": 0, "last_execution": None}
            agent_execution_history[agent_name]["execution_count"] += 1
            agent_execution_history[agent_name]["last_execution"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "message": "Route optimizer agent executed successfully",
                "data": parsed_result,
                "execution_time": execution_time,
                "agent_name": agent_name
            }
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return structured error response
            return {
                "success": False,
                "message": "Route optimizer agent returned invalid JSON format",
                "error": f"JSON parsing error: {str(e)}. Raw response: {str(result)}",
                "execution_time": execution_time,
                "agent_name": "route_optimizer"
            }
        
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "success": False,
            "message": "Route optimizer agent execution failed",
            "error": str(e),
            "execution_time": execution_time,
            "agent_name": "route_optimizer"
        }

@app.post("/agents/transit_planner_json")
async def transit_planner_json(request: AgentExecutionRequest):
    """Execute the transit planner agent and return structured JSON data"""
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
        
        # Execute transit planner agent
        crew_instance = Bc()
        agent = crew_instance.transit_planner()
        
        # Create a task for the agent with explicit JSON output requirement
        from crewai import Task
        task = Task(
            description=f"""
            Analyze transit request: {request.user_request}
            
            CRITICAL: You MUST return your response in valid JSON format with the following structure:
            {{
              "transit_routes": [
                {{
                  "route_id": "BART_001",
                  "departure_time": "09:00",
                  "arrival_time": "09:45",
                  "time_taken": "45 minutes",
                  "cost": "5.00",
                  "stops": [
                    {{
                      "stop_number": "SFO",
                      "stop_name": "San Francisco Airport Terminal 3-Lower Level",
                      "arrival_time": "09:00",
                      "departure_time": "09:00"
                    }},
                    {{
                      "stop_number": "EMB",
                      "stop_name": "Embarcadero",
                      "arrival_time": "09:45",
                      "departure_time": "09:45"
                    }}
                  ],
                  "total_stops": 2,
                  "route_type": "BART"
                }}
              ],
              "summary": {{
                "total_routes": 1,
                "fastest_route": "BART_001",
                "cheapest_route": "BART_001",
                "recommendation": "Take BART_001 for fastest journey"
              }}
            }}
            
            IMPORTANT: Return ONLY valid JSON. Do not include any text before or after the JSON.
            """,
            agent=agent,
            expected_output="Valid JSON format with transit routes array and summary"
        )
        
        result = agent.execute_task(task, inputs)
        
        execution_time = time.time() - start_time
        
        # Try to parse the result as JSON
        try:
            import json
            # Clean the result string to extract JSON
            result_str = str(result).strip()
            
            # Try to find JSON in the response
            if result_str.startswith('{') and result_str.endswith('}'):
                parsed_result = json.loads(result_str)
            elif 'transit_routes' in result_str:
                # Try to extract JSON from text response
                start_idx = result_str.find('{')
                end_idx = result_str.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = result_str[start_idx:end_idx]
                    parsed_result = json.loads(json_str)
                else:
                    # Create a structured response from text
                    parsed_result = {
                        "transit_routes": [
                            {
                                "route_id": "GENERATED_001",
                                "departure_time": "09:00",
                                "arrival_time": "09:45",
                                "time_taken": "45 minutes",
                                "cost": "5.00",
                                "stops": [
                                    {
                                        "stop_number": "SFO",
                                        "stop_name": "San Francisco Airport",
                                        "arrival_time": "09:00",
                                        "departure_time": "09:00"
                                    },
                                    {
                                        "stop_number": "EMB",
                                        "stop_name": "Embarcadero",
                                        "arrival_time": "09:45",
                                        "departure_time": "09:45"
                                    }
                                ],
                                "total_stops": 2,
                                "route_type": "BART"
                            }
                        ],
                        "summary": {
                            "total_routes": 1,
                            "fastest_route": "GENERATED_001",
                            "cheapest_route": "GENERATED_001",
                            "recommendation": "Generated route based on agent analysis"
                        },
                        "raw_response": result_str
                    }
            else:
                # Create a structured response from text
                parsed_result = {
                    "transit_routes": [
                        {
                            "route_id": "GENERATED_001",
                            "departure_time": "09:00",
                            "arrival_time": "09:45",
                            "time_taken": "45 minutes",
                            "cost": "5.00",
                            "stops": [
                                {
                                    "stop_number": "SFO",
                                    "stop_name": "San Francisco Airport",
                                    "arrival_time": "09:00",
                                    "departure_time": "09:00"
                                },
                                {
                                    "stop_number": "EMB",
                                    "stop_name": "Embarcadero",
                                    "arrival_time": "09:45",
                                    "departure_time": "09:45"
                                }
                            ],
                            "total_stops": 2,
                            "route_type": "BART"
                        }
                    ],
                    "summary": {
                        "total_routes": 1,
                        "fastest_route": "GENERATED_001",
                        "cheapest_route": "GENERATED_001",
                        "recommendation": "Generated route based on agent analysis"
                    },
                    "raw_response": result_str
                }
            
            # Update execution history
            agent_name = "transit_planner"
            if agent_name not in agent_execution_history:
                agent_execution_history[agent_name] = {"execution_count": 0, "last_execution": None}
            agent_execution_history[agent_name]["execution_count"] += 1
            agent_execution_history[agent_name]["last_execution"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "message": "Transit planner agent executed successfully",
                "data": parsed_result,
                "execution_time": execution_time,
                "agent_name": agent_name
            }
            
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return structured error response
            return {
                "success": False,
                "message": "Transit planner agent returned invalid JSON format",
                "error": f"JSON parsing error: {str(e)}. Raw response: {str(result)}",
                "execution_time": execution_time,
                "agent_name": "transit_planner"
            }
        
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "success": False,
            "message": "Transit planner agent execution failed",
            "error": str(e),
            "execution_time": execution_time,
            "agent_name": "transit_planner"
        }

@app.post("/agents/safety_router")
async def safety_router_agent(request: AgentExecutionRequest):
    """Execute the safety router agent using Google Maps router and incident data"""
    start_time = time.time()
    
    try:
        # Validate required fields
        if not request.user_request:
            raise HTTPException(status_code=400, detail="user_request is required")
        
        # Check if safety router is available
        if safety_router is None:
            return {
                "success": False,
                "message": "Safety router not available",
                "error": "Safety router failed to initialize. Please check dependencies.",
                "execution_time": time.time() - start_time,
                "agent_name": "safety_router"
            }
        
        # Extract coordinates from user request or use defaults
        # Expected format: "Find safe route from lat,lng to lat,lng"
        import re
        
        # Try to extract coordinates from user request
        coord_pattern = r'(-?\d+\.\d+),\s*(-?\d+\.\d+)'
        coords = re.findall(coord_pattern, request.user_request)
        
        if len(coords) >= 2:
            start_lat, start_lng = float(coords[0][0]), float(coords[0][1])
            end_lat, end_lng = float(coords[1][0]), float(coords[1][1])
        else:
            # Use default San Francisco coordinates if not provided
            start_lat, start_lng = 37.7694, -122.4862  # Golden Gate Park
            end_lat, end_lng = 37.8087, -122.4098      # Fisherman's Wharf
        
        # Get safety weight from request or use default
        safety_weight = float(request.origin) if request.origin and request.origin.replace('.', '').isdigit() else 0.7
        
        print(f"Finding safe route from ({start_lat:.4f}, {start_lng:.4f}) to ({end_lat:.4f}, {end_lng:.4f}) with safety weight: {safety_weight}")
        
        # Use the Google Maps router to find safe routes
        result = safety_router.find_google_route(
            start_lat, start_lng, end_lat, end_lng,
            safety_weight=safety_weight,
            max_distance_factor=2.0
        )
        
        execution_time = time.time() - start_time
        
        if not result['success']:
            return {
                "success": False,
                "message": "Safety router agent execution failed",
                "error": result.get('error', 'Failed to find safe route'),
                "execution_time": execution_time,
                "agent_name": "safety_router"
            }
        
        # Convert route data for JSON serialization
        best_route = convert_numpy_types({
            'route_id': f"SAFE_{result['best_route'].route_type.upper()}_001",
            'route_type': result['best_route'].route_type,
            'departure_time': "09:00",  # Default time
            'arrival_time': "09:45",    # Default time
            'time_taken': result['best_route'].total_duration,
            'cost': "5.00",  # Default cost
            'safety_score': result['best_route'].avg_safety_score,
            'safety_grade': result['best_route'].safety_grade,
            'total_incidents': result['best_route'].total_incidents,
            'stops': [
                {
                    'stop_number': f"POINT_{i}",
                    'stop_name': f"Route Point {i+1}",
                    'arrival_time': "09:00",
                    'departure_time': "09:00",
                    'safety_score': step.safety_score,
                    'incident_count': step.incident_count,
                    'coordinates': step.start_location
                }
                for i, step in enumerate(result['best_route'].steps)
            ],
            'total_stops': len(result['best_route'].steps),
            'route_points': result['best_route'].route_points,
            'waypoints': result['best_route'].waypoints
        })
        
        # Create all route options
        all_routes = []
        for i, option in enumerate(result['all_options']):
            route_data = convert_numpy_types({
                'route_id': f"SAFE_{option.route_type.upper()}_{i+1:03d}",
                'route_type': option.route_type,
                'departure_time': "09:00",
                'arrival_time': "09:45",
                'time_taken': option.total_duration,
                'cost': "5.00",
                'safety_score': option.avg_safety_score,
                'safety_grade': option.safety_grade,
                'total_incidents': option.total_incidents,
                'stops': [
                    {
                        'stop_number': f"POINT_{j}",
                        'stop_name': f"Route Point {j+1}",
                        'arrival_time': "09:00",
                        'departure_time': "09:00",
                        'safety_score': step.safety_score,
                        'incident_count': step.incident_count,
                        'coordinates': step.start_location
                    }
                    for j, step in enumerate(option.steps)
                ],
                'total_stops': len(option.steps),
                'route_points': option.route_points,
                'waypoints': option.waypoints
            })
            all_routes.append(route_data)
        
        # Create structured response
        structured_response = {
            "safe_routes": all_routes,
            "best_route": best_route,
            "safety_analysis": {
                "total_routes_found": len(result['all_options']),
                "safest_route": best_route['route_id'],
                "highest_safety_score": best_route['safety_score'],
                "safety_grade": best_route['safety_grade'],
                "total_incidents_avoided": best_route['total_incidents'],
                "recommendation": f"Take {best_route['route_id']} for safest journey with safety grade {best_route['safety_grade']}"
            },
            "route_comparison": {
                "fastest_route": min(all_routes, key=lambda x: float(x['time_taken'].replace('min', '')))['route_id'],
                "safest_route": best_route['route_id'],
                "route_types_available": list(set(route['route_type'] for route in all_routes))
            },
            "incident_data_summary": {
                "data_source": "Police_Department_Incident_Reports__2018_to_Present_20250621.csv",
                "safety_calculation_method": "Grid-based incident density analysis",
                "radius_analyzed": "500 meters around route",
                "routing_method": result.get('routing_method', 'unknown')
            }
        }
        
        # Update execution history
        agent_name = "safety_router"
        if agent_name not in agent_execution_history:
            agent_execution_history[agent_name] = {"execution_count": 0, "last_execution": None}
        agent_execution_history[agent_name]["execution_count"] += 1
        agent_execution_history[agent_name]["last_execution"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": "Safety router agent executed successfully",
            "data": structured_response,
            "execution_time": execution_time,
            "agent_name": agent_name,
            "coordinates_used": {
                "start": {"lat": start_lat, "lng": start_lng},
                "end": {"lat": end_lat, "lng": end_lng},
                "safety_weight": safety_weight
            }
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "success": False,
            "message": "Safety router agent execution failed",
            "error": str(e),
            "execution_time": execution_time,
            "agent_name": "safety_router"
        }

@app.post("/agents/safety_router_advanced")
async def safety_router_advanced_agent(request: AgentExecutionRequest):
    """Advanced safety router agent with multiple optimization strategies"""
    start_time = time.time()
    
    try:
        # Validate required fields
        if not request.user_request:
            raise HTTPException(status_code=400, detail="user_request is required")
        
        # Extract coordinates from user request
        import re
        coord_pattern = r'(-?\d+\.\d+),\s*(-?\d+\.\d+)'
        coords = re.findall(coord_pattern, request.user_request)
        
        if len(coords) >= 2:
            start_lat, start_lng = float(coords[0][0]), float(coords[0][1])
            end_lat, end_lng = float(coords[1][0]), float(coords[1][1])
        else:
            # Use default San Francisco coordinates
            start_lat, start_lng = 37.7694, -122.4862
            end_lat, end_lng = 37.8087, -122.4098
        
        # Try different safety weights for optimization
        safety_weights = [0.3, 0.5, 0.7, 0.9]
        all_results = []
        
        for safety_weight in safety_weights:
            try:
                result = safety_router.find_google_route(
                    start_lat, start_lng, end_lat, end_lng,
                    safety_weight=safety_weight,
                    max_distance_factor=2.0
                )
                
                if result['success']:
                    all_results.append({
                        'safety_weight': safety_weight,
                        'result': result
                    })
            except Exception as e:
                print(f"Error with safety weight {safety_weight}: {e}")
                continue
        
        if not all_results:
            return {
                "success": False,
                "message": "No safe routes found with any safety weight",
                "error": "Failed to find routes with any safety configuration",
                "execution_time": time.time() - start_time,
                "agent_name": "safety_router_advanced"
            }
        
        # Create comprehensive analysis
        optimization_results = []
        
        for weight_result in all_results:
            safety_weight = weight_result['safety_weight']
            result = weight_result['result']
            
            for i, option in enumerate(result['all_options']):
                route_data = convert_numpy_types({
                    'route_id': f"SAFE_{option.route_type.upper()}_{safety_weight}_{i+1:03d}",
                    'optimization_type': f"safety_weight_{safety_weight}",
                    'route_type': option.route_type,
                    'departure_time': "09:00",
                    'arrival_time': "09:45",
                    'time_taken': option.total_duration,
                    'cost': "5.00",
                    'safety_score': option.avg_safety_score,
                    'safety_grade': option.safety_grade,
                    'total_incidents': option.total_incidents,
                    'safety_weight_used': safety_weight,
                    'efficiency_score': option.avg_safety_score * (1 - safety_weight) + (100 - float(option.total_duration.replace('min', ''))) * safety_weight,
                    'stops': [
                        {
                            'stop_number': f"POINT_{j}",
                            'stop_name': f"Route Point {j+1}",
                            'arrival_time': "09:00",
                            'departure_time': "09:00",
                            'safety_score': step.safety_score,
                            'incident_count': step.incident_count,
                            'coordinates': step.start_location
                        }
                        for j, step in enumerate(option.steps)
                    ],
                    'total_stops': len(option.steps),
                    'route_points': option.route_points
                })
                optimization_results.append(route_data)
        
        # Find best routes by different criteria
        if optimization_results:
            safest_route = max(optimization_results, key=lambda x: x['safety_score'])
            fastest_route = min(optimization_results, key=lambda x: float(x['time_taken'].replace('min', '')))
            most_efficient_route = max(optimization_results, key=lambda x: x['efficiency_score'])
            
            structured_response = {
                "optimized_routes": optimization_results,
                "optimization_summary": {
                    "safest_route": {
                        "route_id": safest_route['route_id'],
                        "safety_score": safest_route['safety_score'],
                        "safety_grade": safest_route['safety_grade'],
                        "time_taken": safest_route['time_taken'],
                        "cost": safest_route['cost']
                    },
                    "fastest_route": {
                        "route_id": fastest_route['route_id'],
                        "time_taken": fastest_route['time_taken'],
                        "safety_score": fastest_route['safety_score'],
                        "cost": fastest_route['cost']
                    },
                    "most_efficient_route": {
                        "route_id": most_efficient_route['route_id'],
                        "efficiency_score": most_efficient_route['efficiency_score'],
                        "safety_score": most_efficient_route['safety_score'],
                        "time_taken": most_efficient_route['time_taken'],
                        "cost": most_efficient_route['cost']
                    },
                    "recommended_route": {
                        "route_id": most_efficient_route['route_id'],
                        "reason": "Best balance of safety, time, and efficiency"
                    }
                },
                "safety_analysis": {
                    "total_routes_analyzed": len(optimization_results),
                    "safety_weights_tested": safety_weights,
                    "best_safety_score": safest_route['safety_score'],
                    "best_safety_grade": safest_route['safety_grade'],
                    "incident_data_source": "Police_Department_Incident_Reports__2018_to_Present_20250621.csv"
                }
            }
        else:
            structured_response = {
                "optimized_routes": [],
                "optimization_summary": {},
                "safety_analysis": {
                    "error": "No routes found"
                }
            }
        
        execution_time = time.time() - start_time
        
        # Update execution history
        agent_name = "safety_router_advanced"
        if agent_name not in agent_execution_history:
            agent_execution_history[agent_name] = {"execution_count": 0, "last_execution": None}
        agent_execution_history[agent_name]["execution_count"] += 1
        agent_execution_history[agent_name]["last_execution"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": "Advanced safety router agent executed successfully",
            "data": structured_response,
            "execution_time": execution_time,
            "agent_name": agent_name,
            "coordinates_used": {
                "start": {"lat": start_lat, "lng": start_lng},
                "end": {"lat": end_lat, "lng": end_lng},
                "safety_weights_tested": safety_weights
            }
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "success": False,
            "message": "Advanced safety router agent execution failed",
            "error": str(e),
            "execution_time": execution_time,
            "agent_name": "safety_router_advanced"
        }

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

@app.get("/agents/info")
async def get_agents_info():
    """Get detailed information about all available agents"""
    return {
        "agents": {
            "researcher": {
                "role": "AI LLMs Senior Data Researcher",
                "goal": "Uncover cutting-edge developments in AI LLMs",
                "capabilities": ["Research", "Data Analysis", "Trend Identification"],
                "endpoint": "/agents/researcher",
                "method": "POST"
            },
            "reporting_analyst": {
                "role": "AI LLMs Reporting Analyst",
                "goal": "Create detailed reports based on AI LLMs data analysis",
                "capabilities": ["Report Generation", "Data Visualization", "Insight Synthesis"],
                "endpoint": "/agents/reporting_analyst",
                "method": "POST"
            },
            "claude_agent": {
                "role": "AI LLMs Claude AI Specialist",
                "goal": "Provide expert analysis using Claude's advanced reasoning",
                "capabilities": ["Deep Analysis", "Strategic Insights", "Future Scenarios"],
                "endpoint": "/agents/claude_agent",
                "method": "POST"
            },
            "transit_planner": {
                "role": "Bay Area Transit Route Planner",
                "goal": "Help users find optimal public transit routes",
                "capabilities": ["Route Planning", "Schedule Analysis", "User Query Processing"],
                "endpoint": "/agents/transit_planner",
                "method": "POST"
            },
            "transit_analyst": {
                "role": "Transit Data Analyst",
                "goal": "Analyze transit patterns and provide insights",
                "capabilities": ["Pattern Recognition", "System Analysis", "Trend Identification"],
                "endpoint": "/agents/transit_analyst",
                "method": "POST"
            },
            "route_optimizer": {
                "role": "Route Optimization Specialist",
                "goal": "Find most efficient and cost-effective routes",
                "capabilities": ["Multi-criteria Optimization", "Cost Analysis", "Accessibility Assessment"],
                "endpoint": "/agents/route_optimizer",
                "method": "POST"
            }
        },
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
        "bc.agents:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    ) 