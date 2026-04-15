#!/usr/bin/env python3
"""
ReAct Agent - Reasoning + Acting Pattern for Security Analysis
Implements autonomous decision-making with tool use for security operations
"""

import logging
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
import re

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent execution states"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    COMPLETED = "completed"
    ERROR = "error"


class ReActStep:
    """Represents a single step in the ReAct cycle"""
    def __init__(self, thought: str, action: str, action_input: Dict[str, Any], observation: str = ""):
        self.thought = thought
        self.action = action
        self.action_input = action_input
        self.observation = observation
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "thought": self.thought,
            "action": self.action,
            "action_input": self.action_input,
            "observation": self.observation,
            "timestamp": self.timestamp.isoformat()
        }


class ReActAgent:
    """
    ReAct Agent for autonomous security analysis and remediation.
    
    The agent follows the ReAct pattern:
    1. Thought: Reason about the current situation
    2. Action: Choose and execute a tool
    3. Observation: Process the result
    4. Repeat until task is complete
    """
    
    def __init__(
        self,
        llm_client: Any,
        tools: Dict[str, Callable],
        max_iterations: int = 10,
        verbose: bool = False
    ):
        """
        Initialize the ReAct agent.
        
        Args:
            llm_client: LLM client (OpenAI or Anthropic)
            tools: Dictionary of available tools {name: function}
            max_iterations: Maximum reasoning-action cycles
            verbose: Enable detailed logging
        """
        self.llm_client = llm_client
        self.tools = tools
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        self.state = AgentState.IDLE
        self.history: List[ReActStep] = []
        self.memory: Dict[str, Any] = {}
        
        # System prompt for ReAct reasoning
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt with tool descriptions"""
        tool_descriptions = "\n".join([
            f"- {name}: {func.__doc__ or 'No description'}"
            for name, func in self.tools.items()
        ])
        
        return f"""You are an autonomous security analysis agent using the ReAct (Reasoning + Acting) pattern.

Available Tools:
{tool_descriptions}

Your task is to analyze security issues and take appropriate actions. For each step:

1. THOUGHT: Reason about what you need to do next
2. ACTION: Choose a tool to use
3. ACTION INPUT: Provide the input for the tool
4. OBSERVATION: You'll receive the result

Format your response as:
THOUGHT: [your reasoning]
ACTION: [tool name]
ACTION INPUT: [JSON input for the tool]

When you have completed the task, use:
THOUGHT: [final reasoning]
ACTION: FINISH
ACTION INPUT: {{"result": "your final answer"}}

