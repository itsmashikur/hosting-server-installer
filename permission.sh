#!/bin/bash

directory="/var/www/html/host.whms.com/"

groups=("admin" "apache" "ftp")
users=("admin" "apache" "ftp")



# Set ACLs for groups
for group in "${groups[@]}"; do
    sudo setfacl -Rm g:"$group":rwx "$directory"
done

# Set ACLs for users
for user in "${users[@]}"; do
    sudo setfacl -Rm u:"$user":rwx "$directory"
done

sudo chcon -Rv --type=httpd_sys_rw_content_t $directory

echo "ACLs set successfully."
