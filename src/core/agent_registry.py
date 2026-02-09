"""
Agent Registry

Central registry for all Vidhi agents.
Responsible for:
- Agent discovery and registration
- Enforcing unique agent names
- Providing ordered execution lists
- Supporting orchestration and graph execution
"""

from __future__ import annotations

from typing import Dict, List, Type

from src.agents.base_agent import BaseAgent
from src.config.constants import (
    AGENT_EXECUTION_ORDER,
)


class AgentRegistry:
    """
    Central registry for all agents in the system.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, BaseAgent] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, agent: BaseAgent) -> None:
        """
        Register an agent instance.

        Raises:
            ValueError: if agent name is missing or duplicate
        """
        if not agent.name:
            raise ValueError("Agent must have a non-empty name")

        if agent.name in self._agents:
            raise ValueError(f"Agent '{agent.name}' already registered")

        self._agents[agent.name] = agent

    def bulk_register(self, agents: List[BaseAgent]) -> None:
        """
        Register multiple agents at once.
        """
        for agent in agents:
            self.register(agent)

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get(self, agent_name: str) -> BaseAgent:
        """
        Retrieve a registered agent by name.
        """
        if agent_name not in self._agents:
            raise KeyError(f"Agent '{agent_name}' is not registered")

        return self._agents[agent_name]

    def list_agents(self) -> List[str]:
        """
        List registered agent names.
        """
        return list(self._agents.keys())

    def all_agents(self) -> List[BaseAgent]:
        """
        Return all registered agent instances.
        """
        return list(self._agents.values())

    # ------------------------------------------------------------------
    # Execution Ordering
    # ------------------------------------------------------------------

    def get_execution_order(self) -> List[BaseAgent]:
        """
        Return agents ordered according to AGENT_EXECUTION_ORDER.

        Raises:
            ValueError: if required agents are missing
        """
        ordered_agents: List[BaseAgent] = []
        missing_agents: List[str] = []

        for agent_name in AGENT_EXECUTION_ORDER:
            agent = self._agents.get(agent_name)
            if not agent:
                missing_agents.append(agent_name)
            else:
                ordered_agents.append(agent)

        if missing_agents:
            raise ValueError(
                f"Missing required agents in registry: {missing_agents}"
            )

        return ordered_agents

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> None:
        """
        Validate registry state.
        Ensures all required agents are registered.
        """
        missing = [
            name for name in AGENT_EXECUTION_ORDER
            if name not in self._agents
        ]

        if missing:
            raise RuntimeError(
                f"Agent registry incomplete. Missing agents: {missing}"
            )
