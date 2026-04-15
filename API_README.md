# Agentic Security API

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file with your API keys:

```bash
# Required: At least one AI provider API key
ANTHROPIC_API_KEY=your_anthropic_key_here
# OR
OPENAI_API_KEY=your_openai_key_here

# Optional: For Slack notifications
SLACK_WEBHOOK=your_slack_webhook_url
```

### 3. Run the API Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Or with auto-reload for development:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Access the API

- **API Documentation (Swagger UI)**: http://localhost:8000/docs
- **Alternative Documentation (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Health & Status

- `GET /` or `GET /health` - Health check and system status

### Security Scanning

- `POST /api/v1/scan` - Start a security scan
  ```json
  {
    "target": "./src",
    "config_file": "config.yml",
    "timeout": 300
  }
  ```

- `GET /api/v1/scan/{scan_id}` - Get scan status and results
- `GET /api/v1/scans` - List all scans

### Agent Operations

- `POST /api/v1/agent/task` - Create a new agent task
  ```json
  {
    "task": "Analyze the codebase for security vulnerabilities",
    "mode": "autonomous",
    "max_iterations": 10
  }
  ```

- `GET /api/v1/agent/task/{task_id}` - Get agent task status
- `GET /api/v1/agent/capabilities` - Get agent capabilities

### Configuration

- `GET /api/v1/config` - Get current configuration

## Example Usage

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Start a security scan
curl -X POST http://localhost:8000/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "./src", "timeout": 300}'

# Create an agent task
curl -X POST http://localhost:8000/api/v1/agent/task \
  -H "Content-Type: application/json" \
  -d '{"task": "Scan for SQL injection vulnerabilities", "mode": "autonomous"}'
```

### Using Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Start a scan
scan_data = {
    "target": "./src",
    "timeout": 300
}
response = requests.post("http://localhost:8000/api/v1/scan", json=scan_data)
scan_id = response.json()["scan_id"]
print(f"Scan started: {scan_id}")

# Check scan status
response = requests.get(f"http://localhost:8000/api/v1/scan/{scan_id}")
print(response.json())
```

## Configuration

The API uses `config.yml` for configuration. Key settings:

```yaml
security:
  critical_threshold: 7.0
  max_fix_attempts: 3

agent:
  enabled: true
  autonomous: false
  max_iterations: 10
  
ai:
  models:
    architecture_review: gpt-4-1106-preview
    fix_implementation: claude-3-sonnet-20240229
```

## Troubleshooting

### Module Import Errors

If you get import errors, ensure the `src` directory is in your Python path:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

Or on Windows:
```powershell
$env:PYTHONPATH = "$env:PYTHONPATH;$(Get-Location)\src"
```

### Missing Dependencies

Install all required dependencies:

```bash
pip install -r requirements.txt
```

### API Key Issues

Ensure your `.env` file is in the project root and contains valid API keys:

```bash
# Check if .env file exists
ls -la .env

# Verify environment variables are loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('ANTHROPIC_API_KEY:', 'SET' if os.getenv('ANTHROPIC_API_KEY') else 'NOT SET')"
```

## Development

### Running with Auto-Reload

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running in Debug Mode

```bash
export SECURITY_DEBUG=true
uvicorn main:app --reload --log-level debug
```

### Testing the API

```bash
# Run tests
pytest tests/

# Test specific endpoint
curl -X GET http://localhost:8000/health -v
```

## Production Deployment

For production, consider:

1. Using a production ASGI server like Gunicorn with Uvicorn workers:
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

2. Setting up proper logging and monitoring
3. Using environment variables for sensitive configuration
4. Implementing rate limiting and authentication
5. Running behind a reverse proxy (nginx, traefik, etc.)

## Docker Deployment

Build and run with Docker:

```bash
docker build -t agentic-security-api .
docker run -p 8000:8000 --env-file .env agentic-security-api
```

Or use docker-compose:

```bash
docker-compose up