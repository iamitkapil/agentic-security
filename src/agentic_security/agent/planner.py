#!/usr/bin/env python3
"""
Agent Planner - Strategic planning and reasoning for security operations
Implements multi-step planning and goal decomposition
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PlanStatus(Enum):
    """Status of a plan or step"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PlanStep:
    """Represents a single step in a plan"""
    id: int
    description: str
    action: str
    dependencies: List[int]
    priority: int
    status: PlanStatus = PlanStatus.PENDING
    result: Optional[Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "action": self.action,
            "dependencies": self.dependencies,
            "priority": self.priority,
            "status": self.status.value,
            "result": self.result
        }


class SecurityPlanner:
    """
    Strategic planner for security operations.
    Decomposes complex security tasks into actionable steps.
    """
    
    def __init__(self, llm_client: Any, verbose: bool = False):
        """
        Initialize the planner.
        
        Args:
            llm_client: LLM client for generating plans
            verbose: Enable detailed logging
        """
        self.llm_client = llm_client
        self.verbose = verbose
        self.current_plan: Optional[List[PlanStep]] = None
    
    def create_plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> List[PlanStep]:
        """
        Create a strategic plan for a security task.
        
        Args:
            task: The security task to plan for
            context: Additional context (scan results, vulnerabilities, etc.)
            
        Returns:
            List of planned steps
        """
        if self.verbose:
            logger.info(f"Creating plan for task: {task}")
        
        # Build planning prompt
        prompt = self._build_planning_prompt(task, context)
        
        # Get plan from LLM
        plan_text = self._call_llm(prompt)
        
        # Parse plan into steps
        steps = self._parse_plan(plan_text)
        
        self.current_plan = steps
        
        if self.verbose:
            logger.info(f"Created plan with {len(steps)} steps")
            for step in steps:
                logger.info(f"  Step {step.id}: {step.description}")
        
        return steps
    
    def _build_planning_prompt(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the planning prompt"""
        prompt = f"""Create a detailed step-by-step plan for the following security task:

Task: {task}
"""
        
        if context:
            prompt += f"\nContext:\n{self._format_context(context)}\n"
        
        prompt += """
Please create a plan with the following format for each step:

STEP [number]
DESCRIPTION: [what this step does]
ACTION: [the tool/action to use]
DEPENDENCIES: [comma-separated list of step numbers this depends on, or "none"]
PRIORITY: [1-5, where 5 is highest priority]

Guidelines:
1. Break down complex tasks into simple, atomic steps
2. Identify dependencies between steps
3. Prioritize critical security issues
4. Include validation steps after fixes
5. Plan for error handling and rollback if needed
6. Keep steps focused and actionable

Create the plan:"""
        
        return prompt
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context information for the prompt"""
        formatted = []
        
        if 'vulnerabilities' in context:
            vulns = context['vulnerabilities']
            formatted.append(f"Found {len(vulns)} vulnerabilities:")
            for vuln in vulns[:5]:  # Show first 5
                formatted.append(f"  - {vuln.get('type', 'unknown')} in {vuln.get('file', 'unknown')}")
        
        if 'scan_summary' in context:
            summary = context['scan_summary']
            formatted.append(f"\nScan Summary:")
            formatted.append(f"  Total issues: {summary.get('total', 0)}")
            if 'by_severity' in summary:
                formatted.append(f"  High: {summary['by_severity'].get('high', 0)}")
                formatted.append(f"  Medium: {summary['by_severity'].get('medium', 0)}")
                formatted.append(f"  Low: {summary['by_severity'].get('low', 0)}")
        
        return '\n'.join(formatted)
    
    def _parse_plan(self, plan_text: str) -> List[PlanStep]:
        """Parse LLM-generated plan into PlanStep objects"""
        steps = []
        current_step = {}
        step_id = 0
        
        for line in plan_text.split('\n'):
            line = line.strip()
            
            if line.startswith('STEP'):
                # Save previous step if exists
                if current_step:
                    steps.append(self._create_step_from_dict(step_id, current_step))
                    step_id += 1
                current_step = {}
            
            elif line.startswith('DESCRIPTION:'):
                current_step['description'] = line.replace('DESCRIPTION:', '').strip()
            
            elif line.startswith('ACTION:'):
                current_step['action'] = line.replace('ACTION:', '').strip()
            
            elif line.startswith('DEPENDENCIES:'):
                deps_str = line.replace('DEPENDENCIES:', '').strip().lower()
                if deps_str == 'none' or not deps_str:
                    current_step['dependencies'] = []
                else:
                    # Parse comma-separated step numbers
                    try:
                        current_step['dependencies'] = [
                            int(d.strip()) for d in deps_str.split(',') if d.strip().isdigit()
                        ]
                    except:
                        current_step['dependencies'] = []
            
            elif line.startswith('PRIORITY:'):
                try:
                    priority_str = line.replace('PRIORITY:', '').strip()
                    current_step['priority'] = int(priority_str[0]) if priority_str else 3
                except:
                    current_step['priority'] = 3
        
        # Add last step
        if current_step:
            steps.append(self._create_step_from_dict(step_id, current_step))
        
        return steps
    
    def _create_step_from_dict(self, step_id: int, step_dict: Dict[str, Any]) -> PlanStep:
        """Create a PlanStep from a dictionary"""
        return PlanStep(
            id=step_id,
            description=step_dict.get('description', 'No description'),
            action=step_dict.get('action', 'UNKNOWN'),
            dependencies=step_dict.get('dependencies', []),
            priority=step_dict.get('priority', 3)
        )
    
    def get_next_step(self) -> Optional[PlanStep]:
        """
        Get the next step to execute based on dependencies and priorities.
        
        Returns:
            Next step to execute, or None if plan is complete
        """
        if not self.current_plan:
            return None
        
        # Find pending steps whose dependencies are met
        available_steps = []
        
        for step in self.current_plan:
            if step.status != PlanStatus.PENDING:
                continue
            
            # Check if all dependencies are completed
            dependencies_met = all(
                self.current_plan[dep_id].status == PlanStatus.COMPLETED
                for dep_id in step.dependencies
                if dep_id < len(self.current_plan)
            )
            
            if dependencies_met:
                available_steps.append(step)
        
        if not available_steps:
            return None
        
        # Return highest priority step
        return max(available_steps, key=lambda s: s.priority)
    
    def update_step_status(self, step_id: int, status: PlanStatus, result: Any = None) -> None:
        """
        Update the status of a step.
        
        Args:
            step_id: ID of the step to update
            status: New status
            result: Optional result of the step execution
        """
        if self.current_plan and step_id < len(self.current_plan):
            self.current_plan[step_id].status = status
            self.current_plan[step_id].result = result
            
            if self.verbose:
                logger.info(f"Step {step_id} status updated to {status.value}")
    
    def get_plan_progress(self) -> Dict[str, Any]:
        """
        Get current plan progress.
        
        Returns:
            Dictionary with progress information
        """
        if not self.current_plan:
            return {"message": "No active plan"}
        
        total = len(self.current_plan)
        completed = sum(1 for s in self.current_plan if s.status == PlanStatus.COMPLETED)
        failed = sum(1 for s in self.current_plan if s.status == PlanStatus.FAILED)
        in_progress = sum(1 for s in self.current_plan if s.status == PlanStatus.IN_PROGRESS)
        
        return {
            "total_steps": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "pending": total - completed - failed - in_progress,
            "progress_percentage": (completed / total * 100) if total > 0 else 0,
            "steps": [step.to_dict() for step in self.current_plan]
        }
    
    def is_plan_complete(self) -> bool:
        """Check if the current plan is complete"""
        if not self.current_plan:
            return True
        
        return all(
            step.status in [PlanStatus.COMPLETED, PlanStatus.SKIPPED]
            for step in self.current_plan
        )
    
    def has_failed_steps(self) -> bool:
        """Check if any steps have failed"""
        if not self.current_plan:
            return False
        
        return any(step.status == PlanStatus.FAILED for step in self.current_plan)
    
    def get_failed_steps(self) -> List[PlanStep]:
        """Get list of failed steps"""
        if not self.current_plan:
            return []
        
        return [step for step in self.current_plan if step.status == PlanStatus.FAILED]
    
    def replan_from_failure(self, failed_step_id: int) -> List[PlanStep]:
        """
        Create a new plan to recover from a failure.
        
        Args:
            failed_step_id: ID of the failed step
            
        Returns:
            New recovery plan
        """
        if not self.current_plan or failed_step_id >= len(self.current_plan):
            return []
        
        failed_step = self.current_plan[failed_step_id]
        
        prompt = f"""A step in our security plan has failed. Create a recovery plan.

Failed Step:
- Description: {failed_step.description}
- Action: {failed_step.action}
- Result: {failed_step.result}

Create a recovery plan that:
1. Diagnoses why the step failed
2. Provides alternative approaches
3. Includes rollback steps if needed
4. Ensures system stability

Use the same format as before (STEP, DESCRIPTION, ACTION, DEPENDENCIES, PRIORITY)."""

        plan_text = self._call_llm(prompt)
        recovery_steps = self._parse_plan(plan_text)
        
        if self.verbose:
            logger.info(f"Created recovery plan with {len(recovery_steps)} steps")
        
        return recovery_steps
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the prompt"""
        try:
            if hasattr(self.llm_client, 'chat'):
                # OpenAI-style
                response = self.llm_client.chat.completions.create(
                    model=getattr(self.llm_client, 'model', 'gpt-4'),
                    messages=[
                        {"role": "system", "content": "You are a security planning expert. Create detailed, actionable plans for security operations."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            elif hasattr(self.llm_client, 'messages'):
                # Anthropic-style
                response = self.llm_client.messages.create(
                    model=getattr(self.llm_client, 'model', 'claude-3-sonnet-20240229'),
                    system="You are a security planning expert. Create detailed, actionable plans for security operations.",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.content[0].text
            else:
                raise ValueError("Unsupported LLM client type")
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return ""
    
    def export_plan(self) -> Dict[str, Any]:
        """Export the current plan as a dictionary"""
        if not self.current_plan:
            return {}
        
        return {
            "steps": [step.to_dict() for step in self.current_plan],
            "progress": self.get_plan_progress()
        }

# Made with Bob
