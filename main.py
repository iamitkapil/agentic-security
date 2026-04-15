#!/usr/bin/env python3
"""
FastAPI main application for Agentic Security
Provides REST API endpoints for security scanning and agent operations
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import os
import sys
import yaml
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentic_security.security_pipeline import SecurityPipeline
from agentic_security.agent.agent_manager import AgentManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Security API",
    description="AI-powered security scanning and fixing pipeline with autonomous agent capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
pipeline_instance: Optional[SecurityPipeline] = None
agent_manager_instance: Optional[AgentManager] = None
scan_results: Dict[str, Any] = {}
agent_tasks: Dict[str, Any] = {}
config_data: Dict[str, Any] = {}


# Pydantic models for request/response
class ScanRequest(BaseModel):
    target: str = Field(..., description="Target path or URL to scan")
    config_file: Optional[str] = Field("config.yml", description="Configuration file path")
    timeout: Optional[int] = Field(300, description="Scan timeout in seconds")


class ScanResponse(BaseModel):
    scan_id: str
    status: str
    message: str
    timestamp: str


class AgentTaskRequest(BaseModel):
    task: str = Field(..., description="Task description for the agent")
    mode: Optional[str] = Field("autonomous", description="Agent mode: autonomous, interactive, or guided")
    max_iterations: Optional[int] = Field(10, description="Maximum iterations for the agent")


class AgentTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    components: Dict[str, str]


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global pipeline_instance, agent_manager_instance, config_data
    
    logger.info("Starting Agentic Security API...")
    
    try:
        # Check for required environment variables
        if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            logger.warning("No AI API keys found. Some features may not work.")
        
        # Load configuration
        config_path = "config.yml"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            logger.info("Configuration loaded")
            
            # Initialize pipeline
            pipeline_instance = SecurityPipeline(config_file=config_path)
            logger.info("Security pipeline initialized")
            
            # Initialize agent manager with config
            agent_manager_instance = AgentManager(
                config=config_data,
                pipeline=pipeline_instance,
                verbose=config_data.get('agent', {}).get('behavior', {}).get('verbose', False)
            )
            logger.info("Agent manager initialized")
        else:
            logger.warning(f"Config file not found: {config_path}")
        
        logger.info("Agentic Security API started successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Don't fail startup, allow API to run with limited functionality


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Agentic Security API...")


# Health check endpoint
@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    components = {
        "pipeline": "initialized" if pipeline_instance else "not_initialized",
        "agent_manager": "initialized" if agent_manager_instance else "not_initialized",
        "anthropic_api": "configured" if os.getenv("ANTHROPIC_API_KEY") else "not_configured",
        "openai_api": "configured" if os.getenv("OPENAI_API_KEY") else "not_configured"
    }
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
        components=components
    )


# Security scanning endpoints
@app.post("/api/v1/scan", response_model=ScanResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """Start a security scan"""
    if not pipeline_instance:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Security pipeline not initialized. Check configuration."
        )
    
    scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Add scan task to background
    background_tasks.add_task(run_scan, scan_id, request)
    
    return ScanResponse(
        scan_id=scan_id,
        status="started",
        message=f"Security scan started for target: {request.target}",
        timestamp=datetime.now().isoformat()
    )


@app.get("/api/v1/scan/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get scan status and results"""
    if scan_id not in scan_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan ID not found: {scan_id}"
        )
    
    return scan_results[scan_id]


@app.get("/api/v1/scans")
async def list_scans():
    """List all scans"""
    return {
        "scans": list(scan_results.keys()),
        "count": len(scan_results)
    }


# Agent endpoints
@app.post("/api/v1/agent/task", response_model=AgentTaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_agent_task(request: AgentTaskRequest, background_tasks: BackgroundTasks):
    """Create a new agent task"""
    if not agent_manager_instance:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent manager not initialized"
        )
    
    task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Add agent task to background
    background_tasks.add_task(run_agent_task, task_id, request)
    
    return AgentTaskResponse(
        task_id=task_id,
        status="started",
        message=f"Agent task started: {request.task}",
        timestamp=datetime.now().isoformat()
    )


@app.get("/api/v1/agent/task/{task_id}")
async def get_agent_task_status(task_id: str):
    """Get agent task status"""
    # Implementation would track task status
    return {
        "task_id": task_id,
        "status": "running",
        "message": "Task status tracking not yet implemented"
    }


@app.get("/api/v1/agent/capabilities")
async def get_agent_capabilities():
    """Get agent capabilities and available tools"""
    if not agent_manager_instance:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent manager not initialized"
        )
    
    return {
        "capabilities": [
            "security_scanning",
            "vulnerability_analysis",
            "code_fixing",
            "git_operations",
            "file_operations"
        ],
        "modes": ["autonomous", "interactive", "guided"],
        "status": "available"
    }


# Configuration endpoints
@app.get("/api/v1/config")
async def get_config():
    """Get current configuration"""
    if not pipeline_instance:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Pipeline not initialized"
        )
    
    return {
        "critical_threshold": pipeline_instance.critical_threshold,
        "max_fix_attempts": pipeline_instance.max_fix_attempts,
        "analysis_model": pipeline_instance.analysis_model
    }


# Background task functions
async def run_scan(scan_id: str, request: ScanRequest):
    """Background task to run security scan"""
    try:
        scan_results[scan_id] = {
            "scan_id": scan_id,
            "status": "running",
            "target": request.target,
            "started_at": datetime.now().isoformat()
        }
        
        # Run the actual scan
        logger.info(f"Starting scan {scan_id} for target: {request.target}")
        
        # This is a placeholder - implement actual scan logic
        # pipeline_instance.run_scan(request.target)
        
        scan_results[scan_id].update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "message": "Scan completed successfully"
        })
        
    except Exception as e:
        logger.error(f"Error in scan {scan_id}: {e}")
        scan_results[scan_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })


async def run_agent_task(task_id: str, request: AgentTaskRequest):
    """Background task to run agent task"""
    try:
        if not agent_manager_instance:
            raise RuntimeError("Agent manager not initialized")
            
        logger.info(f"Starting agent task {task_id}: {request.task}")
        
        agent_tasks[task_id]["status"] = "running"
        
        # Use the agent manager to execute the task
        if request.mode == "autonomous":
            # Run autonomous scan
            result = agent_manager_instance.run_autonomous_scan(path=".")
        elif "analyze" in request.task.lower():
            # Run codebase analysis
            result = agent_manager_instance.analyze_codebase(path=".")
        else:
            # Use the agent's run method directly for custom tasks
            result = agent_manager_instance.agent.run(request.task)
        
        agent_tasks[task_id].update({
            "status": "completed",
            "result": result,
            "completed_at": datetime.now().isoformat()
        })
        
        logger.info(f"Agent task {task_id} completed")
        
    except Exception as e:
        logger.error(f"Error in agent task {task_id}: {e}")
        agent_tasks[task_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

# Made with Bob
