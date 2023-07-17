directory="/var/www/html/host.whms.com"

# Set ownership for the directory
chown -R apache:admin $directory

# Set permissions for the directory and its contents
chmod -R 775 $directory



# Set permissions for Pure-FTPd
sudo chown -R ftpuser:ftpuser /var/www/html/host.whms.com/
sudo chmod -R 755 /var/www/html/host.whms.com/

# Set permissions for Apache
sudo chown -R apache:apache /var/www/html/host.whms.com/
sudo chmod -R 755 /var/www/html/host.whms.com/

# Set permissions for the admin user
sudo chown -R admin:admin /var/www/html/host.whms.com/
sudo chmod -R 755 /var/www/html/host.whms.com/



#FOR PHP PERMISSION

#!/bin/bash

# Step 1: Verify ownership and permissions
ls -l /var/www/html/host.whms.com/

# Step 2: Grant write permissions to the directory
sudo chmod -R 755 /var/www/html/host.whms.com/

# Step 3: Adjust ownership
sudo chown -R apache:apache /var/www/html/host.whms.com/

# Step 4: Check SELinux context
ls -Z /var/www/html/host.whms.com/

# Step 5: Change SELinux context
sudo chcon -Rv --type=httpd_sys_rw_content_t /var/www/html/host.whms.com/

# Step 6: Restart web server
sudo systemctl restart httpd

echo "Permission fix completed."
