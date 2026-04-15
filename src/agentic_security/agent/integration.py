#!/usr/bin/env python3
"""
Integration module - Connects ReAct agent with existing SecurityPipeline
Provides seamless integration between autonomous agent and traditional pipeline
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .agent_manager import AgentManager
from .planner import SecurityPlanner, PlanStatus

logger = logging.getLogger(__name__)


class AgentPipelineIntegration:
    """
    Integrates the ReAct agent with the existing SecurityPipeline.
    Provides a unified interface for both autonomous and traditional operations.
    """
    
    def __init__(self, pipeline, config: Dict[str, Any], verbose: bool = False):
        """
        Initialize the integration.
        
        Args:
            pipeline: SecurityPipeline instance
            config: Configuration dictionary
            verbose: Enable detailed logging
        """
        self.pipeline = pipeline
        self.config = config
        self.verbose = verbose
        
        # Initialize agent components
        self.agent_manager = AgentManager(config, pipeline, verbose)
        self.planner = SecurityPlanner(self.agent_manager.llm_client, verbose)
        
        logger.info("Agent-Pipeline integration initialized")
    
    def run_autonomous_pipeline(self, scan_targets: Optional[list] = None) -> Dict[str, Any]:
        """
        Run the full security pipeline autonomously using the agent.
        
        Args:
            scan_targets: Optional list of targets to scan
            
        Returns:
            Results of autonomous pipeline execution
        """
        logger.info("Starting autonomous security pipeline")
        
        # Get scan targets from config if not provided
        if not scan_targets:
            scan_targets = self.config.get('security', {}).get('scan_targets', [])
        
        # Create a comprehensive task for the agent
        task = self._build_pipeline_task(scan_targets or [])
        
        # Create strategic plan
        plan = self.planner.create_plan(task, {"scan_targets": scan_targets})
        
        # Execute plan using agent
        results = {
            "plan": self.planner.export_plan(),
            "execution": [],
            "summary": {}
        }
        
        step_count = 0
        while not self.planner.is_plan_complete() and step_count < 20:
            next_step = self.planner.get_next_step()
            if not next_step:
                break
            
            logger.info(f"Executing step {next_step.id}: {next_step.description}")
            
            # Mark step as in progress
            self.planner.update_step_status(next_step.id, PlanStatus.IN_PROGRESS)
            
            # Execute the step using agent
            step_result = self._execute_plan_step(next_step)
            
            # Update step status based on result
            if step_result.get('success', False):
                self.planner.update_step_status(
                    next_step.id,
                    PlanStatus.COMPLETED,
                    step_result
                )
            else:
                self.planner.update_step_status(
                    next_step.id,
                    PlanStatus.FAILED,
                    step_result
                )
            
            results["execution"].append({
                "step": next_step.to_dict(),
                "result": step_result
            })
            
            step_count += 1
        
        # Generate summary
        results["summary"] = {
            "total_steps": len(self.planner.current_plan) if self.planner.current_plan else 0,
            "completed": sum(1 for r in results["execution"] if r["result"].get("success")),
            "failed": sum(1 for r in results["execution"] if not r["result"].get("success")),
            "plan_complete": self.planner.is_plan_complete()
        }
        
        logger.info(f"Autonomous pipeline completed: {results['summary']}")
        
        return results
    
    def _build_pipeline_task(self, scan_targets: list) -> str:
        """Build a comprehensive task description for the pipeline"""
        task = """Execute a complete security pipeline with the following objectives:

1. SCAN PHASE:
   - Scan all specified targets for security vulnerabilities
   - Identify SQL injection, XSS, command injection, and crypto weaknesses
   - Categorize findings by severity (high, medium, low)

2. ANALYSIS PHASE:
   - Analyze each high and critical severity vulnerability in detail
   - Assess the risk and potential impact
   - Prioritize fixes based on severity and exploitability

3. REMEDIATION PHASE:
   - Generate secure fixes for high-priority vulnerabilities
   - Apply fixes to the codebase
   - Validate that fixes work correctly

4. VALIDATION PHASE:
   - Run tests to ensure fixes don't break functionality
   - Re-scan to verify vulnerabilities are resolved
   - Document all changes made

5. REPORTING PHASE:
   - Create a comprehensive security report
   - Generate pull request with all fixes
   - Provide recommendations for remaining issues

