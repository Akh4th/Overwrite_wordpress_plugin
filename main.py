import json
import os
import socket
from ftplib import FTP
import requests


"""
Once you've filled 'websites.txt' using Websites_to_host.py and 'CREDS.json' this script is ready
to be executed. The script will login to the FTP of a host and will iterate through the websites on
that host from the list and will replace the existing folder (remote_folder) with the local folder
"""

websites_file = "websites.txt" # list of websites to operate
creds_file = "CREDS.json" # Credentials json file for all the cPanels
local_folder_path = "google-sitemap-generator.4.1.16" # Local folder to upload
remote_folder = "google-sitemap-generator" # Plugin to replace


def file_to_json(FILE):
    print("Importing json file...")
    with open(FILE, "r") as file:
        content = file.read()
        file.close()
    print("JSON File imported successfully.")
    return json.loads(content)


def file_to_list(FILE):
    print("Importing websites list...")
    websites = {}
    with open(FILE, "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                host = line[1:-1]
                websites[host] = []
            elif host:
                websites[host].append(line)
    print(f"Successfully imported {sum(len(sites) for sites in websites.values())} websites")
    return websites


def delete_url_from_file(file_path, url_to_delete):
    with open(file_path, "r") as file:
        urls = file.readlines()
    modified_urls = [url.strip() for url in urls if url.strip() != url_to_delete]
    with open(file_path, "w") as file:
        for url in modified_urls:
            file.write(url + "\n")


def remove_directory_recursively(ftp, path):
    if path not in ftp.nlst(): # Plugin does not exists
        print(f"The plugin {path} does not exists on the site.")
        return
    ftp.cwd(path)
    items = ftp.nlst()
    for item in items:
        if item not in [".", ".."]:
            try:
                ftp.delete(item)
            except Exception:
                remove_directory_recursively(ftp, item)
    try:
        ftp.cwd('..')
        ftp.rmd(path)
    except Exception as e:
        print(f"Error removing directory {path}: {e}")


def upload_directory(ftp, local_path, remote_path):
    if not os.path.exists(local_path):
        print(f"Local directory does not exist: {local_path}")
        return
    if os.path.isdir(local_path):
        try:
            ftp.mkd(remote_path)
        except Exception as e:
            print(f"Could not create remote directory {remote_path}: {e}")

        for item in os.listdir(local_path):
            local_item_path = os.path.join(local_path, item)
            remote_item_path = os.path.join(remote_path, item.replace("\\", "/"))
            upload_directory(ftp, local_item_path, remote_item_path)
    else:
        try:
            with open(local_path, 'rb') as file:
                ftp.storbinary(f'STOR {remote_path}', file)
        except Exception as e:
            print(f"Error uploading file {local_path}: {e}")


def main():
    hosts = file_to_list(websites_file)
    cpanels = file_to_json(creds_file)
    fails, success = [], []
    for host, websites in hosts.items():
        cpanel_data = cpanels.get(host, {})
        with FTP() as ftp:
            try:
                ftp.connect(cpanel_data['host'], int(cpanel_data.get('port', 21)), timeout=15)
                ftp.login(cpanel_data['user'], cpanel_data['pass'])
                print(f"Connected to FTP: {host}")
                for site in websites:
                    site = site.split("//")[-1].split("www.")[-1]
                    try:
                        for SITE in ftp.nlst():
                            if SITE in ('.', '..', '', ' ', None):
                                continue
                            elif site.lower() == SITE.lower() or SITE in site:
                                site = SITE
                                break
                            elif SITE == ftp.nlst()[-1]:
                                site = site.split('.')[0]
                        if len(SITE) == 0:
                            break
                        ftp.cwd('/')
                        ftp.cwd('public_html')
                        ftp.cwd(site)
                        ftp.cwd('wp-content')
                        ftp.cwd('plugins')
                        remove_directory_recursively(ftp, remote_folder)
                        print(f"Plugin deleted successfully on {site}")
                        upload_directory(ftp, local_folder_path, remote_folder)
                        print(f"Updated {site} successfully.")
                        success.append(site)
                        delete_url_from_file(websites_file, site)
                    except Exception as e:
                        print(f"Error updating {site}: {e}")
                        fails.append(site)
                        continue
            except socket.timeout:
                print(f"Request timed out for {host}.\nConnection string : ftp://{cpanel_data['user']}@{cpanel_data['host']}:{cpanel_data.get('port', 21)}")
                fails.extend(websites)
            except Exception as e:
                print(f"FTP connection error for {host}: {e}")
                fails.extend(websites)
        ftp.close()
    print("Update Summary:")
    print("Failed sites:", fails)
    print("Succeeded sites:", success)


if __name__ == "__main__":
    main()
