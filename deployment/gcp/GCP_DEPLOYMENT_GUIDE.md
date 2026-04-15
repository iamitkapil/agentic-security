# 🚀 GCP VM Deployment Guide - Agentic Security Agent

Complete guide to deploy your Agentic Security agent on Google Cloud Platform VM.

---

## 📋 Prerequisites

1. **GCP Account** with billing enabled
2. **gcloud CLI** installed on your local machine
3. **API Keys** (Anthropic or OpenAI)
4. **GitHub Account** for creating PRs

---

## 🎯 Quick Deployment (5 Minutes)

### Step 1: Create GCP VM

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Create VM instance
gcloud compute instances create agentic-security-vm \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --boot-disk-size=50GB \
    --boot-disk-type=pd-standard \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --tags=http-server,https-server \
    --metadata=startup-script='#!/bin/bash
    apt-get update
    apt-get install -y git curl
    '
```

### Step 2: SSH into VM

```bash
gcloud compute ssh agentic-security-vm --zone=us-central1-a
```

### Step 3: Run Setup Script

```bash
# Download and run setup script
curl -fsSL https://raw.githubusercontent.com/ruvnet/agentic-security/main/deployment/gcp/setup_vm.sh | bash

# Or if you have the repo locally, copy the script:
# gcloud compute scp deployment/gcp/setup_vm.sh agentic-security-vm:~ --zone=us-central1-a
# ssh into VM and run: bash setup_vm.sh
```

### Step 4: Configure API Keys

```bash
# Edit .env file
cd /opt/agentic-security
nano .env

# Add your keys:
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
```

### Step 5: Authenticate GitHub

```bash
gh auth login
# Follow the prompts to authenticate
```

### Step 6: Test the Agent

```bash
# Activate virtual environment
cd /opt/agentic-security
source venv/bin/activate

# Test the agent
agentic-agent --help
agentic-agent version

# Run a test scan
agentic-agent analyze --path ./tests/samples --verbose
```

---

## 🔧 Detailed Setup

### Option A: Automated Setup (Recommended)

Use the provided setup script:

```bash
# On your GCP VM
wget https://raw.githubusercontent.com/ruvnet/agentic-security/main/deployment/gcp/setup_vm.sh
chmod +x setup_vm.sh
./setup_vm.sh
```

### Option B: Manual Setup

#### 1. Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### 2. Install Python 3.10+

```bash
sudo apt-get install -y python3.10 python3.10-venv python3-pip
```

#### 3. Install Git and GitHub CLI

```bash
sudo apt-get install -y git

# GitHub CLI
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt-get update
sudo apt-get install -y gh
```

#### 4. Clone and Install Agent

```bash
# Create directory
sudo mkdir -p /opt/agentic-security
sudo chown $USER:$USER /opt/agentic-security
cd /opt/agentic-security

# Clone repository
git clone https://github.com/ruvnet/agentic-security.git .

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install
pip install --upgrade pip
pip install -e .
```

#### 5. Configure Environment

```bash
# Create .env file
cat > .env << 'EOF'
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
SLACK_WEBHOOK=your_webhook_here
EOF

# Edit with your actual keys
nano .env
```

---

## ⚙️ Running the Agent

### Manual Execution

```bash
cd /opt/agentic-security
source venv/bin/activate

# Scan a repository
agentic-agent autonomous-scan --path /path/to/repo

# Run full pipeline
agentic-agent run-pipeline --mode autonomous

# Interactive mode
agentic-agent interactive
```

### As a Service

```bash
# Start the service
sudo systemctl start agentic-security

# Enable on boot
sudo systemctl enable agentic-security

# Check status
sudo systemctl status agentic-security

# View logs
sudo journalctl -u agentic-security -f
```

### Scheduled Scans (Cron)

The setup script creates a daily cron job. To customize:

```bash
# Edit crontab
crontab -e

# Examples:
# Every day at 2 AM
0 2 * * * cd /opt/agentic-security && /opt/agentic-security/venv/bin/agentic-agent run-pipeline --mode autonomous