"""
        
        if scan_targets:
            task += f"\nScan Targets:\n"
            for target in scan_targets:
                task += f"- {target.get('type', 'unknown')}: {target.get('path', target.get('url', 'unknown'))}\n"
        
        return task
    
    def _execute_plan_step(self, step) -> Dict[str, Any]:
        """Execute a single plan step"""
        try:
            # Map plan actions to agent tasks
            action = step.action.upper()
            
            if 'SCAN' in action:
                # Use agent to perform scan
                result = self.agent_manager.agent.run(
                    f"Scan the codebase for security vulnerabilities. {step.description}"
                )
                return {"success": result["status"] == "completed", "details": result}
            
            elif 'ANALYZE' in action:
                # Use agent to analyze
                result = self.agent_manager.agent.run(
                    f"Analyze security vulnerabilities. {step.description}"
                )
                return {"success": result["status"] == "completed", "details": result}
            
            elif 'FIX' in action or 'REMEDIATE' in action:
                # Use agent to generate and apply fixes
                result = self.agent_manager.agent.run(
                    f"Generate and apply security fixes. {step.description}"
                )
                return {"success": result["status"] == "completed", "details": result}
            
            elif 'TEST' in action or 'VALIDATE' in action:
                # Use agent to run tests
                result = self.agent_manager.agent.run(
                    f"Validate security fixes by running tests. {step.description}"
                )
                return {"success": result["status"] == "completed", "details": result}
            
            elif 'REPORT' in action:
                # Use agent to generate report
                result = self.agent_manager.agent.run(
                    f"Generate security report and documentation. {step.description}"
                )
                return {"success": result["status"] == "completed", "details": result}
            
            else:
                # Generic execution
                result = self.agent_manager.agent.run(step.description)
                return {"success": result["status"] == "completed", "details": result}
                
        except Exception as e:
            logger.error(f"Error executing step {step.id}: {e}")
            return {"success": False, "error": str(e)}
    
    def run_hybrid_pipeline(self, use_agent_for: Optional[list] = None) -> Dict[str, Any]:
        """
        Run a hybrid pipeline using both traditional and agent-based approaches.
        
        Args:
            use_agent_for: List of phases to use agent for (e.g., ['analysis', 'remediation'])
            
        Returns:
            Results of hybrid execution
        """
        if not use_agent_for:
            use_agent_for = ['analysis', 'remediation']
        
        logger.info(f"Running hybrid pipeline with agent for: {use_agent_for}")
        
        results: Dict[str, Any] = {
            "scan": {},
            "analysis": {},
            "fixes": {},
            "validation": {}
        }
        
        # 1. Scan (traditional pipeline)
        logger.info("Phase 1: Scanning (traditional)")
        try:
            # Use existing pipeline scan methods
            scan_results = self._run_traditional_scan()
            results["scan"] = scan_results
        except Exception as e:
            logger.error(f"Scan phase failed: {e}")
            results["scan"] = {"error": str(e)}
        
        # 2. Analysis (agent or traditional)
        if 'analysis' in use_agent_for and results["scan"]:
            logger.info("Phase 2: Analysis (agent)")
            analysis_task = f"Analyze the following security scan results and provide detailed risk assessment:\n{results['scan']}"
            analysis_result = self.agent_manager.agent.run(analysis_task)
            results["analysis"] = analysis_result
        else:
            logger.info("Phase 2: Analysis (traditional)")
            results["analysis"] = self._run_traditional_analysis(results["scan"])
        
        # 3. Remediation (agent or traditional)
        if 'remediation' in use_agent_for and results["analysis"]:
            logger.info("Phase 3: Remediation (agent)")
            remediation_task = "Generate and apply security fixes for the identified vulnerabilities"
            fix_result = self.agent_manager.agent.run(remediation_task)
            results["fixes"] = fix_result
        else:
            logger.info("Phase 3: Remediation (traditional)")
            results["fixes"] = self._run_traditional_fixes(results["analysis"])
        
        # 4. Validation (traditional)
        logger.info("Phase 4: Validation (traditional)")
        results["validation"] = self._run_traditional_validation()
        
        return results
    
    def _run_traditional_scan(self) -> Dict[str, Any]:
        """Run traditional pipeline scan"""
        # Use existing pipeline methods
        if hasattr(self.pipeline, 'run_security_scans'):
            return self.pipeline.run_security_scans()
        return {"message": "Traditional scan not available"}
    
    def _run_traditional_analysis(self, scan_results: Dict[str, Any]) -> Dict[str, Any]:
        """Run traditional analysis"""
        if hasattr(self.pipeline, 'analyze_results'):
            return self.pipeline.analyze_results(scan_results)
        return {"message": "Traditional analysis not available"}
    
    def _run_traditional_fixes(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Run traditional fix generation"""
        if hasattr(self.pipeline, 'generate_fixes'):
            return self.pipeline.generate_fixes(analysis)
        return {"message": "Traditional fixes not available"}
    
    def _run_traditional_validation(self) -> Dict[str, Any]:
        """Run traditional validation"""
        if hasattr(self.pipeline, 'validate_fixes'):
            return self.pipeline.validate_fixes()
        return {"message": "Traditional validation not available"}
    
    def get_agent_recommendations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get agent recommendations for security improvements.
        
        Args:
            context: Context information (scan results, code analysis, etc.)
            
        Returns:
            Agent recommendations
        """
        task = f"""Based on the following security context, provide strategic recommendations:

Context:
{context}

Provide:
1. Top 5 security priorities
2. Recommended remediation approach
3. Risk mitigation strategies
4. Long-term security improvements
5. Resource allocation suggestions

Be specific and actionable."""

        result = self.agent_manager.agent.run(task)
        return result
    
    def enable_autonomous_mode(self) -> None:
        """Enable fully autonomous operation mode"""
        logger.info("Enabling autonomous mode")
        self.config['agent'] = self.config.get('agent', {})
        self.config['agent']['autonomous'] = True
        self.config['agent']['auto_fix'] = True
        self.config['agent']['auto_pr'] = True
    
    def disable_autonomous_mode(self) -> None:
        """Disable autonomous mode, require manual approval"""
        logger.info("Disabling autonomous mode")
        self.config['agent'] = self.config.get('agent', {})
        self.config['agent']['autonomous'] = False
        self.config['agent']['auto_fix'] = False
        self.config['agent']['auto_pr'] = False

# Made with Bob
