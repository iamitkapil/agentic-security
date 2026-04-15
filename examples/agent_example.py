#!/usr/bin/env python3
"""
Example: Using the ReAct Security Agent
Demonstrates autonomous security scanning and remediation
"""

import yaml
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from agentic_security.security_pipeline import SecurityPipeline
from agentic_security.agent.agent_manager import AgentManager
from agentic_security.agent.integration import AgentPipelineIntegration


def example_1_autonomous_scan():
    """Example 1: Run autonomous security scan"""
    print("=" * 60)
    print("Example 1: Autonomous Security Scan")
    print("=" * 60)
    
    # Load configuration
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize pipeline and agent
    pipeline = SecurityPipeline('config.yml')
    integration = AgentPipelineIntegration(pipeline, config, verbose=True)
    
    # Run autonomous scan
    print("\n🤖 Starting autonomous scan...")
    result = integration.agent_manager.run_autonomous_scan('./src')
    
    print(f"\n✅ Scan completed!")
    print(f"Status: {result['status']}")
    print(f"Iterations: {result['iterations']}")
    
    if result.get('final_result'):
        print(f"\nResult:\n{result['final_result']}")


def example_2_fix_vulnerability():
    """Example 2: Fix a specific vulnerability"""
    print("\n" + "=" * 60)
    print("Example 2: Fix Specific Vulnerability")
    print("=" * 60)
    
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    pipeline = SecurityPipeline('config.yml')
    integration = AgentPipelineIntegration(pipeline, config, verbose=True)
    
    # Fix a SQL injection vulnerability
    print("\n🔧 Fixing SQL injection vulnerability...")
    result = integration.agent_manager.fix_vulnerability(
        file_path='tests/samples/vulnerable_query.py',
        line_number=10,
        vuln_type='sql_injection'
    )
    
    print(f"\n✅ Fix completed!")
    print(f"Status: {result['status']}")


def example_3_analyze_codebase():
    """Example 3: Analyze codebase security"""
    print("\n" + "=" * 60)
    print("Example 3: Codebase Security Analysis")
    print("=" * 60)
    
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    pipeline = SecurityPipeline('config.yml')
    integration = AgentPipelineIntegration(pipeline, config, verbose=True)
    
    # Analyze codebase
    print("\n🔬 Analyzing codebase security...")
    result = integration.agent_manager.analyze_codebase('./src')
    
    print(f"\n✅ Analysis completed!")
    print(f"Status: {result['status']}")


def example_4_hybrid_pipeline():
    """Example 4: Run hybrid pipeline"""
    print("\n" + "=" * 60)
    print("Example 4: Hybrid Pipeline (Agent + Traditional)")
    print("=" * 60)
    
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    pipeline = SecurityPipeline('config.yml')
    integration = AgentPipelineIntegration(pipeline, config, verbose=True)
    
    # Run hybrid pipeline
    print("\n🔄 Running hybrid pipeline...")
    result = integration.run_hybrid_pipeline(use_agent_for=['analysis', 'remediation'])
    
    print(f"\n✅ Pipeline completed!")
    print(f"Scan: {result.get('scan', {}).get('message', 'Done')}")
    print(f"Analysis: {result.get('analysis', {}).get('status', 'Done')}")
    print(f"Fixes: {result.get('fixes', {}).get('status', 'Done')}")


def example_5_memory_usage():
    """Example 5: Using agent memory"""
    print("\n" + "=" * 60)
    print("Example 5: Agent Memory Usage")
    print("=" * 60)
    
    from agentic_security.agent.memory import AgentMemory
    
    # Initialize memory
    memory = AgentMemory()
    
    # Store information
    print("\n💾 Storing information in memory...")
    memory.store(
        key="last_scan_results",
        value={"vulnerabilities": 5, "fixed": 3},
        category="scan_results",
        persist=True
    )
    
    memory.store(
        key="common_patterns",
        value=["sql_injection", "xss", "command_injection"],
        category="patterns",
        persist=True
    )
    
    # Retrieve information
    print("\n📖 Retrieving from memory...")
    scan_results = memory.retrieve("last_scan_results")
    print(f"Last scan results: {scan_results}")
    
    # Search memory
    print("\n🔍 Searching memory...")
    scan_entries = memory.search(category="scan_results")
    print(f"Found {len(scan_entries)} scan result entries")
    
    # Get statistics
    stats = memory.get_statistics()
    print(f"\n📊 Memory statistics:")
    print(f"  Total entries: {stats['total_count']}")
    print(f"  Categories: {stats['categories']}")
    
    # Export memory
    print("\n💾 Exporting memory...")
    memory.export_memory("example_memory_export.json")
    print("Memory exported to example_memory_export.json")


def example_6_custom_task():
    """Example 6: Custom agent task"""
    print("\n" + "=" * 60)
    print("Example 6: Custom Agent Task")
    print("=" * 60)
    
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    pipeline = SecurityPipeline('config.yml')
    agent_manager = AgentManager(config, pipeline, verbose=True)
    
    # Define custom task
    custom_task = """
    Analyze the test samples directory for security vulnerabilities.
    Focus on:
    1. SQL injection patterns
    2. Command injection risks
    3. Insecure cryptography
    
    Provide a prioritized list of issues with severity ratings.
    """
    
    print("\n🤖 Running custom task...")
    result = agent_manager.agent.run(custom_task)
    
    print(f"\n✅ Task completed!")
    print(f"Status: {result['status']}")
    print(f"Iterations: {result['iterations']}")


def main():
    """Run all examples"""
    print("\n🤖 ReAct Security Agent Examples\n")
    
    examples = [
        ("Autonomous Scan", example_1_autonomous_scan),
        ("Fix Vulnerability", example_2_fix_vulnerability),
        ("Analyze Codebase", example_3_analyze_codebase),
        ("Hybrid Pipeline", example_4_hybrid_pipeline),
        ("Memory Usage", example_5_memory_usage),
        ("Custom Task", example_6_custom_task),
    ]
    
    print("Available examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print(f"  0. Run all examples")
    
    try:
        choice = input("\nSelect example (0-6): ").strip()
        
        if choice == "0":
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"\n❌ Error in {name}: {e}")
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            name, func = examples[int(choice) - 1]
            func()
        else:
            print("Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()

# Made with Bob
