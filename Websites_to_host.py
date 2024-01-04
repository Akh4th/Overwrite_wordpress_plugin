import socket

'''
This script will take the content of 'unsorted_websites.txt' which is a list of URLs
and will remove the 'http://www.' out of it and then will group all the URLs into hosts
into the file called 'websites.txt' so you can work with main.py on that list.
DO NOT FORGET TO UPDATE 'CREDS.json' file accordingly !
'''


def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]


def get_ip(url):
    try:
        return socket.gethostbyname(url)
    except socket.gaierror:
        return None


urls = read_urls_from_file('unsorted_websites.txt')
url_ip_map = {url: get_ip(url.split("//")[-1].split("/")[0]) for url in urls}
host_groups = {}

for url, ip in url_ip_map.items():
    if ip:
        if ip not in host_groups:
            host_groups[ip] = []
        host_groups[ip].append(url)


with open("websites.txt", 'w') as file:
    for ip, urls in host_groups.items():
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except socket.herror:
            hostname = "Unknown Host"
        file.write(f"[{hostname}]\n")
        for url in urls:
            file.write(f"{url}\n")
        file.write("\n")
