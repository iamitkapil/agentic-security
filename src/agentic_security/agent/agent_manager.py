#!/usr/bin/env python3
"""
Agent Manager - Coordinates ReAct agent with security pipeline
Provides high-level interface for autonomous security operations
"""

import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from .react_agent import ReActAgent, AgentState
from .tools import SecurityTools

logger = logging.getLogger(__name__)


class AgentManager:
    """
    Manages the ReAct agent lifecycle and integration with security pipeline.
    Provides high-level interface for autonomous security operations.
    """
    
    def __init__(self, config: Dict[str, Any], pipeline=None, verbose: bool = False):
        """
        Initialize the agent manager.
        
        Args:
            config: Configuration dictionary
            pipeline: Optional SecurityPipeline instance
            verbose: Enable detailed logging
        """
        self.config = config
        self.pipeline = pipeline
        self.verbose = verbose
        
        # Initialize LLM client
        self.llm_client = self._initialize_llm()
        
        # Initialize tools
        self.tools = SecurityTools(config, pipeline)
        
        # Initialize agent
        self.agent = ReActAgent(
            llm_client=self.llm_client,
            tools=self.tools.get_tools(),
            max_iterations=config.get('agent', {}).get('max_iterations', 10),
            verbose=verbose
        )
        
        # Execution history
        self.execution_history = []
    
    def _initialize_llm(self) -> Any:
        """Initialize the LLM client based on configuration"""
        from dotenv import load_dotenv
        load_dotenv()
        
        # Get model configuration
        ai_config = self.config.get('ai', {})
        model_name = ai_config.get('models', {}).get('fix_implementation', 'claude-3-sonnet-20240229')
        
        # Determine provider
        if 'gpt' in model_name.lower():
            # OpenAI
            import openai
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            
            client = openai.OpenAI(api_key=api_key)
            client.model = model_name
            return client
        else:
            # Anthropic
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in environment")
            
            client = anthropic.Anthropic(api_key=api_key)
            client.model = model_name
            return client
    
    def run_autonomous_scan(self, path: str = ".") -> Dict[str, Any]:
        """
        Run autonomous security scan and remediation.
        
        Args:
            path: Path to scan
            
        Returns:
            Results of autonomous operation
        """
        task = f"""Perform a comprehensive security scan and remediation on the codebase at '{path}'.

Your objectives:
1. Scan the code for security vulnerabilities
2. Analyze each vulnerability found
3. Generate and apply fixes for critical and high-severity issues
4. Validate that fixes work correctly
5. Create a summary report

Follow these steps:
- First, scan the code to identify vulnerabilities
- For each high or critical vulnerability:
  - Analyze it in detail
  - Generate an appropriate fix
  - Apply the fix
  - Validate the fix worked
- Create a summary of all actions taken

Be thorough but efficient. Focus on the most critical security issues first."""

        logger.info(f"Starting autonomous scan on {path}")
        result = self.agent.run(task)
        
        # Store execution history
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "task": "autonomous_scan",
            "path": path,
            "result": result
        })
        
        return result
    
    def fix_vulnerability(
        self,
        file_path: str,
        line_number: int,
        vuln_type: str
    ) -> Dict[str, Any]:
        """
        Autonomously fix a specific vulnerability.
        
        Args:
            file_path: Path to vulnerable file
            line_number: Line number of vulnerability
            vuln_type: Type of vulnerability
            
        Returns:
            Results of fix operation
        """
        task = f"""Fix the {vuln_type} vulnerability in {file_path} at line {line_number}.

Steps to follow:
1. Analyze the vulnerability in detail
2. Generate an appropriate secure fix
3. Apply the fix to the file
4. Validate the fix was applied correctly
5. Run tests if available to ensure nothing broke

Provide a summary of what was done."""

        logger.info(f"Fixing {vuln_type} in {file_path}:{line_number}")
        result = self.agent.run(task)
        
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "task": "fix_vulnerability",
            "file": file_path,
            "line": line_number,
            "type": vuln_type,
            "result": result
        })
        
        return result
    
    def analyze_codebase(self, path: str = ".") -> Dict[str, Any]:
        """
        Perform autonomous codebase security analysis.
        
        Args:
            path: Path to analyze
            
        Returns:
            Analysis results
        """
        task = f"""Analyze the codebase at '{path}' for security issues.

Provide:
1. Overview of the codebase structure
2. List of all security vulnerabilities found
3. Risk assessment for each vulnerability
4. Prioritized recommendations for fixes
5. Summary of overall security posture

Be comprehensive in your analysis."""

        logger.info(f"Analyzing codebase at {path}")
        result = self.agent.run(task)
        
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "task": "analyze_codebase",
            "path": path,
            "result": result
        })
        
        return result
    
    def create_security_pr(
        self,
        branch_name: str,
        fixes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Autonomously create a security PR with fixes.
        
        Args:
            branch_name: Name for the new branch
            fixes: List of fixes to include
            
        Returns:
            PR creation results
        """
        task = f"""Create a pull request for security fixes.

Branch name: {branch_name}
Fixes to include: {json.dumps(fixes, indent=2)}

Steps:
1. Create a new branch with the given name
2. Commit all changes with a descriptive message
3. Create a pull request with:
   - Clear title describing the security fixes
   - Detailed body explaining each fix
   - List of vulnerabilities addressed
   - Testing performed

Make the PR description professional and comprehensive."""

        logger.info(f"Creating security PR on branch {branch_name}")
        result = self.agent.run(task)
        
        self.execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "task": "create_security_pr",
            "branch": branch_name,
            "result": result
        })
        
        return result
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get summary of all agent executions.
        
        Returns:
            Summary of execution history
        """
        if not self.execution_history:
            return {"message": "No executions yet"}
        
        summary = {
            "total_executions": len(self.execution_history),
            "tasks": {},
            "recent_executions": self.execution_history[-5:]  # Last 5
        }
        
        # Count by task type
        for execution in self.execution_history:
            task_type = execution.get("task", "unknown")
            summary["tasks"][task_type] = summary["tasks"].get(task_type, 0) + 1
        
        return summary
    
    def save_execution_log(self, output_path: str = "agent_execution_log.json") -> None:
        """
        Save execution history to file.
        
        Args:
            output_path: Path to save the log
        """
        try:
            with open(output_path, 'w') as f:
                json.dump({
                    "executions": self.execution_history,
                    "summary": self.get_execution_summary()
                }, f, indent=2)
            logger.info(f"Execution log saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving execution log: {e}")
    
    def interactive_mode(self) -> None:
        """
        Run agent in interactive mode for custom tasks.
        """
        print("\n🤖 ReAct Agent - Interactive Mode")
        print("=" * 60)
        print("Enter your security task (or 'quit' to exit):\n")
        
        while True:
            try:
                task = input("Task> ").strip()
                
                if task.lower() in ['quit', 'exit', 'q']:
                    print("\nExiting interactive mode...")
                    break
                
                if not task:
                    continue
                
                print(f"\n🔄 Processing task...\n")
                result = self.agent.run(task)
                
                print(f"\n✅ Task completed!")
                print(f"Status: {result['status']}")
                print(f"Iterations: {result['iterations']}")
                
                if result.get('final_result'):
                    print(f"\nResult:\n{result['final_result']}")
                
                print("\n" + "=" * 60 + "\n")
                
            except KeyboardInterrupt:
                print("\n\nInterrupted. Exiting...")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"\n❌ Error: {e}\n")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get current agent status.
        
        Returns:
            Agent status information
        """
        return {
            "state": self.agent.state.value,
            "total_steps": len(self.agent.history),
            "memory_items": len(self.agent.memory),
            "last_action": self.agent.history[-1].action if self.agent.history else None,
            "execution_count": len(self.execution_history)
        }

# Made with Bob
