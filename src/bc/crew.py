from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from bc.tools.transport_tools import (
    LoadTransitDataTool,
    SearchStopsTool,
    FindTransitRoutesTool,
    GetRouteInfoTool,
    GetSystemStatsTool
)
from bc.tools.safety_routing_tools import (
    FindSafeRouteTool,
    GetSafetyInfoTool,
    GetIncidentDataTool
)

# Import Groq configuration and utilities
from bc.groq_config import groq_llm, groq_fast, groq_balanced, groq_powerful
from bc.groq_utils import get_agent_llm_config

@CrewBase
class Bc():
    """Bc crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def researcher(self) -> Agent:
        config = get_agent_llm_config('researcher')
        return Agent(
            config=self.agents_config['researcher'],
            llm=config['llm'],
            verbose=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        config = get_agent_llm_config('reporting_analyst')
        return Agent(
            config=self.agents_config['reporting_analyst'],
            llm=config['llm'],
            verbose=True
        )

    @agent
    def claude_agent(self) -> Agent:
        config = get_agent_llm_config('claude_agent')
        return Agent(
            config=self.agents_config['claude_agent'],
            llm=config['llm'],
            verbose=True
        )

    @agent
    def transit_planner(self) -> Agent:
        config = get_agent_llm_config('transit_planner')
        return Agent(
            config=self.agents_config['transit_planner'],
            tools=[
                LoadTransitDataTool(),
                SearchStopsTool(),
                FindTransitRoutesTool(),
                GetRouteInfoTool(),
                GetSystemStatsTool()
            ],
            llm=config['llm'],
            verbose=True
        )

    @agent
    def transit_analyst(self) -> Agent:
        config = get_agent_llm_config('transit_analyst')
        return Agent(
            config=self.agents_config['transit_analyst'],
            tools=[
                LoadTransitDataTool(),
                SearchStopsTool(),
                FindTransitRoutesTool(),
                GetRouteInfoTool(),
                GetSystemStatsTool()
            ],
            llm=config['llm'],
            verbose=True
        )

    @agent
    def route_optimizer(self) -> Agent:
        config = get_agent_llm_config('route_optimizer')
        return Agent(
            config=self.agents_config['route_optimizer'],
            tools=[
                LoadTransitDataTool(),
                SearchStopsTool(),
                FindTransitRoutesTool(),
                GetRouteInfoTool(),
                GetSystemStatsTool()
            ],
            llm=config['llm'],
            verbose=True
        )

    @agent
    def safety_route_finder(self) -> Agent:
        config = get_agent_llm_config('safety_route_finder')
        return Agent(
            config=self.agents_config['safety_route_finder'],
            tools=[
                FindSafeRouteTool(),
                GetSafetyInfoTool(),
                GetIncidentDataTool()
            ],
            llm=config['llm'],
            verbose=False,
            max_iter=3,
            allow_delegation=False
        )

    @agent
    def safety_analyst(self) -> Agent:
        config = get_agent_llm_config('safety_analyst')
        return Agent(
            config=self.agents_config['safety_analyst'],
            tools=[
                FindSafeRouteTool(),
                GetSafetyInfoTool(),
                GetIncidentDataTool()
            ],
            llm=config['llm'],
            verbose=False,
            max_iter=3,
            allow_delegation=False
        )

    @agent
    def route_planner(self) -> Agent:
        config = get_agent_llm_config('route_planner')
        return Agent(
            config=self.agents_config['route_planner'],
            tools=[
                FindSafeRouteTool(),
                GetSafetyInfoTool(),
                GetIncidentDataTool()
            ],
            llm=config['llm'],
            verbose=False,
            max_iter=3,
            allow_delegation=False
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'],
            output_file='report.md'
        )

    @task
    def claude_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['claude_analysis_task'],
            output_file='claude_analysis.md'
        )

    @task
    def transit_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['transit_planning_task'],
            output_file='transit_plan.md'
        )

    @task
    def transit_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['transit_analysis_task'],
            output_file='transit_analysis.md'
        )

    @task
    def route_optimization_task(self) -> Task:
        return Task(
            config=self.tasks_config['route_optimization_task'],
            output_file='route_optimization.md'
        )

    @task
    def safety_route_finding_task(self) -> Task:
        return Task(
            config=self.tasks_config['safety_route_finding_task'],
            output_file='safety_routes.json'
        )

    @task
    def safety_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['safety_analysis_task'],
            output_file='safety_analysis.json'
        )

    @task
    def route_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['route_planning_task'],
            output_file='route_plan.json'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Bc crew with research tasks only (default)"""
        return Crew(
            agents=[self.researcher(), self.reporting_analyst(), self.claude_agent()],
            tasks=[self.research_task(), self.reporting_task(), self.claude_analysis_task()],
            process=Process.sequential,
            verbose=True,
        )

    def transit_crew(self) -> Crew:
        """Creates a transit-only crew"""
        return Crew(
            agents=[self.transit_planner(), self.transit_analyst(), self.route_optimizer()],
            tasks=[self.transit_planning_task(), self.transit_analysis_task(), self.route_optimization_task()],
            process=Process.sequential,
            verbose=True,
        )

    def safety_crew(self) -> Crew:
        """Creates a safety routing crew"""
        return Crew(
            agents=[self.safety_route_finder(), self.safety_analyst(), self.route_planner()],
            tasks=[self.safety_route_finding_task(), self.safety_analysis_task(), self.route_planning_task()],
            process=Process.sequential,
            verbose=False,
        )

    def full_crew(self) -> Crew:
        """Creates a crew with all tasks"""
        return Crew(
            agents=[
                self.researcher(), 
                self.reporting_analyst(), 
                self.claude_agent(),
                self.transit_planner(), 
                self.transit_analyst(), 
                self.route_optimizer()
            ],
            tasks=[
                self.research_task(), 
                self.reporting_task(), 
                self.claude_analysis_task(),
                self.transit_planning_task(), 
                self.transit_analysis_task(), 
                self.route_optimization_task()
            ],
            process=Process.sequential,
            verbose=True,
        )