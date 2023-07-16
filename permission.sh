directory="/var/www/html/host.whms.com"

# Set ownership for the directory
chown -R apache:admin $directory

# Set permissions for the directory and its contents
chmod -R 775 $directory