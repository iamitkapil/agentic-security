#!/usr/bin/env python3
"""
Tests for the ReAct Security Agent
"""

import pytest
import os
import yaml
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Import agent components
from src.agentic_security.agent.react_agent import ReActAgent, AgentState, ReActStep
from src.agentic_security.agent.tools import SecurityTools
from src.agentic_security.agent.planner import SecurityPlanner, PlanStatus
from src.agentic_security.agent.memory import AgentMemory, MemoryEntry, ConversationMemory
from src.agentic_security.agent.agent_manager import AgentManager


class TestReActAgent:
    """Test ReAct agent core functionality"""
    
    def test_agent_initialization(self):
        """Test agent can be initialized"""
        mock_llm = Mock()
        tools = {"TEST_TOOL": lambda x: "result"}
        
        agent = ReActAgent(mock_llm, tools, max_iterations=5, verbose=False)
        
        assert agent.state == AgentState.IDLE
        assert agent.max_iterations == 5
        assert len(agent.tools) == 1
        assert len(agent.history) == 0
    
    def test_react_step_creation(self):
        """Test ReActStep creation"""
        step = ReActStep(
            thought="I need to scan the code",
            action="SCAN_CODE",
            action_input={"path": "./src"},
            observation="Found 3 vulnerabilities"
        )
        
        assert step.thought == "I need to scan the code"
        assert step.action == "SCAN_CODE"
        assert step.observation == "Found 3 vulnerabilities"
        
        # Test serialization
        step_dict = step.to_dict()
        assert "thought" in step_dict
        assert "action" in step_dict
        assert "observation" in step_dict
    
    def test_agent_state_transitions(self):
        """Test agent state transitions"""
        mock_llm = Mock()
        tools = {"FINISH": lambda result: result}
        
        agent = ReActAgent(mock_llm, tools)
        
        assert agent.state == AgentState.IDLE
        
        # Simulate state changes
        agent.state = AgentState.THINKING
        assert agent.state == AgentState.THINKING
        
        agent.state = AgentState.COMPLETED
        assert agent.state == AgentState.COMPLETED


class TestSecurityTools:
    """Test security tools"""
    
    def test_tools_initialization(self):
        """Test tools can be initialized"""
        config = {
            "security_patterns": {
                "sql_injection": ["SELECT", "INSERT"],
                "xss": ["<script>", "innerHTML"]
            }
        }
        
        tools = SecurityTools(config)
        tool_dict = tools.get_tools()
        
        assert "SCAN_CODE" in tool_dict
        assert "ANALYZE_VULNERABILITY" in tool_dict
        assert "GENERATE_FIX" in tool_dict
        assert callable(tool_dict["SCAN_CODE"])
    
    def test_scan_code_tool(self):
        """Test code scanning tool"""
        config = {
            "security_patterns": {
                "sql_injection": ["SELECT * FROM"]
            }
        }
        
        tools = SecurityTools(config)
        
        # Create a temporary test file
        test_file = Path("test_scan.py")
        test_file.write_text('query = f"SELECT * FROM users WHERE id={user_id}"')
        
        try:
            result = tools.scan_code(path=str(test_file), scan_type="sql_injection")
            
            assert "vulnerabilities" in result
            assert "summary" in result
            assert result["summary"]["total"] >= 0
        finally:
            if test_file.exists():
                test_file.unlink()
    
    def test_read_file_tool(self):
        """Test file reading tool"""
        config = {}
        tools = SecurityTools(config)
        
        # Create a temporary test file
        test_file = Path("test_read.py")
        test_file.write_text("line 1\nline 2\nline 3\n")
        
        try:
            result = tools.read_file(str(test_file))
            
            assert "content" in result
            assert "line 1" in result["content"]
            assert result["lines"] == 3
        finally:
            if test_file.exists():
                test_file.unlink()


class TestSecurityPlanner:
    """Test strategic planner"""
    
    def test_planner_initialization(self):
        """Test planner can be initialized"""
        mock_llm = Mock()
        planner = SecurityPlanner(mock_llm, verbose=False)
        
        assert planner.llm_client == mock_llm
        assert planner.current_plan is None
    
    def test_plan_step_creation(self):
        """Test plan step creation"""
        from src.agentic_security.agent.planner import PlanStep
        
        step = PlanStep(
            id=1,
            description="Scan for vulnerabilities",
            action="SCAN_CODE",
            dependencies=[],
            priority=5
        )
        
        assert step.id == 1
        assert step.status == PlanStatus.PENDING
        assert step.priority == 5
        
        # Test serialization
        step_dict = step.to_dict()
        assert step_dict["id"] == 1
        assert step_dict["status"] == "pending"


