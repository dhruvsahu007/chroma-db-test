# EC2 Deployment Guide - RAG Chatbot

## EC2 Instance Details
- **Instance ID**: i-0f0a956e5f8e760ac
- **Instance Type**: t3.medium
- **Public IP**: 13.201.21.240
- **Region**: ap-south-1 (Mumbai)
- **GitHub Repo**: https://github.com/dhruvsahu007/chroma-db-test.git

---

## Prerequisites Checklist

- [x] EC2 instance running (Ubuntu/Amazon Linux)
- [ ] PEM key file downloaded (e.g., `chroma-db-test.pem`)
- [ ] Security Group allows ports: 22 (SSH), 8000 (Backend), 5173 or 80 (Frontend)
- [ ] AWS credentials configured on EC2 or IAM role attached
- [ ] GitHub repository created

---

## Step 1: Prepare Local Repository

### 1.1 Initialize Git (if not already done)
```bash
cd /Users/dhruvsahu/Desktop/Test
git init
git add .
git commit -m "Initial commit: RAG chatbot with Bedrock and ChromaDB"
```

### 1.2 Add Remote and Push
```bash
git remote add origin https://github.com/dhruvsahu007/chroma-db-test.git
git branch -M main
git push -u origin main
```

---

## Step 2: Connect to EC2 Instance

### 2.1 Set PEM Key Permissions
```bash
chmod 400 /path/to/chroma-db-test.pem
```

### 2.2 SSH into EC2
```bash
ssh -i /path/to/chroma-db-test.pem ubuntu@13.201.21.240
# OR for Amazon Linux:
# ssh -i /path/to/chroma-db-test.pem ec2-user@13.201.21.240
```

---

## Step 3: Install Required Software on EC2

### 3.1 Update System
```bash
sudo apt update && sudo apt upgrade -y
# For Amazon Linux: sudo yum update -y
```

### 3.2 Install Python 3.11
```bash
sudo apt install -y python3.11 python3.11-venv python3-pip
# For Amazon Linux:
# sudo yum install -y python3.11 python3.11-pip
```

### 3.3 Install Node.js & npm
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installations
node --version
npm --version
```

### 3.4 Install PM2 Globally
```bash
sudo npm install -g pm2
```

### 3.5 Install Git
```bash
sudo apt install -y git
# For Amazon Linux: sudo yum install -y git
```

---

## Step 4: Clone Repository on EC2

```bash
cd ~
git clone https://github.com/dhruvsahu007/chroma-db-test.git
cd chroma-db-test
```

---

## Step 5: Configure AWS Credentials on EC2

### Option 1: AWS CLI Configuration (Recommended)
```bash
aws configure
# Enter:
# AWS Access Key ID: YOUR_AWS_ACCESS_KEY_ID
# AWS Secret Access Key: YOUR_AWS_SECRET_ACCESS_KEY
# Default region: us-east-1
# Default output format: json
```

### Option 2: Create .env file
```bash
cat > .env << EOF
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION=us-east-1
EOF
```

---

## Step 6: Setup Backend

### 6.1 Create Python Virtual Environment
```bash
cd ~/chroma-db-test
python3.11 -m venv .venv
source .venv/bin/activate
```

### 6.2 Install Python Dependencies
```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

### 6.3 Test Backend Manually (Optional)
```bash
python app.py
# Press Ctrl+C after verifying it starts successfully
```

---

## Step 7: Setup Frontend

### 7.1 Install Dependencies
```bash
cd ~/chroma-db-test/frontend
npm install
```

### 7.2 Build Frontend for Production
```bash
npm run build
```

### 7.3 Update API URL for Production
Create a `.env` file in frontend directory:
```bash
cat > .env << EOF
VITE_API_URL=http://13.201.21.240:8000
EOF
```

Then rebuild:
```bash
npm run build
```

---

## Step 8: Create PM2 Ecosystem File

Create `ecosystem.config.js` in the project root:

```bash
cd ~/chroma-db-test
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'rag-backend',
      script: '.venv/bin/python',
      args: 'backend/app.py',
      cwd: '/home/ubuntu/chroma-db-test',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      time: true
    },
    {
      name: 'rag-frontend',
      script: 'serve',
      args: '-s frontend/dist -l 5173',
      cwd: '/home/ubuntu/chroma-db-test',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/frontend-error.log',
      out_file: './logs/frontend-out.log',
      time: true
    }
  ]
};
EOF
```

### 8.1 Install Serve Package
```bash
sudo npm install -g serve
```

### 8.2 Create Logs Directory
```bash
mkdir -p ~/chroma-db-test/logs
```

