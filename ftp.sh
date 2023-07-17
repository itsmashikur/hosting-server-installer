#!/bin/bash

# Install Telnet if not already installed
if ! command -v telnet &>/dev/null; then
    echo "Telnet is not installed. Installing Telnet..."
    sudo yum install -y telnet
fi

# Retrieve server IP dynamically
SERVER_IP=$(hostname -I | awk '{print $1}')

# Prompt for FTP username
read -p "Enter the FTP username: " FTP_USERNAME

# Prompt for FTP password
read -s -p "Enter the FTP password: " FTP_PASSWORD
echo

# Check if port 21 is open
if ! sudo firewall-cmd --zone=public --query-port=21/tcp; then
    echo "Port 21 is not open. Trying to open the port..."
    sudo firewall-cmd --permanent --zone=public --add-port=21/tcp
    sudo firewall-cmd --reload
fi

# Install Pure-FTPd
sudo yum install -y pure-ftpd

# Configure Pure-FTPd
sudo systemctl enable pure-ftpd.service
sudo systemctl start pure-ftpd.service

# Create a user
sudo pure-pw useradd $FTP_USERNAME -u ftpuser -g ftpgroup -d /var/www/html/

# Set user password
sudo pure-pw passwd $FTP_USERNAME -m

# Create user folder
sudo mkdir -p /var/www/html/$FTP_USERNAME
sudo chown -R ftpuser:ftpgroup /var/www/html/$FTP_USERNAME

# Provide read-write permissions
sudo chmod -R 755 /var/www/html/$FTP_USERNAME

# Update Pure-FTPd database
sudo pure-pw mkdb

# Restart Pure-FTPd
sudo systemctl restart pure-ftpd.service

# Check port 21 connectivity from another device
echo "Checking port 21 connectivity from another device..."
telnet $SERVER_IP 21