# Every 6 hours
0 */6 * * * cd /opt/agentic-security && /opt/agentic-security/venv/bin/agentic-agent autonomous-scan --path /repos

# Every Monday at 9 AM
0 9 * * 1 cd /opt/agentic-security && /opt/agentic-security/venv/bin/agentic-agent run-pipeline --mode autonomous
```

---

## 🔄 Scanning GitHub Repositories

### Method 1: Clone and Scan

```bash
cd /opt/agentic-security
source venv/bin/activate

# Clone repository
git clone https://github.com/username/repo.git /tmp/repo-to-scan

# Scan it
cd /tmp/repo-to-scan
agentic-agent run-pipeline --mode autonomous

# The agent will:
# 1. Scan for vulnerabilities
# 2. Fix them
# 3. Create a PR
```

### Method 2: Automated Script

Create `/opt/agentic-security/scan_repo.sh`:

```bash
#!/bin/bash
# Scan any GitHub repository

REPO_URL=$1
REPO_NAME=$(basename $REPO_URL .git)
WORK_DIR="/tmp/scans/$REPO_NAME"

# Clone
rm -rf $WORK_DIR
git clone $REPO_URL $WORK_DIR

# Scan
cd $WORK_DIR
source /opt/agentic-security/venv/bin/activate
agentic-agent run-pipeline --mode autonomous

# Cleanup
cd /opt/agentic-security
rm -rf $WORK_DIR

echo "Scan complete for $REPO_NAME"
```

Usage:
```bash
chmod +x /opt/agentic-security/scan_repo.sh
/opt/agentic-security/scan_repo.sh https://github.com/username/repo.git
```

### Method 3: Batch Scanning

Create `/opt/agentic-security/repos.txt`:
```
https://github.com/user/repo1.git
https://github.com/user/repo2.git
https://github.com/user/repo3.git
```

Create `/opt/agentic-security/batch_scan.sh`:
```bash
#!/bin/bash
while IFS= read -r repo; do
    echo "Scanning $repo..."
    /opt/agentic-security/scan_repo.sh "$repo"
done < /opt/agentic-security/repos.txt
```

---

## 📊 Monitoring and Logs

### View Logs

```bash
# Service logs
sudo journalctl -u agentic-security -f

