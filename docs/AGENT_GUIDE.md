# 🤖 Autonomous Security Agent Guide

## Overview

The Agentic Security project now includes a **ReAct (Reasoning + Acting) Agent** that provides fully autonomous security analysis and remediation capabilities. The agent uses advanced AI reasoning to understand security issues, plan fixes, and execute them autonomously.

## What is a ReAct Agent?

The ReAct pattern combines:
- **Reasoning**: The agent thinks through problems step-by-step
- **Acting**: The agent uses tools to gather information and make changes
- **Observing**: The agent learns from the results of its actions

This creates a powerful autonomous system that can handle complex security tasks with minimal human intervention.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ReAct Agent Core                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Reasoning  │→ │    Acting    │→ │  Observing   │     │
│  │   (LLM)      │  │   (Tools)    │  │  (Results)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Agent Components                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Planner    │  │    Memory    │  │    Tools     │     │
│  │  (Strategy)  │  │  (Learning)  │  │  (Actions)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Integration with Security Pipeline             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Scanner    │  │   Analyzer   │  │    Fixer     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 🧠 Autonomous Reasoning
- Strategic planning for complex security tasks
- Multi-step problem decomposition
- Context-aware decision making
- Self-correction and adaptation

### 🛠️ Tool Use
- Code scanning and analysis
- Vulnerability detection
- Fix generation and application
- Test execution
- Git operations (branching, commits, PRs)

### 💾 Persistent Memory
- Learns from past executions
- Retains context across sessions
- Improves over time
- Exportable/importable memory

### 📊 Strategic Planning
- Creates detailed execution plans
- Manages dependencies between steps
- Prioritizes critical issues
- Handles failures gracefully

## Installation

The agent is included with the main installation:

```bash
# Install the package
pip install -e .

# Verify agent CLI is available
agentic-agent --help
```

## Configuration

Add agent configuration to your `config.yml`:

```yaml
agent:
  enabled: true                    # Enable agent mode
  autonomous: false                # Require manual approval
  auto_fix: false                  # Auto-apply fixes
  auto_pr: false                   # Auto-create PRs
  max_iterations: 10               # Max reasoning cycles
  memory_enabled: true             # Enable memory
  memory_dir: .agent_memory        # Memory location
  planning_enabled: true           # Enable planning
  learning_enabled: true           # Enable learning
  
  behavior:
    verbose: false                 # Detailed logging
    interactive: false             # Interactive mode
    confirm_actions: true          # Confirm actions
    rollback_on_failure: true      # Auto-rollback
    
  tools:
    scan_enabled: true
    analysis_enabled: true
    fix_enabled: true
    test_enabled: true
    git_enabled: true
```

## Usage

### Basic Commands

#### 1. Autonomous Scan
Run a complete autonomous security scan:

```bash
agentic-agent autonomous-scan --path ./src
```

The agent will:
1. Scan the codebase for vulnerabilities
2. Analyze each finding
3. Generate and apply fixes (if auto_fix enabled)
4. Validate the fixes
5. Create a report

#### 2. Analyze Codebase
Get a comprehensive security analysis:

```bash
agentic-agent analyze --path ./src
```

The agent provides:
- Security posture assessment
- Risk prioritization
- Detailed recommendations
- Architecture review

#### 3. Fix Specific Vulnerability
Autonomously fix a known vulnerability:

```bash
agentic-agent fix-vulnerability src/app.py 42 sql_injection
```

#### 4. Run Full Pipeline
Execute the complete security pipeline:

```bash
# Fully autonomous
agentic-agent run-pipeline --mode autonomous

# Hybrid (agent + traditional)
agentic-agent run-pipeline --mode hybrid
```

#### 5. Interactive Mode
Chat with the agent for custom tasks:

```bash
agentic-agent interactive
```

Example interaction:
```
Task> Scan for SQL injection vulnerabilities and fix the critical ones
🔄 Processing task...
✅ Task completed!
```

### Advanced Usage

#### Memory Management

Export agent memory:
```bash
agentic-agent export-memory --output my_memory.json
```

Import agent memory:
```bash
agentic-agent import-memory my_memory.json --merge
```

Clear memory:
```bash
agentic-agent clear-memory
```

#### Status and Monitoring

Check agent status:
```bash
agentic-agent status
```

View version info:
```bash
agentic-agent version
```

## Agent Workflow

### Autonomous Scan Workflow

```
1. INITIALIZATION
   ├─ Load configuration
   ├─ Initialize LLM client
   ├─ Load memory from previous runs
   └─ Prepare tools

2. PLANNING PHASE
   ├─ Analyze task requirements
   ├─ Create strategic plan
   ├─ Identify dependencies
   └─ Prioritize actions

3. EXECUTION PHASE
   ├─ For each planned step:
   │  ├─ THINK: Reason about what to do
   │  ├─ ACT: Execute tool/action
   │  ├─ OBSERVE: Process results
   │  └─ LEARN: Update memory
   └─ Handle failures and retry

4. VALIDATION PHASE
   ├─ Verify fixes applied correctly
   ├─ Run tests
   ├─ Check for regressions
   └─ Validate security improvements

5. REPORTING PHASE
   ├─ Generate comprehensive report
   ├─ Create PR (if enabled)
   ├─ Save execution log
   └─ Update memory
```

## Available Tools

The agent has access to these tools:

### Scanning Tools
- `SCAN_CODE`: Scan code for vulnerabilities
- `SEARCH_PATTERN`: Search for specific patterns
- `LIST_FILES`: List files in directory

### Analysis Tools
- `ANALYZE_VULNERABILITY`: Deep analysis of vulnerabilities
- `READ_FILE`: Read file contents
- `GET_SCAN_SUMMARY`: Get scan results summary

