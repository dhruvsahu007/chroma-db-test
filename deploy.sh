#!/bin/bash

# EC2 Deployment Script
# Run this script on your EC2 instance after cloning the repository

set -e  # Exit on any error

echo "========================================="
echo "RAG Chatbot Deployment Script"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run this script as root${NC}"
    exit 1
fi

PROJECT_DIR="$HOME/chroma-db-test"

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    OS=$(uname -s)
fi

echo -e "${YELLOW}Step 1: Installing system dependencies...${NC}"
if [ "$OS" = "amzn" ] || [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
    # Amazon Linux / CentOS / RHEL
    sudo yum update -y
    sudo yum install -y python3.11 python3.11-pip git curl tar gzip
else
    # Ubuntu / Debian
    sudo apt update
    sudo apt install -y python3.11 python3.11-venv python3-pip git curl
fi

echo -e "${YELLOW}Step 2: Installing Node.js and npm...${NC}"
if ! command -v node &> /dev/null; then
    if [ "$OS" = "amzn" ] || [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
        # Amazon Linux / CentOS / RHEL
        curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
        sudo yum install -y nodejs
    else
        # Ubuntu / Debian
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt install -y nodejs
    fi
fi

echo -e "${YELLOW}Step 3: Installing PM2...${NC}"
sudo npm install -g pm2 serve

echo -e "${YELLOW}Step 4: Cloning repository (if not exists)...${NC}"
if [ ! -d "$PROJECT_DIR" ]; then
    cd ~
    git clone https://github.com/dhruvsahu007/chroma-db-test.git
else
    echo "Repository already exists, pulling latest changes..."
    cd "$PROJECT_DIR"
    git pull origin main
fi

cd "$PROJECT_DIR"

echo -e "${YELLOW}Step 5: Setting up Python virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    python3.11 -m venv .venv
fi

source .venv/bin/activate
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo -e "${YELLOW}Step 6: Setting up frontend...${NC}"
cd frontend
npm install
npm run build
cd ..

echo -e "${YELLOW}Step 7: Creating logs directory...${NC}"
mkdir -p logs

echo -e "${YELLOW}Step 8: Checking AWS credentials...${NC}"
if aws sts get-caller-identity &> /dev/null; then
    echo -e "${GREEN}AWS credentials are configured!${NC}"
else
    echo -e "${RED}AWS credentials are NOT configured!${NC}"
    echo -e "${YELLOW}Please run: aws configure${NC}"
    echo "Press any key to continue or Ctrl+C to exit..."
    read -n 1
fi

echo -e "${YELLOW}Step 9: Starting applications with PM2...${NC}"
pm2 delete all 2>/dev/null || true
pm2 start ecosystem.config.js
pm2 save

echo -e "${YELLOW}Step 10: Setting up PM2 to start on boot...${NC}"
pm2 startup | grep sudo | bash || true

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "Backend: ${GREEN}http://$(curl -s ifconfig.me):8000${NC}"
echo -e "Frontend: ${GREEN}http://$(curl -s ifconfig.me):5173${NC}"
echo ""
echo "View logs with: pm2 logs"
echo "Check status with: pm2 status"
echo ""
echo -e "${YELLOW}Don't forget to configure your Security Group to allow ports 5173 and 8000!${NC}"
