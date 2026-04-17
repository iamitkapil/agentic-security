# Cloud Deployment Guide for Agentic Security API

This guide covers deploying the Agentic Security API to cloud environments (GCP, AWS, Azure, etc.).

## Prerequisites

- Python 3.10 or higher
- Git
- Cloud VM or container service access

## Quick Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/agentic-security.git
cd agentic-security
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Create .env file
cat > .env << 'EOF'
# Required: At least one AI provider API key
ANTHROPIC_API_KEY=your_anthropic_key_here
# OR
OPENAI_API_KEY=your_openai_key_here

# Optional: Model selection
ANALYSIS_MODEL=claude-3-sonnet-20240229

# Optional: Slack notifications
SLACK_WEBHOOK=your_slack_webhook_url

# Optional: Debug mode
SECURITY_DEBUG=false
EOF
```

### 5. Verify Installation

```bash
# Test imports
python -c "import sys; sys.path.insert(0, 'src'); from main import app; print('Installation successful!')"
```

### 6. Run the Server

```bash
# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000

# Or with more workers for production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Troubleshooting

### Common Issues

#### 1. SyntaxError: f-string expression part cannot include a backslash

**Solution:** This has been fixed in the latest version. Make sure you have the latest code:

```bash
git pull origin main
```

#### 2. ModuleNotFoundError: No module named 'defusedxml'

**Solution:** Install missing dependencies:

```bash
pip install -r requirements.txt
```

#### 3. Import errors with agentic_security module

**Solution:** Ensure the src directory is in Python path:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

Or add to your shell profile:

```bash
echo 'export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"' >> ~/.bashrc
source ~/.bashrc
```

#### 4. Config file not found

**Solution:** Ensure `config.yml` exists in the project root:

```bash
ls -la config.yml
```

If missing, copy from example:

```bash
cp config.yml.example config.yml
```

### Verification Commands

```bash
# Check Python version (should be 3.10+)
python --version

# Check if virtual environment is activated
which python

# List installed packages
pip list

# Test FastAPI import
python -c "from fastapi import FastAPI; print('FastAPI OK')"

# Test uvicorn
uvicorn --version

# Test main.py import
python -c "import sys; sys.path.insert(0, 'src'); from main import app; print('Main app OK')"
```

## Production Deployment Options

### Option 1: Systemd Service (Linux)

Create `/etc/systemd/system/agentic-security.service`:

```ini
[Unit]
Description=Agentic Security API
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/agentic-security
Environment="PATH=/path/to/agentic-security/venv/bin"
Environment="PYTHONPATH=/path/to/agentic-security/src"
ExecStart=/path/to/agentic-security/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable agentic-security
sudo systemctl start agentic-security
sudo systemctl status agentic-security
```

### Option 2: Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t agentic-security-api .

# Run container
docker run -d \
  --name agentic-security \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/config.yml:/app/config.yml \
  agentic-security-api
```

### Option 3: Docker Compose

```bash
docker-compose up -d
```

### Option 4: Gunicorn with Uvicorn Workers

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

## Cloud-Specific Guides

### Google Cloud Platform (GCP)

#### Using Compute Engine

```bash
# SSH into VM
gcloud compute ssh your-instance-name

# Follow standard deployment steps above

# Open firewall for port 8000
gcloud compute firewall-rules create allow-agentic-security \
  --allow tcp:8000 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow Agentic Security API"
```

#### Using Cloud Run

```bash
# Build and deploy
gcloud run deploy agentic-security \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=your_key
```

### AWS

#### Using EC2

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Follow standard deployment steps

# Configure security group to allow port 8000
```

#### Using ECS/Fargate

Use the provided Dockerfile and deploy to ECS.

### Azure

#### Using Virtual Machines

```bash
# SSH into VM
ssh azureuser@your-vm-ip

# Follow standard deployment steps
```

#### Using Container Instances

```bash
az container create \
  --resource-group your-rg \
  --name agentic-security \
  --image your-registry/agentic-security:latest \
  --dns-name-label agentic-security \
  --ports 8000
```

## Monitoring and Logs

### View Logs

```bash
# If using systemd
sudo journalctl -u agentic-security -f

# If running directly
# Logs will appear in terminal

# If using Docker
docker logs -f agentic-security
```

### Health Check

```bash
# Check if API is running
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0",...}
```

## Security Considerations

1. **Use HTTPS in production** - Set up a reverse proxy (nginx, traefik) with SSL
2. **Restrict API access** - Use firewall rules or API authentication
3. **Secure environment variables** - Use cloud secret managers
4. **Regular updates** - Keep dependencies updated
5. **Monitor logs** - Set up log aggregation and monitoring

## Performance Tuning

### Recommended Settings for Production

```bash
# Number of workers (2-4 x CPU cores)
--workers 4

# Worker timeout
--timeout 120

# Keep-alive connections
--keep-alive 5

# Max requests per worker (restart after N requests)
--max-requests 1000
--max-requests-jitter 50
```

### Example Production Command

```bash
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --timeout-keep-alive 5 \
  --log-level info \
  --access-log \
  --use-colors
```

## Backup and Recovery

### Backup Important Files

```bash
# Backup configuration
cp config.yml config.yml.backup

# Backup environment variables
cp .env .env.backup

# Backup agent memory (if using agent features)
tar -czf agent_memory_backup.tar.gz .agent_memory/
```

## Support

For issues or questions:
- Check the [API_README.md](API_README.md) for API usage
- Review logs for error messages
- Ensure all dependencies are installed
- Verify environment variables are set correctly

## Quick Reference

```bash
# Start server
uvicorn main:app --host 0.0.0.0 --port 8000

# Start with reload (development)
uvicorn main:app --reload

# Check health
curl http://localhost:8000/health

# View API docs
# Open browser: http://localhost:8000/docs

# Stop server
# Press Ctrl+C or kill the process