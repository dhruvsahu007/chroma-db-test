# 🚀 EC2 Deployment Checklist

## ✅ Pre-Deployment (On Local Machine)

- [x] `.gitignore` updated (PEM files excluded)
- [x] `ecosystem.config.js` created
- [x] `deploy.sh` script created
- [x] Frontend environment variables configured
- [x] Git repository initialized
- [ ] **Push to GitHub**

```bash
cd /Users/dhruvsahu/Desktop/Test
git push -u origin main
```

---

## ✅ EC2 Setup (One-Time)

### 1. Connect to EC2
```bash
chmod 400 /path/to/your/chroma-db-test.pem
ssh -i /path/to/your/chroma-db-test.pem ubuntu@13.201.21.240
```

### 2. Configure AWS Credentials
```bash
aws configure
```
Enter:
- AWS Access Key ID: `YOUR_AWS_ACCESS_KEY_ID`
- AWS Secret Access Key: `YOUR_AWS_SECRET_ACCESS_KEY`
- Region: `us-east-1`
- Output: `json`

### 3. Run Automated Deployment Script
```bash
cd ~
git clone https://github.com/dhruvsahu007/chroma-db-test.git
cd chroma-db-test
chmod +x deploy.sh
./deploy.sh
```

**OR Manual Setup:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2 and serve
sudo npm install -g pm2 serve

# Clone repo
cd ~
git clone https://github.com/dhruvsahu007/chroma-db-test.git
cd chroma-db-test

# Setup backend
python3.11 -m venv .venv
source .venv/bin/activate
cd backend
pip install -r requirements.txt
cd ..

# Setup frontend
cd frontend
npm install
npm run build
cd ..

# Create logs directory
mkdir -p logs

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

---

## ✅ Security Group Configuration

### Required Inbound Rules:
| Type | Protocol | Port | Source | Description |
|------|----------|------|--------|-------------|
| SSH | TCP | 22 | Your IP | SSH access |
| Custom TCP | TCP | 8000 | 0.0.0.0/0 | Backend API |
| Custom TCP | TCP | 5173 | 0.0.0.0/0 | Frontend |
| HTTP | TCP | 80 | 0.0.0.0/0 | Nginx (if used) |

### Steps:
1. Go to AWS Console → EC2 → Security Groups
2. Find security group for instance `i-0f0a956e5f8e760ac`
3. Edit Inbound Rules
4. Add the rules above
5. Save

---

## ✅ Verification

### 1. Check PM2 Status
```bash
pm2 status
pm2 logs
```

Expected output:
```
┌─────┬──────────────┬─────────┬─────────┬──────────┐
│ id  │ name         │ status  │ restart │ uptime   │
├─────┼──────────────┼─────────┼─────────┼──────────┤
│ 0   │ rag-backend  │ online  │ 0       │ 5m       │
│ 1   │ rag-frontend │ online  │ 0       │ 5m       │
└─────┴──────────────┴─────────┴─────────┴──────────┘
```

### 2. Test Backend API
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

### 3. Check ChromaDB
```bash
ls -la ~/chroma-db-test/backend/chroma_db/
# Should show ChromaDB files
```

### 4. Access from Browser
- Frontend: http://13.201.21.240:5173
- Backend: http://13.201.21.240:8000/docs

---

## ✅ Post-Deployment Testing

### Test Questions:
1. "What is Zaptoz Technologies?"
2. "What cloud solutions does Zaptoz offer?"
3. "Tell me about Windows on AWS"
4. "What are the leadership principles?"

---

## 🔄 Updating the Application

```bash
# On EC2
cd ~/chroma-db-test
git pull origin main

# Update backend
source .venv/bin/activate
cd backend
pip install -r requirements.txt
cd ..

# Update frontend
cd frontend
npm install
npm run build
cd ..

# Restart
pm2 restart all
```

---

## 🛠️ Troubleshooting

### Backend Issues
```bash
# Check logs
pm2 logs rag-backend --lines 50

# Check if ChromaDB exists
ls -la backend/chroma_db/

# Test manually
cd ~/chroma-db-test
source .venv/bin/activate
cd backend
python app.py
```

### Frontend Issues
```bash
# Check logs
pm2 logs rag-frontend --lines 50

# Verify build
ls -la frontend/dist/

# Check API URL
cat frontend/.env.production
```

### AWS Credentials Issues
```bash
# Test credentials
aws sts get-caller-identity

# Check Bedrock access
aws bedrock list-foundation-models --region us-east-1 | grep -i nova
aws bedrock list-foundation-models --region us-east-1 | grep -i titan
```

### Port Issues
```bash
# Check if ports are listening
sudo netstat -tulpn | grep -E '(8000|5173)'

# Kill process on port
sudo lsof -ti:8000 | xargs kill -9
sudo lsof -ti:5173 | xargs kill -9
```

---

## 📊 Monitoring

### Real-time Monitoring
```bash
pm2 monit
```

### View Logs
```bash
# All logs
pm2 logs

# Specific app
pm2 logs rag-backend
pm2 logs rag-frontend

# Last 100 lines
pm2 logs --lines 100
```

### Resource Usage
```bash
# System resources
htop

# Disk usage
df -h

# Memory usage
free -h
```

---

## 🔐 Security Best Practices

- [ ] Remove AWS credentials from `.env` (use IAM role instead)
- [ ] Restrict Security Group to specific IPs
- [ ] Setup SSL/TLS with Let's Encrypt
- [ ] Enable CloudWatch monitoring
- [ ] Setup automated backups for ChromaDB
- [ ] Regular system updates: `sudo apt update && sudo apt upgrade`
- [ ] Use AWS Systems Manager for secure access

---

## 📦 Backup ChromaDB

```bash
# Create backup
cd ~/chroma-db-test/backend
tar -czf chroma_db_backup_$(date +%Y%m%d).tar.gz chroma_db/

# Copy to S3 (if configured)
aws s3 cp chroma_db_backup_*.tar.gz s3://your-backup-bucket/

# Restore from backup
tar -xzf chroma_db_backup_YYYYMMDD.tar.gz
pm2 restart rag-backend
```

---

## 🎯 Production URLs

- **Frontend**: http://13.201.21.240:5173
- **Backend API**: http://13.201.21.240:8000
- **API Documentation**: http://13.201.21.240:8000/docs
- **Health Check**: http://13.201.21.240:8000/health

---

## ℹ️ Important Notes

- **ChromaDB Location**: `/home/ubuntu/chroma-db-test/backend/chroma_db/`
- **Logs Location**: `/home/ubuntu/chroma-db-test/logs/`
- **PM2 Config**: `/home/ubuntu/chroma-db-test/ecosystem.config.js`
- **Knowledge Base**: Will persist on EBS volume
- **AWS Region**: us-east-1 (required for Bedrock models)

---

## 🎉 Success Criteria

- ✅ Both backend and frontend running via PM2
- ✅ PM2 configured to start on system boot
- ✅ ChromaDB populated with 43 chunks
- ✅ Can query chatbot and get responses
- ✅ Logs accessible via `pm2 logs`
- ✅ Applications auto-restart on failure
