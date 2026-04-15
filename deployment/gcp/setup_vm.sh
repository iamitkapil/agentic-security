#!/bin/bash
# GCP VM Setup Script for Agentic Security Agent
# This script sets up the agent on a fresh GCP VM

set -e

echo "🚀 Setting up Agentic Security Agent on GCP VM..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.10+
echo "🐍 Installing Python 3.10..."
sudo apt-get install -y python3.10 python3.10-venv python3-pip

# Install Git
echo "📥 Installing Git..."
sudo apt-get install -y git

# Install GitHub CLI
echo "🔧 Installing GitHub CLI..."
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt-get update
sudo apt-get install -y gh

# Install Docker (optional, for containerized deployment)
echo "🐳 Installing Docker..."
sudo apt-get install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Create application directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/agentic-security
sudo chown $USER:$USER /opt/agentic-security
cd /opt/agentic-security

# Clone the repository
echo "📥 Cloning Agentic Security repository..."
git clone https://github.com/ruvnet/agentic-security.git .

# Create virtual environment
echo "🔨 Creating Python virtual environment..."
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -e .

# Create .env file template
echo "📝 Creating .env template..."
cat > .env << 'EOF'
# API Keys - REPLACE WITH YOUR ACTUAL KEYS
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here

# Optional: Slack notifications
SLACK_WEBHOOK=your_slack_webhook_here

# Agent Configuration
AGENT_VERBOSE=true
AGENT_AUTO_FIX=false
AGENT_AUTO_PR=false
EOF

# Create systemd service
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/agentic-security.service > /dev/null << 'EOF'
[Unit]
Description=Agentic Security Agent
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/agentic-security
Environment="PATH=/opt/agentic-security/venv/bin"
ExecStart=/opt/agentic-security/venv/bin/python -m agentic_security.agent_cli interactive
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Replace $USER in service file
sudo sed -i "s/\$USER/$USER/g" /etc/systemd/system/agentic-security.service

# Create log directory
sudo mkdir -p /var/log/agentic-security
sudo chown $USER:$USER /var/log/agentic-security

# Setup log rotation
sudo tee /etc/logrotate.d/agentic-security > /dev/null << 'EOF'
/var/log/agentic-security/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 $USER $USER
    sharedscripts
}
EOF

sudo sed -i "s/\$USER/$USER/g" /etc/logrotate.d/agentic-security

# Create cron job for scheduled scans
echo "⏰ Setting up cron job for scheduled scans..."
(crontab -l 2>/dev/null; echo "0 2 * * * cd /opt/agentic-security && /opt/agentic-security/venv/bin/agentic-agent run-pipeline --mode autonomous >> /var/log/agentic-security/cron.log 2>&1") | crontab -

# Setup firewall (if needed)
echo "🔒 Configuring firewall..."
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 8080/tcp  # Optional: Web interface
sudo ufw --force enable

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit /opt/agentic-security/.env with your API keys"
echo "2. Authenticate GitHub CLI: gh auth login"
echo "3. Test the agent: cd /opt/agentic-security && source venv/bin/activate && agentic-agent --help"
echo "4. Start the service: sudo systemctl start agentic-security"
echo "5. Enable on boot: sudo systemctl enable agentic-security"
echo ""
echo "📊 Useful commands:"
echo "  - Check status: sudo systemctl status agentic-security"
echo "  - View logs: sudo journalctl -u agentic-security -f"
echo "  - Run manual scan: cd /opt/agentic-security && source venv/bin/activate && agentic-agent autonomous-scan --path /path/to/repo"

# Made with Bob
