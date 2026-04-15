#!/usr/bin/env python3
"""
Agent CLI - Command-line interface for the ReAct security agent
Provides commands for autonomous security operations
"""

import click
import yaml
import os
import sys
from pathlib import Path
from typing import Optional
import logging

from .agent.agent_manager import AgentManager
from .agent.integration import AgentPipelineIntegration
from .security_pipeline import SecurityPipeline
from .security_cli import COLORS, DECORATORS, CYBER_BANNER

logger = logging.getLogger(__name__)


AGENT_BANNER = f"""
{COLORS['neon_purple']}
    ╔═══════════════════════════════════════════════════════════╗
    ║           🤖 AUTONOMOUS SECURITY AGENT MODE 🤖           ║
    ║              ReAct Pattern | Self-Learning               ║
    ╚═══════════════════════════════════════════════════════════╝
{COLORS['reset']}
"""


@click.group()
@click.option('--config', '-c', default='config.yml', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def agent_cli(ctx, config, verbose):
    """Autonomous Security Agent - ReAct Pattern"""
    ctx.ensure_object(dict)
    ctx.obj['config_file'] = config
    ctx.obj['verbose'] = verbose
    
    # Setup logging
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


@agent_cli.command()
@click.option('--path', '-p', default='.', help='Path to scan')
@click.option('--auto-fix', is_flag=True, help='Automatically apply fixes')
@click.pass_context
def autonomous_scan(ctx, path, auto_fix):
    """Run autonomous security scan with agent"""
    print(AGENT_BANNER)
    print(f"{COLORS['neon_green']}🔍 Starting autonomous security scan...{COLORS['reset']}\n")
    
    try:
        # Load config
        with open(ctx.obj['config_file'], 'r') as f:
            config = yaml.safe_load(f)
        
        # Initialize pipeline and agent
        pipeline = SecurityPipeline(ctx.obj['config_file'])
        integration = AgentPipelineIntegration(pipeline, config, ctx.obj['verbose'])
        
        # Run autonomous scan
        print(f"{COLORS['neon_blue']}📊 Agent analyzing codebase...{COLORS['reset']}")
        result = integration.agent_manager.run_autonomous_scan(path)
        
        # Display results
        print(f"\n{COLORS['neon_green']}✅ Scan completed!{COLORS['reset']}")
        print(f"Status: {result['status']}")
        print(f"Iterations: {result['iterations']}")
        
        if result.get('final_result'):
            print(f"\n{COLORS['neon_yellow']}📋 Results:{COLORS['reset']}")
            print(result['final_result'])
        
        # Save execution log
        integration.agent_manager.save_execution_log(f"agent_scan_{path.replace('/', '_')}.json")
        
    except Exception as e:
        print(f"{COLORS['neon_red']}❌ Error: {e}{COLORS['reset']}")
        sys.exit(1)


@agent_cli.command()
@click.option('--path', '-p', default='.', help='Path to analyze')
@click.pass_context
def analyze(ctx, path):
    """Autonomous codebase security analysis"""
    print(AGENT_BANNER)
    print(f"{COLORS['neon_green']}🧠 Starting autonomous analysis...{COLORS['reset']}\n")
    
    try:
        with open(ctx.obj['config_file'], 'r') as f:
            config = yaml.safe_load(f)
        
        pipeline = SecurityPipeline(ctx.obj['config_file'])
        integration = AgentPipelineIntegration(pipeline, config, ctx.obj['verbose'])
        
        print(f"{COLORS['neon_blue']}🔬 Agent analyzing security posture...{COLORS['reset']}")
        result = integration.agent_manager.analyze_codebase(path)
        
        print(f"\n{COLORS['neon_green']}✅ Analysis completed!{COLORS['reset']}")
        print(f"Status: {result['status']}")
        
        if result.get('final_result'):
            print(f"\n{COLORS['neon_yellow']}📊 Analysis:{COLORS['reset']}")
            print(result['final_result'])
        
    except Exception as e:
        print(f"{COLORS['neon_red']}❌ Error: {e}{COLORS['reset']}")
        sys.exit(1)


@agent_cli.command()
@click.argument('file_path')
@click.argument('line_number', type=int)
@click.argument('vuln_type')
@click.pass_context
def fix_vulnerability(ctx, file_path, line_number, vuln_type):
    """Autonomously fix a specific vulnerability"""
    print(AGENT_BANNER)
    print(f"{COLORS['neon_green']}🔧 Fixing {vuln_type} vulnerability...{COLORS['reset']}\n")
    
    try:
        with open(ctx.obj['config_file'], 'r') as f:
            config = yaml.safe_load(f)
        
        pipeline = SecurityPipeline(ctx.obj['config_file'])
        integration = AgentPipelineIntegration(pipeline, config, ctx.obj['verbose'])
        
        print(f"{COLORS['neon_blue']}🤖 Agent generating fix...{COLORS['reset']}")
        result = integration.agent_manager.fix_vulnerability(file_path, line_number, vuln_type)
        
        print(f"\n{COLORS['neon_green']}✅ Fix completed!{COLORS['reset']}")
        print(f"Status: {result['status']}")
        
        if result.get('final_result'):
            print(f"\n{COLORS['neon_yellow']}🔧 Fix Details:{COLORS['reset']}")
            print(result['final_result'])
        
    except Exception as e:
        print(f"{COLORS['neon_red']}❌ Error: {e}{COLORS['reset']}")
        sys.exit(1)


@agent_cli.command()
@click.option('--mode', type=click.Choice(['autonomous', 'hybrid']), default='autonomous')
@click.pass_context
def run_pipeline(ctx, mode):
    """Run full security pipeline with agent"""
    print(AGENT_BANNER)
    print(f"{COLORS['neon_green']}🚀 Running {mode} pipeline...{COLORS['reset']}\n")
    
    try:
        with open(ctx.obj['config_file'], 'r') as f:
            config = yaml.safe_load(f)
        
        pipeline = SecurityPipeline(ctx.obj['config_file'])
        integration = AgentPipelineIntegration(pipeline, config, ctx.obj['verbose'])
        
        if mode == 'autonomous':
            print(f"{COLORS['neon_blue']}🤖 Agent running full autonomous pipeline...{COLORS['reset']}")
            result = integration.run_autonomous_pipeline()
        else:
            print(f"{COLORS['neon_blue']}🔄 Running hybrid pipeline...{COLORS['reset']}")
            result = integration.run_hybrid_pipeline()
        
        print(f"\n{COLORS['neon_green']}✅ Pipeline completed!{COLORS['reset']}")
        
        if 'summary' in result:
            summary = result['summary']
            print(f"\n{COLORS['neon_yellow']}📊 Summary:{COLORS['reset']}")
            print(f"  Total steps: {summary.get('total_steps', 0)}")
            print(f"  Completed: {summary.get('completed', 0)}")
            print(f"  Failed: {summary.get('failed', 0)}")
        
    except Exception as e:
        print(f"{COLORS['neon_red']}❌ Error: {e}{COLORS['reset']}")
        sys.exit(1)


@agent_cli.command()
@click.pass_context
def interactive(ctx):
    """Start agent in interactive mode"""
    print(AGENT_BANNER)
    print(f"{COLORS['neon_green']}💬 Starting interactive agent mode...{COLORS['reset']}\n")
    
    try:
        with open(ctx.obj['config_file'], 'r') as f:
            config = yaml.safe_load(f)
        
        pipeline = SecurityPipeline(ctx.obj['config_file'])
        integration = AgentPipelineIntegration(pipeline, config, ctx.obj['verbose'])
        
        # Run interactive mode
        integration.agent_manager.interactive_mode()
        
    except Exception as e:
        print(f"{COLORS['neon_red']}❌ Error: {e}{COLORS['reset']}")
        sys.exit(1)


@agent_cli.command()
@click.pass_context
def status(ctx):
    """Show agent status and statistics"""
    print(AGENT_BANNER)
    
    try:
        with open(ctx.obj['config_file'], 'r') as f:
            config = yaml.safe_load(f)
        
        pipeline = SecurityPipeline(ctx.obj['config_file'])
        integration = AgentPipelineIntegration(pipeline, config, ctx.obj['verbose'])
        
        # Get status
        agent_status = integration.agent_manager.get_agent_status()
        exec_summary = integration.agent_manager.get_execution_summary()
        
        print(f"{COLORS['neon_yellow']}🤖 Agent Status:{COLORS['reset']}")
        print(f"  State: {agent_status['state']}")
        print(f"  Total steps: {agent_status['total_steps']}")
        print(f"  Memory items: {agent_status['memory_items']}")
        print(f"  Executions: {agent_status['execution_count']}")
        
        if exec_summary.get('tasks'):
            print(f"\n{COLORS['neon_yellow']}📊 Execution Summary:{COLORS['reset']}")
            for task_type, count in exec_summary['tasks'].items():
                print(f"  {task_type}: {count}")
        
    except Exception as e:
        print(f"{COLORS['neon_red']}❌ Error: {e}{COLORS['reset']}")
        sys.exit(1)


@agent_cli.command()
@click.option('--output', '-o', default='agent_memory_export.json', help='Output file')
@click.pass_context
def export_memory(ctx, output):
    """Export agent memory to file"""
    print(f"{COLORS['neon_blue']}💾 Exporting agent memory...{COLORS['reset']}")
    
    try:
        from .agent.memory import AgentMemory
        
        memory = AgentMemory()
        memory.export_memory(output)
        
        stats = memory.get_statistics()
        print(f"{COLORS['neon_green']}✅ Memory exported to {output}{COLORS['reset']}")
        print(f"  Total entries: {stats['total_count']}")
        print(f"  Short-term: {stats['short_term_count']}")
        print(f"  Long-term: {stats['long_term_count']}")
        
    except Exception as e:
        print(f"{COLORS['neon_red']}❌ Error: {e}{COLORS['reset']}")
        sys.exit(1)


@agent_cli.command()
@click.argument('input_file')
@click.option('--merge', is_flag=True, help='Merge with existing memory')
@click.pass_context
def import_memory(ctx, input_file, merge):
    """Import agent memory from file"""
    print(f"{COLORS['neon_blue']}📥 Importing agent memory...{COLORS['reset']}")
    
    try:
        from .agent.memory import AgentMemory
        
        memory = AgentMemory()
        memory.import_memory(input_file, merge)
        
        stats = memory.get_statistics()
        print(f"{COLORS['neon_green']}✅ Memory imported from {input_file}{COLORS['reset']}")
        print(f"  Total entries: {stats['total_count']}")
        
    except Exception as e:
        print(f"{COLORS['neon_red']}❌ Error: {e}{COLORS['reset']}")
        sys.exit(1)


@agent_cli.command()
@click.pass_context
def clear_memory(ctx):
    """Clear agent memory"""
    print(f"{COLORS['neon_yellow']}⚠️  Clearing agent memory...{COLORS['reset']}")
    
    if click.confirm('Are you sure you want to clear all agent memory?'):
        try:
            from .agent.memory import AgentMemory
            
            memory = AgentMemory()
            memory.clear_all()
            
            print(f"{COLORS['neon_green']}✅ Memory cleared{COLORS['reset']}")
            
        except Exception as e:
            print(f"{COLORS['neon_red']}❌ Error: {e}{COLORS['reset']}")
            sys.exit(1)
    else:
        print("Cancelled")


@agent_cli.command()
@click.pass_context
def version(ctx):
    """Show agent version information"""
    print(AGENT_BANNER)
    print(f"{COLORS['neon_yellow']}Version:{COLORS['reset']} 1.0.0")
    print(f"{COLORS['neon_yellow']}Agent Type:{COLORS['reset']} ReAct (Reasoning + Acting)")
    print(f"{COLORS['neon_yellow']}Features:{COLORS['reset']}")
    print("  • Autonomous security scanning")
    print("  • Strategic planning")
    print("  • Self-learning capabilities")
    print("  • Persistent memory")
    print("  • Tool use and reasoning")


if __name__ == '__main__':
    agent_cli()

# Made with Bob
