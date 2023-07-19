import os


class VHostManager:
    def __init__(self, vhost_dir='/etc/httpd/conf.d/'):
        self.vhost_dir = vhost_dir

    def list_virtual_hosts(self):
        virtual_hosts = os.listdir(self.vhost_dir)
        return virtual_hosts

    def create_virtual_host(self, domain):
        vhost_contents = self.generate_vhost_contents(domain)
        vhost_file_path = os.path.join(self.vhost_dir, f'{domain}.conf')

        if os.path.exists(vhost_file_path):
            return f'Virtual host {domain} already exists'

        with open(vhost_file_path, 'w') as vhost_file:
            vhost_file.write(vhost_contents)

        os.chmod(vhost_file_path, 0o644)

        return f'Virtual host {domain} created successfully'

    def delete_virtual_host(self, domain):
        vhost_file_path = os.path.join(self.vhost_dir, f'{domain}.conf')

        if os.path.exists(vhost_file_path):
            os.remove(vhost_file_path)
            return f'Virtual host {domain} deleted successfully'
        else:
            return f'Virtual host {domain} does not exist'

    def get_virtual_host(self, domain):
        vhost_file_path = os.path.join(self.vhost_dir, f'{domain}.conf')

        if os.path.exists(vhost_file_path):
            with open(vhost_file_path, 'r') as vhost_file:
                vhost_contents = vhost_file.read()
                return vhost_contents
        else:
            return f'Virtual host {domain} does not exist'

    def update_virtual_host(self, domain, new_contents):
        vhost_file_path = os.path.join(self.vhost_dir, f'{domain}.conf')

        if os.path.exists(vhost_file_path):
            with open(vhost_file_path, 'w') as vhost_file:
                vhost_file.write(new_contents)
            return f'Virtual host {domain} updated successfully'
        else:
            return f'Virtual host {domain} does not exist'

    @staticmethod
    def generate_vhost_contents(domain):
        vhost_template = f'''\
<VirtualHost *:80>
    ServerAdmin webmaster@{domain}
    ServerName {domain}
    ServerAlias www.{domain}
    DocumentRoot /var/www/html/{domain}
    <Directory /var/www/html/{domain}>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog /var/log/httpd/{domain}-error.log
    CustomLog /var/log/httpd/{domain}-access.log combined
</VirtualHost>
'''
        return vhost_template
