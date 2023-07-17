

#!/bin/bash

# Yum Utils
sudo yum install yum-utils -y

# Install Apache
yum install -y httpd

# Start Apache service
systemctl start httpd

# Enable Apache to start on boot
systemctl enable httpd

# Install PHP 8.2 and required extensions
yum install -y epel-release
rpm -Uvh http://rpms.remirepo.net/enterprise/remi-release-7.rpm

# Disable PHP 5.4
sudo yum-config-manager --disable remi-php54

# Enable PHP 8.2
sudo yum-config-manager --enable remi-php82

sudo yum install php php-cli php-common php-mysqlnd php-pdo php-gd php-mbstring php-xml -y

# Configure main domain virtual host (whms.live)
cat > /etc/httpd/conf.d/whms.live.conf <<EOF
<VirtualHost *:80>
    ServerAdmin webmaster@whms.live
    ServerName whms.live
    ServerAlias www.whms.live
    DocumentRoot /var/www/html/whms.live
    <Directory /var/www/html/whms.live>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog /var/log/httpd/whms.live-error.log
    CustomLog /var/log/httpd/whms.live-access.log combined
</VirtualHost>
EOF

# Configure subdomain virtual host (host.whms.com)
cat > /etc/httpd/conf.d/host.whms.com.conf <<EOF
<VirtualHost *:80>
    ServerAdmin webmaster@whms.live
    ServerName host.whms.com
    DocumentRoot /var/www/html/host.whms.com
    <Directory /var/www/html/host.whms.com>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog /var/log/httpd/host.whms.com-error.log
    CustomLog /var/log/httpd/host.whms.com-access.log combined
</VirtualHost>
EOF

# Create directories for the domains
mkdir -p /var/www/html/whms.live
mkdir -p /var/www/html/host.whms.com

# Create index.php files with PHP info for both domains
cat > /var/www/html/whms.live/index.php <<EOF
<?php
echo "whms.live";
phpinfo();
?>
EOF

cat > /var/www/html/host.whms.com/index.php <<EOF
<?php
echo "host.whms.com";
phpinfo();
?>
EOF

# Set ownership and permissions
chown -R apache:apache /var/www/html/whms.live
chown -R apache:apache /var/www/html/host.whms.com
chmod -R 755 /var/www/html/whms.live
chmod -R 755 /var/www/html/host.whms.com

# Restart Apache service
systemctl restart httpd