### Remediation Tools
- `GENERATE_FIX`: Generate secure fix
- `APPLY_FIX`: Apply fix to file
- `VALIDATE_FIX`: Verify fix correctness
- `ROLLBACK_CHANGES`: Undo changes

### Testing Tools
- `RUN_TESTS`: Execute test suite

### Git Tools
- `CREATE_BRANCH`: Create new branch
- `COMMIT_CHANGES`: Commit changes
- `CREATE_PR`: Create pull request

## Examples

### Example 1: Autonomous SQL Injection Fix

```bash
agentic-agent autonomous-scan --path ./src --auto-fix
```

Agent reasoning:
```
THOUGHT: I need to scan for SQL injection vulnerabilities
ACTION: SCAN_CODE
ACTION INPUT: {"path": "./src", "scan_type": "sql_injection"}
OBSERVATION: Found 3 SQL injection vulnerabilities

THOUGHT: I should analyze the most critical one first
ACTION: ANALYZE_VULNERABILITY
ACTION INPUT: {"file_path": "src/db.py", "line_number": 45, "vuln_type": "sql_injection"}
OBSERVATION: Using string formatting in SQL query, high risk

THOUGHT: I'll generate a secure fix using parameterized queries
ACTION: GENERATE_FIX
ACTION INPUT: {"file_path": "src/db.py", "line_number": 45, "vuln_type": "sql_injection"}
OBSERVATION: Generated fix using cursor.execute with parameters

THOUGHT: Now I'll apply the fix
ACTION: APPLY_FIX
ACTION INPUT: {"file_path": "src/db.py", "line_number": 45, "fixed_code": "..."}
OBSERVATION: Fix applied successfully

THOUGHT: I should validate the fix works
ACTION: VALIDATE_FIX
ACTION INPUT: {"file_path": "src/db.py", "line_number": 45}
OBSERVATION: Fix validated, no unsafe patterns detected

THOUGHT: Task complete, all SQL injections fixed
ACTION: FINISH
ACTION INPUT: {"result": "Fixed 3 SQL injection vulnerabilities"}
```

### Example 2: Interactive Security Review

```bash
agentic-agent interactive
```

```
Task> Review the authentication module for security issues

🔄 Processing task...

THOUGHT: I should first scan the authentication module
ACTION: LIST_FILES
OBSERVATION: Found auth.py, login.py, session.py

THOUGHT: Let me analyze each file for security issues
ACTION: SCAN_CODE
OBSERVATION: Found weak password hashing in auth.py

THOUGHT: I'll provide detailed recommendations
ACTION: ANALYZE_VULNERABILITY
OBSERVATION: Using MD5 for passwords, should use bcrypt

✅ Task completed!
Result: Found 1 critical issue - weak password hashing
Recommendation: Replace MD5 with bcrypt or argon2
```

## Best Practices

### 1. Start with Analysis
Before enabling auto-fix, run analysis first:
```bash
agentic-agent analyze --path ./src
```

### 2. Use Hybrid Mode Initially
Start with hybrid mode to understand agent behavior:
```bash
agentic-agent run-pipeline --mode hybrid
```

### 3. Enable Verbose Logging
For debugging, use verbose mode:
```bash
agentic-agent autonomous-scan --verbose
```

### 4. Regular Memory Exports
Backup agent memory regularly:
```bash
agentic-agent export-memory --output backup_$(date +%Y%m%d).json
```

### 5. Review Agent Actions
Always review the execution log:
```bash
cat agent_execution_log.json
```

## Safety Features

### Confirmation Mode
By default, the agent asks for confirmation:
```yaml
agent:
  behavior:
    confirm_actions: true
```

### Rollback on Failure
Automatic rollback if fixes fail:
```yaml
agent:
  behavior:
    rollback_on_failure: true
```

### Manual Approval
Require manual approval for all actions:
```yaml
agent:
  autonomous: false
  auto_fix: false
  auto_pr: false
```

## Troubleshooting

### Agent Not Finding Vulnerabilities
- Check scan targets in config.yml
- Verify file patterns are correct
- Enable verbose mode for details

### Fixes Not Being Applied
- Check `auto_fix` setting
- Verify file permissions
- Review execution log

### Memory Issues
- Clear memory if corrupted: `agentic-agent clear-memory`
- Check memory directory permissions
- Verify JSON format in memory files

### LLM Connection Issues
- Verify API keys in .env
- Check network connectivity
- Try different model in config

## Performance Tips

1. **Limit Iterations**: Set reasonable `max_iterations`
2. **Use Caching**: Enable memory for faster repeated tasks
3. **Targeted Scans**: Scan specific paths instead of entire codebase
4. **Batch Operations**: Group similar fixes together

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Autonomous Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install Agent
        run: |
          pip install -e .
      
      - name: Run Autonomous Scan
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          agentic-agent autonomous-scan --path ./src
      
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: security-report
          path: agent_execution_log.json
```

## Comparison: Traditional vs Agent Mode

| Feature | Traditional | Agent Mode |
|---------|------------|------------|
| Execution | Manual steps | Autonomous |
| Planning | User-defined | AI-generated |
| Adaptation | Fixed workflow | Dynamic |
| Learning | None | Continuous |
| Context | Limited | Full history |
| Decision Making | Rule-based | Reasoning-based |
| Error Handling | Manual | Self-correcting |

## Future Enhancements

- Multi-agent collaboration
- Advanced learning algorithms
- Custom tool creation
- Real-time monitoring
- Predictive security analysis

## Support

For issues or questions:
- GitHub Issues: [agentic-security/issues](https://github.com/ruvnet/agentic-security/issues)
- Documentation: [docs/](../docs/)
- Examples: [examples/](../examples/)

---

**Created by rUv** - Autonomous Security, Powered by AI