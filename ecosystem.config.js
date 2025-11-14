module.exports = {
  apps: [
    {
      name: 'rag-backend',
      script: '.venv/bin/python',
      args: 'backend/app.py',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      time: true,
      restart_delay: 3000,
      max_restarts: 10
    },
    {
      name: 'rag-frontend',
      script: 'serve',
      args: '-s frontend/dist -p 5173',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/frontend-error.log',
      out_file: './logs/frontend-out.log',
      time: true
    }
  ]
};