class TestAgentMemory:
    """Test agent memory system"""
    
    def test_memory_initialization(self):
        """Test memory can be initialized"""
        memory = AgentMemory(memory_dir=".test_memory", max_entries=100)
        
        assert memory.max_entries == 100
        assert len(memory.short_term) == 0
        assert len(memory.long_term) == 0
        
        # Cleanup
        import shutil
        if Path(".test_memory").exists():
            shutil.rmtree(".test_memory")
    
    def test_memory_store_retrieve(self):
        """Test storing and retrieving from memory"""
        memory = AgentMemory(memory_dir=".test_memory")
        
        # Store in short-term
        memory.store("test_key", "test_value", category="test")
        
        # Retrieve
        value = memory.retrieve("test_key")
        assert value == "test_value"
        
        # Store in long-term
        memory.store("persistent_key", {"data": "important"}, persist=True)
        value = memory.retrieve("persistent_key")
        assert value["data"] == "important"
        
        # Cleanup
        import shutil
        if Path(".test_memory").exists():
            shutil.rmtree(".test_memory")
    
    def test_memory_search(self):
        """Test memory search functionality"""
        memory = AgentMemory(memory_dir=".test_memory")
        
        # Store multiple entries
        memory.store("scan1", {"vulns": 5}, category="scan_results")
        memory.store("scan2", {"vulns": 3}, category="scan_results")
        memory.store("config1", {"setting": "value"}, category="config")
        
        # Search by category
        scan_results = memory.search(category="scan_results")
        assert len(scan_results) == 2
        
        config_results = memory.search(category="config")
        assert len(config_results) == 1
        
        # Cleanup
        import shutil
        if Path(".test_memory").exists():
            shutil.rmtree(".test_memory")
    
    def test_memory_statistics(self):
        """Test memory statistics"""
        memory = AgentMemory(memory_dir=".test_memory")
        
        memory.store("key1", "value1", category="cat1")
        memory.store("key2", "value2", category="cat2")
        memory.store("key3", "value3", category="cat1")
        
        stats = memory.get_statistics()
        
        assert stats["total_count"] == 3
        assert stats["short_term_count"] == 3
        assert "cat1" in stats["categories"]
        assert stats["categories"]["cat1"] == 2
        
        # Cleanup
        import shutil
        if Path(".test_memory").exists():
            shutil.rmtree(".test_memory")


class TestConversationMemory:
    """Test conversation memory"""
    
    def test_conversation_initialization(self):
        """Test conversation memory initialization"""
        conv_memory = ConversationMemory(max_history=10)
        
        assert conv_memory.max_history == 10
        assert len(conv_memory.history) == 0
    
    def test_add_conversation_turn(self):
        """Test adding conversation turns"""
        conv_memory = ConversationMemory()
        
        conv_memory.add_turn("user", "Scan for vulnerabilities")
        conv_memory.add_turn("assistant", "I'll scan the codebase")
        
        assert len(conv_memory.history) == 2
        assert conv_memory.history[0]["role"] == "user"
        assert conv_memory.history[1]["role"] == "assistant"
    
    def test_conversation_history_limit(self):
        """Test conversation history limit"""
        conv_memory = ConversationMemory(max_history=3)
        
        for i in range(5):
            conv_memory.add_turn("user", f"Message {i}")
        
        # Should only keep last 3
        assert len(conv_memory.history) == 3
        assert conv_memory.history[0]["content"] == "Message 2"


class TestAgentIntegration:
    """Integration tests for agent components"""
    
    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="No API keys available"
    )
    def test_agent_manager_initialization(self):
        """Test agent manager can be initialized with real config"""
        config = {
            "security": {
                "critical_threshold": 7.0,
                "max_fix_attempts": 3,
                "scan_targets": []
            },
            "ai": {
                "models": {
                    "fix_implementation": "claude-3-sonnet-20240229"
                }
            },
            "agent": {
                "max_iterations": 5
            },
            "security_patterns": {
                "sql_injection": ["SELECT"]
            }
        }
        
        try:
            manager = AgentManager(config, verbose=False)
            assert manager.agent is not None
            assert manager.tools is not None
        except ValueError as e:
            # Expected if API keys not set
            assert "API_KEY" in str(e)


def test_agent_module_imports():
    """Test that all agent modules can be imported"""
    from src.agentic_security.agent import (
        ReActAgent,
        AgentState,
        ReActStep,
        SecurityTools,
        AgentManager
    )
    
    assert ReActAgent is not None
    assert AgentState is not None
    assert ReActStep is not None
    assert SecurityTools is not None
    assert AgentManager is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
