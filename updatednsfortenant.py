#Copyright(c) by Ogun Akgun, Windriver
#ogun.akgun@windriver.com
#2025.
#V1.1
# Define parameters in main function (at the bootom of file)
# NETBOX_URL = "https://yow-netbox.wrs.com"
#     NETBOX_TOKEN=""
#     USERNAME = 'corp\\oakgun'  # Replace with your username if different
#     PASSWORD = ''  # Replace with actual password
#     tenant_name_arg = "YOW-WRCP-DC-033"  specify the tenant
# Program will connect to netbox and list all IPv4 addresses and then update men&mice records.
# It will then prepare ipV6 dns updates for forward lookup/ reverse lookup files and sections to modify.
# Just fopy the section and update the files and reload DNS Zones.

import json
import subprocess
import sys
import argparse

import requests


#from Demos.security.get_policy_info import dns_domain_name


def format_ipv6_reverse(ipv6_addr):
    """Format IPv6 address in reverse format with dots"""
    # Pad with zeros if needed
    parts = ipv6_addr.split(':')
    full_addr = ''.join(part.zfill(4) for part in parts)
    return '.'.join(reversed(list(full_addr.lower())))


def get_ipv6_with_dns_for_tenant(tenant_name):
    """
    Lists all ipv6 addresses with DNS names for a given tenant in NetBox.

    Args:
        tenant_name (str): The name of the tenant to search for.
    """
    netbox_url = NETBOX_URL
    netbox_token = NETBOX_TOKEN

    if not netbox_url or not netbox_token:
        print("Error: Please set the NETBOX_URL and NETBOX_TOKEN environment variables.")
        sys.exit(1)

    headers = {
        'Authorization': f'Token {netbox_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json; indent=4'
    }

    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings()

    try:
        # Get Tenant ID
        tenant_response = requests.get(f"{netbox_url}/api/tenancy/tenants/?name={tenant_name}", headers=headers,
                                       verify=False)
        tenant_response.raise_for_status()
        tenants = tenant_response.json().get('results', [])

        if not tenants:
            print(f"Tenant '{tenant_name}' not found.")
            return

        tenant_id = tenants[0]['id']

        # Get IP Addresses for the Tenant
        ip_response = requests.get(f"{netbox_url}/api/ipam/ip-addresses/?limit=500&offset=0&tenant_id={tenant_id}", headers=headers,
                                   verify=False)
        ip_response.raise_for_status()
        ip_addresses = ip_response.json().get('results', [])

        print(f"ipv6 addresses with DNS names for tenant '{tenant_name}':")
        print(f"--------------------------------------------------------")
        print("  Update /etc/bind9/db.yow.lab.wrs.com file in yow-tuxlab, remember to increment serial")
        found = False
        ipv6_network = ""
        results_list = []
        for ip in ip_addresses:
            if ip.get('family', {}).get('value') == 6 and ip.get('dns_name'):
                ip_without_subnet = ip['address'].split('/')[0].upper()
                if ipv6_network != ip_without_subnet.split('::')[0]:
                    print(f"\n")
                    print(f"Add following files to /etc/bind9/db.yow.lab.wrs.com file in yow-tuxlab section \n{ip_without_subnet.split('::')[0]}:")
                    print(f"---------------------------")
                    ipv6_network = ip_without_subnet.split('::')[0]
                dns_without_prefix = ip['dns_name'].split('.')[0]
                print(f"{dns_without_prefix:<24}IN      AAAA    {ip_without_subnet}")
                results_list.append(f"{ip_without_subnet} {ip['dns_name']}.")
                found = True
        print("\n  Reverse DNS Entries")
        found = False
        ipv6_network = ""
        results_list = []
        for ip in ip_addresses:
            if ip.get('family', {}).get('value') == 6 and ip.get('dns_name'):
                ip_without_subnet = ip['address'].split('/')[0].upper()
                if ipv6_network != ip_without_subnet.split('::')[0]:
                    print(f"Add following files to /etc/bind9/\n{ip_without_subnet.split('::')[0]}::ip6.arpa  file in tuxlab and increment serial")
                    print(f"---------------------------")
                    ipv6_network = ip_without_subnet.split('::')[0]
                ipv6_addr = ip_without_subnet.split('::')[1]
                reversed_addr = format_ipv6_reverse(ipv6_addr)
                reversed_addr= reversed_addr+".0.0.0.0.0.0.0.0.0.0.0.0"
                print(f"{reversed_addr}  IN  PTR  {ip['dns_name']}.")
                results_list.append(f"{ip_without_subnet} {ip['dns_name']}.")
                found = True
        entries = []
        success_count = 0
        for line in results_list:
            # Split by whitespace and strip
            parts = line.strip().split()
            if len(parts) == 2:
                ip_address, dns_name = parts
                #update_dns_record(dns_name, ip_address, USERNAME, PASSWORD)
                #entries.append((ip_address.strip(), dns_name.strip()))
                success_count += 1



        #print(f"\nDNS update process completed.")
        print(f"Successfully Listed {success_count} out of {len(results_list)} records.Remember you need to run systemctl reload bind9 in tuxlab to reload the zone files." )
        if not found:
            print("  No ipv6 addresses with DNS names found for this tenant.")


    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def get_ipv4_with_dns_for_tenant(tenant_name):
    """
    Lists all IPv4 addresses with DNS names for a given tenant in NetBox.

    Args:
        tenant_name (str): The name of the tenant to search for.
    """
    netbox_url = NETBOX_URL
    netbox_token = NETBOX_TOKEN

    if not netbox_url or not netbox_token:
        print("Error: Please set the NETBOX_URL and NETBOX_TOKEN environment variables.")
        sys.exit(1)

    headers = {
        'Authorization': f'Token {netbox_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json; indent=4'
    }

    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings()

    try:
        # Get Tenant ID
        tenant_response = requests.get(f"{netbox_url}/api/tenancy/tenants/?name={tenant_name}", headers=headers,
                                       verify=False)
        tenant_response.raise_for_status()
        tenants = tenant_response.json().get('results', [])

        if not tenants:
            print(f"Tenant '{tenant_name}' not found.")
            return

        tenant_id = tenants[0]['id']

        # Get IP Addresses for the Tenant
        ip_response = requests.get(f"{netbox_url}/api/ipam/ip-addresses/?limit=500&offset=0&tenant_id={tenant_id}", headers=headers,
                                   verify=False)
        ip_response.raise_for_status()
        ip_addresses = ip_response.json().get('results', [])

        print(f"IPv4 addresses with DNS names for tenant '{tenant_name}':")
        found = False
        results_list = []
        for ip in ip_addresses:
            if ip.get('family', {}).get('value') == 4 and ip.get('dns_name'):
                ip_without_subnet = ip['address'].split('/')[0]
                print(f"  {ip_without_subnet} {ip['dns_name']}.")
                results_list.append(f"{ip_without_subnet} {ip['dns_name']}.")
                found = True
        entries = []
        success_count = 0

        # Ask for user confirmation
        user_input = input("\nDo you want to update DNS records in M&M? (yes/no): ").lower()
        if user_input == 'yes':
            for line in results_list:
                # Split by whitespace and strip
                parts = line.strip().split()
                if len(parts) == 2:
                    ip_address, dns_name = parts
                    update_dns_record(dns_name, ip_address, USERNAME, PASSWORD)
                    entries.append((ip_address.strip(), dns_name.strip()))
                    success_count += 1

            print(f"\nDNS update process completed.")
            print(f"Successfully updated {success_count} out of {len(results_list)} records.")
        else:
            print("\nDNS update cancelled by user.")
        if not found:
            print("  No IPv4 addresses with DNS names found for this tenant.")


    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def update_dns_record(dns_name: str, ip_address: str, username: str, password: str) -> bool:
    """
    Update a single DNS record using curl command
    """
    # Prepare the JSON payload
    payload = {
        "dnsRecord": {
            "name": dns_name,
            "type": "A",
            "data": ip_address
        }
    }

    # Convert the payload to JSON string
    json_data = json.dumps(payload)

    # Construct the curl command
    curl_command = [
        'curl', '-g', '--request', 'POST', '-k',
        '-u', f'{username}:{password}',
        '-H', 'Content-Type: Application/json',
        '-d', json_data,
        'https://ala-menmice.corp.ad.wrs.com/mmws/api/DNSZones/wrs.com/DNSRecords'
    ]

    try:
        # Execute the curl command
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Successfully updated DNS record: {dns_name} -> {ip_address}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error updating record {dns_name}: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error updating record {dns_name}: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update DNS records for tenant')
    parser.add_argument('--username', required=True, help='Username for authentication')
    parser.add_argument('--password', required=True, help='Password for authentication')
    parser.add_argument('--tenant', required=True, help='Tenant name')
    parser.add_argument('--token', default='cbb5441f039967ed26cdf9c1add1c6c0b1db889c', help='Netbox token')

    args = parser.parse_args()

    NETBOX_URL = "https://yow-netbox.wrs.com"
    NETBOX_TOKEN = args.token
    USERNAME = args.username
    PASSWORD = args.password
    tenant_name_arg = args.tenant

    get_ipv4_with_dns_for_tenant(tenant_name_arg)
    get_ipv6_with_dns_for_tenant(tenant_name_arg)