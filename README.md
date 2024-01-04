# Overwrite_wordpress_plugin
Overwrite an existing plugin on a wordpress sites in bulks (Websites most be on 'public_html' folder)

# Grouping URLs by hosts
Open and fill the file 'unsorted_websites.txt' with a URL list and then run 'Websites_to_host.py' in order to group the URLs by hosts.
This script will also remove 'http://www.' from the URL so do not bother removing it manually.

# Filling credentials file
Once you have all the hosts please fill the file 'CREDS.json' accordingly with the same format.

# Final execution 
Once the two files 'websites.txt' and 'CREDS.json' are ready, run main.py to overwrite the plugin.
