#!/bin/bash
# User data script for EC2 instance setup

yum update -y
yum install -y python3 python3-pip git

# Install AWS CLI
pip3 install awscli

# Create application directory
mkdir -p /opt/${project_name}
cd /opt/${project_name}

# Clone or copy application code (modify as needed)
# git clone <your-repo-url> .

# Install Python dependencies
# pip3 install -r requirements.txt

# Create systemd service (optional)
cat > /etc/systemd/system/${project_name}.service << EOF
[Unit]
Description=IAM Automation Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/${project_name}
ExecStart=/usr/bin/python3 src/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
# systemctl enable ${project_name}
# systemctl start ${project_name}

# Setup cron for scheduled tasks (optional)
# echo "0 2 * * * /usr/bin/python3 /opt/${project_name}/src/main.py audit" | crontab -