from flask import Flask, request, jsonify
from werkzeug.exceptions import NotFound
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Custom error handler for returning JSON responses
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, NotFound):
        response = jsonify({
            'message': 'The requested resource was not found.',
            'status_code': 404
        })
        response.status_code = 404
    else:
        response = jsonify({
            'message': 'An internal server error occurred.',
            'status_code': 500
        })
        response.status_code = 500

    return response


# Endpoint to list virtual host files
@app.route('/vhost/all', methods=['GET'])
def list_virtual_hosts():
    virtual_hosts = os.listdir('/etc/httpd/conf.d/')
    return jsonify(virtual_hosts)


# Endpoint to create a virtual host
@app.route('/vhost/create', methods=['POST'])
def create_virtual_host():
    domain = request.json.get('domain')
    vhost_contents = generate_vhost_contents(domain)
    vhost_file_path = f'/etc/httpd/conf.d/{domain}.conf'

    if os.path.exists(vhost_file_path):
        return jsonify({'message': f'Virtual host {domain} already exists'})
        
    with open(vhost_file_path, 'w') as vhost_file:
        vhost_file.write(vhost_contents)

    os.chmod(vhost_file_path, 0o644)

    return jsonify({'message': f'Virtual host {domain} created successfully'})


# Endpoint to delete a virtual host
@app.route('/vhost/delete', methods=['POST'])
def delete_virtual_host():
    domain = request.json.get('domain')
    vhost_file_path = f'/etc/httpd/conf.d/{domain}.conf'

    if os.path.exists(vhost_file_path):
        os.remove(vhost_file_path)
        return jsonify({'message': f'Virtual host {domain} deleted successfully'})
    else:
        return jsonify({'message': f'Virtual host {domain} does not exist'})


# Endpoint to get the contents of a virtual host
@app.route('/vhost/get/<domain>', methods=['GET'])
def get_virtual_host(domain):
    vhost_file_path = f'/etc/httpd/conf.d/{domain}.conf'

    if os.path.exists(vhost_file_path):
        with open(vhost_file_path, 'r') as vhost_file:
            vhost_contents = vhost_file.read()
            return jsonify({'contents': vhost_contents})
    else:
        return jsonify({'message': f'Virtual host {domain} does not exist'})


# Endpoint to update a virtual host
@app.route('/vhost/update', methods=['POST'])
def update_virtual_host():
    domain = request.json.get('domain')
    new_contents = request.json.get('contents')
    vhost_file_path = f'/etc/httpd/conf.d/{domain}.conf'

    if os.path.exists(vhost_file_path):
        with open(vhost_file_path, 'w') as vhost_file:
            vhost_file.write(new_contents)
        return jsonify({'message': f'Virtual host {domain} updated successfully'})
    else:
        return jsonify({'message': f'Virtual host {domain} does not exist'})


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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