Always think step-by-step and use tools to gather information before making decisions.
"""
    
    def _parse_llm_response(self, response: str) -> Optional[ReActStep]:
        """Parse LLM response into a ReActStep"""
        try:
            # Extract THOUGHT
            thought_match = re.search(r'THOUGHT:\s*(.+?)(?=ACTION:|$)', response, re.DOTALL)
            thought = thought_match.group(1).strip() if thought_match else ""
            
            # Extract ACTION
            action_match = re.search(r'ACTION:\s*(\w+)', response)
            action = action_match.group(1).strip() if action_match else ""
            
            # Extract ACTION INPUT
            input_match = re.search(r'ACTION INPUT:\s*(\{.+?\})', response, re.DOTALL)
            if input_match:
                action_input = json.loads(input_match.group(1))
            else:
                action_input = {}
            
            if not thought or not action:
                logger.warning(f"Failed to parse LLM response: {response}")
                return None
            
            return ReActStep(thought, action, action_input)
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return None
    
    def _execute_action(self, step: ReActStep) -> str:
        """Execute the chosen action and return observation"""
        action_name = step.action.upper()
        
        if action_name == "FINISH":
            self.state = AgentState.COMPLETED
            return step.action_input.get("result", "Task completed")
        
        if action_name not in self.tools:
            return f"ERROR: Unknown action '{action_name}'. Available actions: {list(self.tools.keys())}"
        
        try:
            tool = self.tools[action_name]
            result = tool(**step.action_input)
            return str(result)
        except Exception as e:
            logger.error(f"Error executing action {action_name}: {e}")
            return f"ERROR: {str(e)}"
    
    def _build_prompt(self, task: str) -> str:
        """Build the prompt with task and history"""
        prompt = f"Task: {task}\n\n"
        
        if self.history:
            prompt += "Previous steps:\n"
            for i, step in enumerate(self.history, 1):
                prompt += f"\nStep {i}:\n"
                prompt += f"THOUGHT: {step.thought}\n"
                prompt += f"ACTION: {step.action}\n"
                prompt += f"ACTION INPUT: {json.dumps(step.action_input)}\n"
                prompt += f"OBSERVATION: {step.observation}\n"
        
        prompt += "\nWhat should you do next?"
        return prompt
    
    def run(self, task: str) -> Dict[str, Any]:
        """
        Run the agent on a task.
        
        Args:
            task: The task description
            
        Returns:
            Dictionary with result and execution history
        """
        self.state = AgentState.THINKING
        self.history = []
        
        if self.verbose:
            logger.info(f"Starting ReAct agent with task: {task}")
        
        for iteration in range(self.max_iterations):
            if self.state == AgentState.COMPLETED:
                break
            
            # Build prompt with history
            prompt = self._build_prompt(task)
            
            # Get LLM response
            try:
                self.state = AgentState.THINKING
                response = self._call_llm(prompt)
                
                if self.verbose:
                    logger.info(f"\n{'='*60}")
                    logger.info(f"Iteration {iteration + 1}")
                    logger.info(f"{'='*60}")
                    logger.info(f"LLM Response:\n{response}")
                
                # Parse response
                step = self._parse_llm_response(response)
                if not step:
                    logger.error("Failed to parse LLM response")
                    self.state = AgentState.ERROR
                    break
                
                # Execute action
                self.state = AgentState.ACTING
                observation = self._execute_action(step)
                step.observation = observation
                
                if self.verbose:
                    logger.info(f"Observation: {observation}")
                
                # Store step
                self.history.append(step)
                self.state = AgentState.OBSERVING
                
            except Exception as e:
                logger.error(f"Error in iteration {iteration + 1}: {e}")
                self.state = AgentState.ERROR
                break
        
        # Build result
        result = {
            "status": self.state.value,
            "iterations": len(self.history),
            "history": [step.to_dict() for step in self.history],
            "final_result": self.history[-1].observation if self.history else None
        }
        
        if self.verbose:
            logger.info(f"\nAgent completed with status: {self.state.value}")
            logger.info(f"Total iterations: {len(self.history)}")
        
        return result
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the prompt"""
        # This will be implemented based on the LLM client type
        if hasattr(self.llm_client, 'chat'):
            # OpenAI-style client
            response = self.llm_client.chat.completions.create(
                model=getattr(self.llm_client, 'model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        elif hasattr(self.llm_client, 'messages'):
            # Anthropic-style client
            response = self.llm_client.messages.create(
                model=getattr(self.llm_client, 'model', 'claude-3-sonnet-20240229'),
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            return response.content[0].text
        else:
            raise ValueError("Unsupported LLM client type")
    
    def add_to_memory(self, key: str, value: Any) -> None:
        """Add information to agent memory"""
        self.memory[key] = value
    
    def get_from_memory(self, key: str) -> Optional[Any]:
        """Retrieve information from agent memory"""
        return self.memory.get(key)
    
    def clear_memory(self) -> None:
        """Clear agent memory"""
        self.memory.clear()
    
    def get_history_summary(self) -> str:
        """Get a summary of the agent's execution history"""
        if not self.history:
            return "No execution history"
        
        summary = f"Agent executed {len(self.history)} steps:\n"
        for i, step in enumerate(self.history, 1):
            summary += f"\n{i}. {step.action}"
            if step.action != "FINISH":
                summary += f" -> {step.observation[:100]}..."
        
        return summary

# Made with Bob
