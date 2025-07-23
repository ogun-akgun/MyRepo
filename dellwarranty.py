from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import pandas as pd
import click
import requests
import urllib3
import os
from typing import Optional
from urllib3.exceptions import InsecureRequestWarning


def get_dell_warr(tags):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        for tag in tags:
            try:
                url = f"https://www.dell.com/support/home/en-us/product-support/servicetag/{tag['tag']}/warranty"
                print(f"Checking warranty for Service Tag: {tag['tag']}")
                driver.get(url)

                # Wait for page load
                time.sleep(1)

                try:
                    # Method 1: Direct XPath for warranty cards
                    warranty_elements = driver.find_elements(By.XPATH,
                                                             "//*[contains(text(), 'Ended on') or contains(text(), 'Ending on')]")
                    for element in warranty_elements:
                        # print("\nFound warranty element:")
                        text = element.text
                        date_parts = text.split('on ', 1)
                        if len(date_parts) > 1:
                            date_str = date_parts[1].strip()
                            date_obj = pd.to_datetime(date_str)
                            iso_date = date_obj.strftime('%Y-%m-%d')

                        print(f"Warranty date: {iso_date}")
                        return iso_date

                except Exception as e:
                    print(f"Error extracting warranty details: {str(e)}")

                print("*" * 50)
                # time.sleep(2)

            except Exception as e:
                print(f"Error processing service tag {tag['tag']}: {str(e)}")
                continue

    finally:
        driver.quit()

    def get_netbox_serial(device_name: str, netbox_token: str) -> Optional[str]:

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    netbox_url = "https://yow-netbox.wrs.com"

    if not netbox_url or not netbox_token:
        raise ValueError("NETBOX_URL and NETBOX_TOKEN environment variables must be set")

    headers = {
        'Authorization': f'Token {netbox_token}',
        'Accept': 'application/json'
    }

    response = requests.get(
        f"{netbox_url}/api/dcim/devices/?name={device_name}",
        headers=headers,
        verify=False
    )

    if response.status_code != 200:
        raise Exception(f"Failed to query Netbox API: {response.status_code}")

    data = response.json()
    if data['count'] == 0:
        raise ValueError(f"Device {device_name} not found in Netbox")

    return data['results'][0]['serial']


@click.command()
@click.argument('device_name')
@click.option('--netbox-token', required=True, help='Netbox API token')
@click.option('--update', default="NO", help='Update warranty date in Netbox (YES/NO)')
def main(device_name, netbox_token,):
    try:
        serial = get_netbox_serial(device_name, netbox_token)

        warranty_date = get_dell_warr([{'tag': serial}])
        print(f"Warranty date for {device_name} (Serial: {serial}): {warranty_date}")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
