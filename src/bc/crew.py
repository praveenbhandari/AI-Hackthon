from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from .tools import (
    LoadTransitDataTool,
    SearchStopsTool,
    FindTransitRoutesTool,
    GetRouteInfoTool,
    GetSystemStatsTool
)
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Bc():
    """Bc crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'], # type: ignore[index]
            verbose=True
        )

    @agent
    def claude_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['claude_agent'], # type: ignore[index]
            verbose=True
        )

    @agent
    def transit_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['transit_planner'], # type: ignore[index]
            tools=[
                LoadTransitDataTool(),
                SearchStopsTool(),
                FindTransitRoutesTool(),
                GetRouteInfoTool(),
                GetSystemStatsTool()
            ],
            llm="anthropic/claude-3-haiku-20240307",
            verbose=True
        )

    @agent
    def transit_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['transit_analyst'], # type: ignore[index]
            tools=[
                LoadTransitDataTool(),
                SearchStopsTool(),
                FindTransitRoutesTool(),
                GetRouteInfoTool(),
                GetSystemStatsTool()
            ],
            llm="anthropic/claude-3-haiku-20240307",
            verbose=True
        )

    @agent
    def route_optimizer(self) -> Agent:
        return Agent(
            config=self.agents_config['route_optimizer'], # type: ignore[index]
            tools=[
                LoadTransitDataTool(),
                SearchStopsTool(),
                FindTransitRoutesTool(),
                GetRouteInfoTool(),
                GetSystemStatsTool()
            ],
            llm="anthropic/claude-3-haiku-20240307",
            verbose=True
        )

    @agent
    def safety_router(self) -> Agent:
        return Agent(
            config=self.agents_config['safety_router'], # type: ignore[index]
            llm="anthropic/claude-3-haiku-20240307",
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], # type: ignore[index]
            output_file='report.md'
        )

    @task
    def claude_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['claude_analysis_task'], # type: ignore[index]
            output_file='claude_analysis.md'
        )

    @task
    def transit_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['transit_planning_task'], # type: ignore[index]
            output_file='transit_plan.md'
        )

    @task
    def transit_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['transit_analysis_task'], # type: ignore[index]
            output_file='transit_analysis.md'
        )

    @task
    def route_optimization_task(self) -> Task:
        return Task(
            config=self.tasks_config['route_optimization_task'], # type: ignore[index]
            output_file='route_optimization.md'
        )

    @task
    def safety_routing_task(self) -> Task:
        return Task(
            config=self.tasks_config['safety_routing_task'], # type: ignore[index]
            output_file='safety_routing.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Bc crew with research tasks only (default)"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=[self.researcher(), self.reporting_analyst(), self.claude_agent()],
            tasks=[self.research_task(), self.reporting_task(), self.claude_analysis_task()],
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
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
        """Creates a safety-focused crew"""
        return Crew(
            agents=[self.safety_router()],
            tasks=[self.safety_routing_task()],
            process=Process.sequential,
            verbose=True,
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
                self.route_optimizer(),
                self.safety_router()
            ],
            tasks=[
                self.research_task(), 
                self.reporting_task(), 
                self.claude_analysis_task(),
                self.transit_planning_task(), 
                self.transit_analysis_task(), 
                self.route_optimization_task(),
                self.safety_routing_task()
            ],
            process=Process.sequential,
            verbose=True,
        )
