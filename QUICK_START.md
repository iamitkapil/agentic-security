# 🚀 Quick Start Guide - Using Your Autonomous Security Agent

## Step-by-Step Setup

### 1. Install the Agent

```bash
# Navigate to your project directory
cd c:/Users/AmitKapil/Projects/agentic-security

# Install the package (this registers the agent CLI)
pip install -e .

# Verify installation
agentic-agent --help
```

You should see the agent commands listed.

### 2. Set Up API Keys

The agent needs an AI model to work. Add your API key to `.env`:

```bash
# Create or edit .env file
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
# OR
echo "OPENAI_API_KEY=your_key_here" >> .env
```

Get API keys from:
- Anthropic: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/api-keys

### 3. Configure the Agent (Optional)

The agent is already configured in `config.yml`. You can adjust settings:

```yaml
agent:
  enabled: true
  autonomous: false      # Set to true for full autonomy
  auto_fix: false        # Set to true to auto-apply fixes
  auto_pr: false         # Set to true to auto-create PRs
  max_iterations: 10
```

## 🎯 Usage Examples

### Example 1: Scan Your Code (Recommended First Step)

```bash
# Scan the src directory for vulnerabilities
agentic-agent autonomous-scan --path ./src

# Scan with verbose output to see agent reasoning
agentic-agent autonomous-scan --path ./src --verbose
```