# Application logs
tail -f /var/log/agentic-security/*.log

# Cron logs
tail -f /var/log/agentic-security/cron.log
```

### Check Agent Status

```bash
cd /opt/agentic-security
source venv/bin/activate
agentic-agent status
```

### View Execution History

```bash
cd /opt/agentic-security
cat agent_execution_log.json | jq '.'
```

---

## 🔒 Security Best Practices

### 1. Secure API Keys

```bash
# Restrict .env file permissions
chmod 600 /opt/agentic-security/.env

# Use GCP Secret Manager (recommended)
gcloud secrets create anthropic-api-key --data-file=- <<< "your_key"
gcloud secrets create openai-api-key --data-file=- <<< "your_key"

# Access in scripts:
export ANTHROPIC_API_KEY=$(gcloud secrets versions access latest --secret="anthropic-api-key")
```

### 2. Firewall Rules

```bash
# Allow only SSH
gcloud compute firewall-rules create allow-ssh \
    --allow tcp:22 \
    --source-ranges 0.0.0.0/0 \
    --target-tags agentic-security-vm

# Restrict to your IP
gcloud compute firewall-rules create allow-ssh-my-ip \
    --allow tcp:22 \
    --source-ranges YOUR_IP/32 \
    --target-tags agentic-security-vm
```

### 3. Regular Updates

```bash
# Create update script
cat > /opt/agentic-security/update.sh << 'EOF'
#!/bin/bash
cd /opt/agentic-security
git pull
source venv/bin/activate
pip install --upgrade -e .
sudo systemctl restart agentic-security
EOF

chmod +x /opt/agentic-security/update.sh

# Run weekly
(crontab -l; echo "0 3 * * 0 /opt/agentic-security/update.sh") | crontab -
```

---

## 💰 Cost Optimization

### VM Sizing

```bash
# Small repos (< 1000 files)
--machine-type=e2-small  # $13/month

# Medium repos (1000-5000 files)
--machine-type=e2-medium  # $27/month

# Large repos (> 5000 files)
--machine-type=e2-standard-2  # $49/month
```

### Preemptible VMs (70% cheaper)

```bash
gcloud compute instances create agentic-security-vm \
    --preemptible \
    --machine-type=e2-medium \
    # ... other flags
```

### Scheduled Start/Stop

```bash
# Stop VM when not in use
gcloud compute instances stop agentic-security-vm --zone=us-central1-a

# Start VM
gcloud compute instances start agentic-security-vm --zone=us-central1-a

# Automate with Cloud Scheduler
gcloud scheduler jobs create http start-vm \
    --schedule="0 8 * * 1-5" \
    --uri="https://compute.googleapis.com/compute/v1/projects/PROJECT_ID/zones/us-central1-a/instances/agentic-security-vm/start" \
    --http-method=POST
```

---

## 🔧 Troubleshooting

### Agent Not Starting

```bash
# Check service status
sudo systemctl status agentic-security

# Check logs
sudo journalctl -u agentic-security -n 50

# Test manually
cd /opt/agentic-security
source venv/bin/activate
agentic-agent --help
```

### API Key Issues

```bash
# Verify .env file
cat /opt/agentic-security/.env

# Test API connection
cd /opt/agentic-security
source venv/bin/activate
python3 << 'EOF'
import os
from dotenv import load_dotenv
load_dotenv()
print("ANTHROPIC_API_KEY:", os.getenv("ANTHROPIC_API_KEY")[:10] + "...")
EOF
```

### GitHub Authentication

```bash
# Re-authenticate
gh auth login

# Check status
gh auth status

# Test
gh repo list
```

### Memory Issues

```bash
# Check memory usage
free -h

# Increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 📈 Scaling

### Multiple VMs

```bash
# Create multiple VMs for parallel scanning
for i in {1..3}; do
    gcloud compute instances create agentic-security-vm-$i \
        --zone=us-central1-a \
        --machine-type=e2-medium \
        # ... other flags
done
```

### Load Balancing

```bash
# Create instance group
gcloud compute instance-groups managed create agentic-security-group \
    --base-instance-name=agentic-security \
    --size=3 \
    --zone=us-central1-a
```

---

## 🎯 Example Workflows

### Workflow 1: Daily Security Scan

```bash
# /opt/agentic-security/daily_scan.sh
#!/bin/bash
cd /opt/agentic-security
source venv/bin/activate

# Scan all repos in organization
gh repo list YOUR_ORG --limit 100 --json name,url | jq -r '.[].url' | while read repo; do
    echo "Scanning $repo..."
    /opt/agentic-security/scan_repo.sh "$repo"
done

# Send summary
echo "Daily scan complete" | mail -s "Security Scan Summary" admin@example.com
```

### Workflow 2: PR-Triggered Scan

```bash
# Use GitHub webhooks to trigger scans on new PRs
# Setup webhook endpoint on VM
# Agent scans PR changes and comments on PR
```

### Workflow 3: Continuous Monitoring

```bash
# Monitor specific repos continuously
while true; do
    agentic-agent autonomous-scan --path /repos/critical-app
    sleep 3600  # Every hour
done
```

---

## 📚 Additional Resources

- **GCP Documentation**: https://cloud.google.com/compute/docs
- **Agent Guide**: [`docs/AGENT_GUIDE.md`](../../docs/AGENT_GUIDE.md)
- **Quick Start**: [`QUICK_START.md`](../../QUICK_START.md)
- **GitHub CLI**: https://cli.github.com/manual/

---

## ✅ Deployment Checklist

- [ ] GCP VM created
- [ ] Setup script executed
- [ ] API keys configured in .env
- [ ] GitHub CLI authenticated
- [ ] Agent tested successfully
- [ ] Service enabled and running
- [ ] Cron jobs configured
- [ ] Firewall rules set
- [ ] Monitoring setup
- [ ] Backup strategy in place

---

**Your Agentic Security agent is now running on GCP!** 🎉

For support, check the documentation or create an issue on GitHub.