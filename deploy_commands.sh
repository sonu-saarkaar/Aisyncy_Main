#!/bin/bash
cd /tmp
aws s3 cp s3://aisyncy-recharge-assets/deploy_package.zip .
unzip -o deploy_package.zip

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and pip if not already installed
sudo apt-get install -y python3 python3-pip python3-venv

# Create and activate virtual environment
python3 -m venv /var/www/aisyncy-recharge/venv
source /var/www/aisyncy-recharge/venv/bin/activate

# Install MongoDB if not already installed
if ! command -v mongod &> /dev/null; then
    wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
    echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
    sudo apt-get update
    sudo apt-get install -y mongodb-org
    sudo systemctl start mongod
    sudo systemctl enable mongod
fi

# Install Node.js and PM2 if not already installed
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
    sudo npm install -g pm2
fi

# Create application directory
sudo mkdir -p /var/www/aisyncy-recharge
cd /var/www/aisyncy-recharge

# Copy deployment files
sudo cp -r /tmp/deploy_package/* .

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cat > .env << EOL
MONGO_URI=mongodb://localhost:27017/aisyncy_recharge
FLASK_ENV=production
FLASK_APP=app.py
EOL

# Set proper permissions
sudo chown -R ubuntu:ubuntu /var/www/aisyncy-recharge
sudo chmod -R 755 /var/www/aisyncy-recharge

# Start the application with PM2
pm2 stop aisyncy-recharge || true
pm2 delete aisyncy-recharge || true
pm2 start app.py --name aisyncy-recharge --interpreter /var/www/aisyncy-recharge/venv/bin/python3
pm2 save

# Set up Nginx if not already installed
if ! command -v nginx &> /dev/null; then
    sudo apt-get install -y nginx
    sudo tee /etc/nginx/sites-available/aisyncy-recharge << EOL
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \System.Management.Automation.Internal.Host.InternalHost;
        proxy_cache_bypass \;
        proxy_set_header X-Real-IP \;
        proxy_set_header X-Forwarded-For \;
    }

    location /static {
        alias /var/www/aisyncy-recharge/static;
    }
}
EOL
    sudo ln -sf /etc/nginx/sites-available/aisyncy-recharge /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t
    sudo systemctl restart nginx
fi