**What happens:**
1. Agent scans your code for security issues
2. Analyzes each vulnerability found
3. Provides detailed report
4. Suggests fixes (but doesn't apply them unless auto_fix is enabled)

### Example 2: Analyze Your Codebase

```bash
# Get a comprehensive security analysis
agentic-agent analyze --path ./src
```

**What you get:**
- Security posture assessment
- Risk prioritization
- Detailed recommendations
- No changes made to your code

### Example 3: Interactive Mode (Chat with Agent)

```bash
# Start interactive mode
agentic-agent interactive
```

Then you can ask questions like:
```
Task> Scan for SQL injection vulnerabilities in the src directory
Task> What are the most critical security issues?
Task> Explain how to fix the XSS vulnerability in app.py
Task> quit
```

### Example 4: Fix a Specific Vulnerability

```bash
# Fix a known vulnerability
agentic-agent fix-vulnerability src/app.py 42 sql_injection
```

Replace:
- `src/app.py` with your file path
- `42` with the line number
- `sql_injection` with the vulnerability type

### Example 5: Run Full Pipeline

```bash
# Run complete security pipeline (scan + analyze + fix)
agentic-agent run-pipeline --mode autonomous

# Or use hybrid mode (mix of agent and traditional)
agentic-agent run-pipeline --mode hybrid
```

### Example 6: Check Agent Status

```bash
# See what the agent has done
agentic-agent status
```

## 📋 Common Commands

```bash
# Scan code
agentic-agent autonomous-scan --path ./src

# Analyze security
agentic-agent analyze --path ./src

# Interactive chat
agentic-agent interactive

# Run full pipeline
agentic-agent run-pipeline --mode autonomous

# Check status
agentic-agent status

# View version
agentic-agent version

# Export agent memory
agentic-agent export-memory --output my_memory.json

# Get help
agentic-agent --help
```

## 🔧 Configuration Options

### Safe Mode (Recommended for First Use)

```yaml
agent:
  autonomous: false      # Agent asks for approval
  auto_fix: false        # Don't auto-apply fixes
  auto_pr: false         # Don't auto-create PRs
  behavior:
    confirm_actions: true  # Confirm each action
```

### Autonomous Mode (After Testing)

```yaml
agent:
  autonomous: true       # Full autonomy
  auto_fix: true         # Auto-apply fixes
  auto_pr: true          # Auto-create PRs
  behavior:
    confirm_actions: false
```

## 📝 Python Usage

You can also use the agent in your Python code:

```python
import yaml
from agentic_security.security_pipeline import SecurityPipeline
from agentic_security.agent.agent_manager import AgentManager
from agentic_security.agent.integration import AgentPipelineIntegration

# Load config
with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize
pipeline = SecurityPipeline('config.yml')
integration = AgentPipelineIntegration(pipeline, config, verbose=True)

# Run autonomous scan
result = integration.agent_manager.run_autonomous_scan('./src')
print(f"Status: {result['status']}")
print(f"Result: {result['final_result']}")
```

## 🎓 Learning Path

### Day 1: Exploration
1. Run `agentic-agent analyze --path ./src`
2. Review the analysis
3. Try interactive mode: `agentic-agent interactive`

### Day 2: Testing
1. Run `agentic-agent autonomous-scan --path ./tests`
2. Let it find vulnerabilities
3. Review the findings

### Day 3: Fixing
1. Enable auto_fix in config.yml
2. Run `agentic-agent autonomous-scan --path ./src`
3. Review the fixes applied

### Day 4: Automation
1. Enable full autonomous mode
2. Run `agentic-agent run-pipeline --mode autonomous`
3. Review the PR created

## 🔍 What the Agent Does

### Autonomous Scan Workflow

```
1. SCAN
   └─ Searches your code for security patterns
   └─ Identifies vulnerabilities (SQL injection, XSS, etc.)

2. ANALYZE
   └─ Examines each vulnerability in detail
   └─ Assesses risk and severity
   └─ Prioritizes fixes

3. PLAN
   └─ Creates a strategic plan
   └─ Determines fix order
   └─ Identifies dependencies

4. FIX (if enabled)
   └─ Generates secure code
   └─ Applies fixes
   └─ Validates changes

5. VALIDATE
   └─ Runs tests
   └─ Verifies fixes work
   └─ Checks for regressions

6. REPORT
   └─ Creates detailed report
   └─ Generates PR (if enabled)
   └─ Saves execution log
```

## 🛡️ Safety Features

The agent has multiple safety features:

1. **Confirmation Mode**: Asks before making changes (default)
2. **Rollback**: Automatically reverts failed changes
3. **Dry Run**: Analyze without making changes
4. **Execution Log**: Full audit trail of all actions
5. **Memory**: Learns from mistakes

## 📊 Understanding Output

### Scan Results
```json
{
  "status": "completed",
  "iterations": 5,
  "final_result": "Found 3 vulnerabilities: 2 SQL injection, 1 XSS"
}
```

### Agent Reasoning
When verbose mode is enabled, you'll see:
```
THOUGHT: I need to scan for SQL injection
ACTION: SCAN_CODE
ACTION INPUT: {"path": "./src", "scan_type": "sql_injection"}
OBSERVATION: Found 2 SQL injection vulnerabilities
```

## 🐛 Troubleshooting

### "API key not found"
```bash
# Add your API key to .env
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

### "Command not found: agentic-agent"
```bash
# Reinstall the package
pip install -e .
```

### "No vulnerabilities found"
```bash
# Try scanning a different path
agentic-agent autonomous-scan --path ./tests/samples
```

### Agent not making changes
```bash
# Check config.yml - auto_fix should be true
# Or use interactive mode to manually approve changes
```

## 📚 More Resources

- **Full Documentation**: [`docs/AGENT_GUIDE.md`](docs/AGENT_GUIDE.md)
- **Examples**: [`examples/agent_example.py`](examples/agent_example.py)
- **Configuration**: [`config.yml`](config.yml)
- **Tests**: [`tests/test_agent.py`](tests/test_agent.py)

## 💡 Tips

1. **Start with analysis** - Don't enable auto_fix until you're comfortable
2. **Use verbose mode** - See what the agent is thinking
3. **Review logs** - Check `agent_execution_log.json` after each run
4. **Export memory** - Backup agent learning regularly
5. **Test on samples** - Try on `tests/samples/` directory first

## 🎯 Your First Command

Try this right now:

```bash
# Analyze your test samples
agentic-agent analyze --path ./tests/samples --verbose
```

This will:
- ✅ Not modify any code
- ✅ Show you what the agent finds
- ✅ Display agent reasoning (verbose mode)
- ✅ Give you a feel for how it works

## 🚀 Next Steps

1. Run the first command above
2. Review the output
3. Try interactive mode
4. Read the full guide when ready
5. Enable auto_fix when comfortable

---

**Need Help?** Check [`docs/AGENT_GUIDE.md`](docs/AGENT_GUIDE.md) for detailed documentation.

**Ready to go?** Run: `agentic-agent analyze --path ./src --verbose`