---

## Step 9: Start Applications with PM2

### 9.1 Start Both Applications
```bash
cd ~/chroma-db-test
pm2 start ecosystem.config.js
```

### 9.2 Check Status
```bash
pm2 status
pm2 logs
```

### 9.3 Save PM2 Configuration
```bash
pm2 save
pm2 startup
# Follow the command it outputs to enable PM2 on system boot
```

---

## Step 10: Configure Security Group

### Add Inbound Rules:
1. **SSH**: Port 22 (already configured)
2. **Backend**: Port 8000, Source: 0.0.0.0/0
3. **Frontend**: Port 5173, Source: 0.0.0.0/0

### AWS Console Steps:
1. Go to EC2 → Instances
2. Select instance `i-0f0a956e5f8e760ac`
3. Security tab → Click Security Group
4. Inbound rules → Edit inbound rules → Add rules

---

## Step 11: Access Your Application

- **Frontend**: http://13.201.21.240:5173
- **Backend API**: http://13.201.21.240:8000
- **API Docs**: http://13.201.21.240:8000/docs
- **Health Check**: http://13.201.21.240:8000/health

---

## Step 12: Setup Nginx Reverse Proxy (Optional - Recommended)

### 12.1 Install Nginx
```bash
sudo apt install -y nginx
```

### 12.2 Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/rag-chatbot
```

Paste this configuration:
```nginx
server {
    listen 80;
    server_name 13.201.21.240;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 12.3 Enable Site and Restart Nginx
```bash
sudo ln -s /etc/nginx/sites-available/rag-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 12.4 Update Security Group
- Remove port 5173 and 8000 from public access
- Keep only port 80 (HTTP) and 22 (SSH) open

---

## Useful PM2 Commands

```bash
# View logs
pm2 logs rag-backend
pm2 logs rag-frontend

# Restart applications
pm2 restart rag-backend
pm2 restart rag-frontend
pm2 restart all

# Stop applications
pm2 stop rag-backend
pm2 stop rag-frontend

# Delete from PM2
pm2 delete rag-backend
pm2 delete rag-frontend

# Monitor in real-time
pm2 monit

# View detailed info
pm2 show rag-backend
```

---

## Troubleshooting

### Backend won't start
```bash
# Check logs
pm2 logs rag-backend --lines 100

# Test manually
cd ~/chroma-db-test
source .venv/bin/activate
cd backend
python app.py
```

### Frontend won't start
```bash
# Check logs
pm2 logs rag-frontend --lines 100

# Test build
cd ~/chroma-db-test/frontend
npm run build
```

### ChromaDB Issues
```bash
# Check if directory exists
ls -la ~/chroma-db-test/backend/chroma_db

# Delete and restart to rebuild
rm -rf ~/chroma-db-test/backend/chroma_db
pm2 restart rag-backend
```

### AWS Credentials Issues
```bash
# Test AWS credentials
aws sts get-caller-identity

# Check Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

---

## Updating the Application

### Pull Latest Changes
```bash
cd ~/chroma-db-test
git pull origin main

# Update backend
source .venv/bin/activate
cd backend
pip install -r requirements.txt

# Update frontend
cd ../frontend
npm install
npm run build

# Restart PM2
pm2 restart all
```

---

## Security Recommendations

1. **Never commit `.env` or `.pem` files** (already in .gitignore)
2. **Use IAM roles** instead of hardcoded AWS credentials on EC2
3. **Enable HTTPS** using Let's Encrypt/Certbot
4. **Restrict Security Group** to specific IPs when possible
5. **Regular updates**: `sudo apt update && sudo apt upgrade`
6. **Setup CloudWatch** for monitoring
7. **Enable AWS Systems Manager** for secure access instead of SSH

---

## Production Checklist

- [ ] Applications running via PM2
- [ ] PM2 configured to start on boot
- [ ] Security Group properly configured
- [ ] AWS credentials working
- [ ] ChromaDB populated with knowledge base
- [ ] Nginx reverse proxy configured (optional)
- [ ] SSL certificate installed (optional)
- [ ] Monitoring and logging setup
- [ ] Backups configured for ChromaDB

---

## Notes

- **ChromaDB Location**: `/home/ubuntu/chroma-db-test/backend/chroma_db/`
- **Logs Location**: `/home/ubuntu/chroma-db-test/logs/`
- **Project Root**: `/home/ubuntu/chroma-db-test/`

The ChromaDB will persist on the EC2 instance's EBS volume. For production, consider:
- Regular EBS snapshots
- S3 backups of ChromaDB
- Using AWS EFS for shared storage if scaling to multiple instances
