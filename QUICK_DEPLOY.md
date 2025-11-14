# Quick Deploy Commands

## On Your Local Machine

```bash
# 1. Push to GitHub
cd /Users/dhruvsahu/Desktop/Test
git add .
git commit -m "Ready for EC2 deployment"
git push origin main
```

## On EC2 Instance

```bash
# 2. SSH into EC2
ssh -i /path/to/chroma-db-test.pem ubuntu@13.201.21.240

# 3. Install dependencies (one-time setup)
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip git

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2
sudo npm install -g pm2 serve

# 4. Clone repository
cd ~
git clone https://github.com/dhruvsahu007/chroma-db-test.git
cd chroma-db-test

# 5. Configure AWS
aws configure
# Enter your AWS credentials

# 6. Setup Backend
python3.11 -m venv .venv
source .venv/bin/activate
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# 7. Setup Frontend
cd frontend
npm install
npm run build
cd ..

# 8. Create logs directory
mkdir -p logs

# 9. Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup

# 10. Check status
pm2 status
pm2 logs
```

## Access Your App

- Frontend: http://13.201.21.240:5173
- Backend: http://13.201.21.240:8000/docs

## Update Security Group

Add inbound rules for ports 5173 and 8000 (source: 0.0.0.0/0)
