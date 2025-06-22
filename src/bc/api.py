#!/usr/bin/env python
"""
FastAPI endpoints for BC CrewAI agents
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import os
from datetime import datetime

from bc.crew import Bc

# Default SFO BART schedule file path
DEFAULT_SCHEDULE_FILE = "./src/sfo_bart_schedule.csv"

# Initialize FastAPI app
app = FastAPI(
    title="BC CrewAI API",
    description="API endpoints for BC CrewAI agents - Research, Transit, and Full Crew",
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
            "full": "/full - Full crew (Research + Transit)",
            "health": "/health - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health ch eck endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "BC CrewAI API"
    }

@app.post("/research", response_model=AgentResponse)
async def research_endpoint(request: ResearchRequest):
    """
    Research crew endpoint - Analyzes AI LLMs and provides insights
    """
    import time
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
    import time
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

@app.post("/full", response_model=AgentResponse)
async def full_crew_endpoint(request: FullCrewRequest):
    """
    Full crew endpoint - Executes both research and transit tasks
    """
    import time
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