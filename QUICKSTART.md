# 🚀 Quick Start: Deploy to EC2

## Step 1: SSH into EC2
```bash
chmod 400 /path/to/your-key.pem
ssh -i /path/to/your-key.pem ubuntu@13.201.21.240
```

## Step 2: One-Command Deployment
```bash
cd ~ && \
git clone https://github.com/dhruvsahu007/chroma-db-test.git && \
cd chroma-db-test && \
chmod +x deploy.sh && \
./deploy.sh
```

## Step 3: Configure AWS Credentials (when prompted)
```bash
aws configure
```
- Access Key ID: [Your AWS Access Key]
- Secret Access Key: [Your AWS Secret Key]  
- Region: `us-east-1`
- Output: `json`

## Step 4: Configure Security Group
Add these inbound rules in AWS Console:
- Port 22 (SSH) - Your IP
- Port 8000 (Backend) - 0.0.0.0/0
- Port 5173 (Frontend) - 0.0.0.0/0

## Step 5: Access Your App
- Frontend: http://13.201.21.240:5173
- Backend: http://13.201.21.240:8000/docs

## Verify Deployment
```bash
pm2 status
pm2 logs
```

That's it! 🎉

---

## Common Commands

```bash
# View logs
pm2 logs

# Restart apps
pm2 restart all

# Stop apps
pm2 stop all

# Update app after code changes
cd ~/chroma-db-test
git pull
pm2 restart all
```

## Need Help?
Check `DEPLOYMENT.md` for detailed instructions.
