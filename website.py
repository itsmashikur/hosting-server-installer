from flask import Flask, request, jsonify
from werkzeug.exceptions import NotFound
from flask_cors import CORS
from vhost import VHostManager
import sqlite3
import os
from CloudFlare import CloudFlare

app = Flask(__name__)
CORS(app)


# Create an instance of VHostManager
vhost_manager = VHostManager(vhost_dir='/etc/httpd/conf.d/')

# Cloudflare API credentials
CF_EMAIL = "itsmashikur@gmail.com"
CF_API_KEY = "81e987302c85ca7bc2bbf92de59f3dba49ff0"
CF_ZONE_ID = "0c590f54b95381698c205279bf68fcb2"
IP_ADDRESS = "34.126.145.116"

# Function to add an A record to Cloudflare
def add_cloudflare_a_record(domain, ip_address):
    cf = CloudFlare(email=CF_EMAIL, token=CF_API_KEY)
    params = {
        "name": domain,
        "type": "A",
        "content": ip_address,
        "proxied": True
    }
    zone = cf.zones.get(CF_ZONE_ID)
    record = cf.zones.dns_records.post(zone["id"], data=params)
    return record

# SQLite database initialization
DATABASE_NAME = "web.db"

def initialize_database():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    # Create the table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS websites
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, domain TEXT, directory TEXT)''')
    conn.commit()
    conn.close()

# Function to add website data to the database
def add_website_to_database(domain, directory):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    c.execute("INSERT INTO websites (domain, directory) VALUES (?, ?)", (domain, directory))
    conn.commit()
    conn.close()

# Function to update website data in the database
def update_website_in_database(domain, new_directory):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    c.execute("UPDATE websites SET directory = ? WHERE domain = ?", (new_directory, domain))
    conn.commit()
    conn.close()

# Function to delete website data from the database
def delete_website_from_database(domain):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    c.execute("DELETE FROM websites WHERE domain = ?", (domain,))
    conn.commit()
    conn.close()

# Initialize the database
initialize_database()

# Custom error handler for returning JSON responses
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, NotFound):
        response = jsonify({
            'message': 'The requested resource was not found.',
            'status_code': 404
        })
        response.status_code = 404
    elif isinstance(e, sqlite3.Error):
        response = jsonify({
            'message': 'A database error occurred.',
            'status_code': 500
        })
        response.status_code = 500
    else:
        response = jsonify({
            'message': 'An internal server error occurred.',
            'status_code': 500,
            'error': str(e)
        })
        response.status_code = 500

    return response

# Endpoint to create a virtual host and directory and add Cloudflare A record
@app.route('/website/create', methods=['POST'])
def create_website():
    data = request.json
    domain = data.get('domain')

    directory = data.get('directory')

    

    # Create virtual host
    vhost_manager = VHostManager(vhost_dir='/etc/httpd/conf.d/')
    vhost_message = vhost_manager.create_virtual_host(domain)

    
    # Create directory
    website_directory = f'/var/www/html/{domain}'
    os.makedirs(website_directory)

    # Create index.php file
    index_php_path = os.path.join(website_directory, 'index.php')
    with open(index_php_path, 'w') as index_php_file:
        index_php_content = f"<?php echo '{domain} is ready'; ?>"
        index_php_file.write(index_php_content)


    # Add Cloudflare A record
    ip_address = IP_ADDRESS
    cf_record = add_cloudflare_a_record(domain, ip_address)

    # Save website data to the database
    add_website_to_database(domain, directory)

    return jsonify({
        'message': f'Website {domain} created successfully',
        'vhost_message': vhost_message,
        'cloudflare_record': cf_record
    })

# Endpoint to edit website data and update Cloudflare A record
@app.route('/website/edit', methods=['POST'])
def edit_website():
    data = request.json
    domain = data.get('domain')
    new_directory = data.get('new_directory')

    # Update virtual host directory
    vhost_manager = VHostManager(vhost_dir='/etc/httpd/conf.d/')
    vhost_message = vhost_manager.update_virtual_host(domain, new_directory)

    # Update Cloudflare A record
    ip_address = IP_ADDRESS
    cf_record = add_cloudflare_a_record(domain, ip_address)

    # Update website data in the database
    update_website_in_database(domain, new_directory)

    return jsonify({
        'message': f'Website {domain} updated successfully',
        'vhost_message': vhost_message,
        'cloudflare_record': cf_record
    })

# Endpoint to delete a website and remove Cloudflare A record
@app.route('/website/delete', methods=['POST'])
def delete_website():
    domain = request.json.get('domain')

    # Delete virtual host and directory
    vhost_manager = VHostManager(vhost_dir='/etc/httpd/conf.d/')
    vhost_message = vhost_manager.delete_virtual_host(domain)
    directory_path = f'/var/www/html/{domain}'
    if os.path.exists(directory_path):
        os.rmdir(directory_path)

    # Delete Cloudflare A record
    cf_record = delete_cloudflare_a_record(domain)

    # Delete website data from the database
    delete_website_from_database(domain)

    return jsonify({
        'message': f'Website {domain} deleted successfully',
        'vhost_message': vhost_message,
        'cloudflare_record_deleted': cf_record
    })

# Endpoint to view all website data as JSON
@app.route('/website/list', methods=['GET'])
def list_websites():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM websites")
    rows = c.fetchall()

    websites_list = []
    for row in rows:
        websites_list.append({
            'id': row['id'],
            'domain': row['domain'],
            'directory': row['directory']
        })

    conn.close()

    return jsonify({
        'message': 'List of all websites',
        'websites': websites_list
    })

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=3306)
