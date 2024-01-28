import requests
import csv
import time
from bs4 import BeautifulSoup
from lxml import etree
from tqdm import tqdm

end = 46000
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
}


def check_index():
    with open('index.txt', 'r') as txt_file:
        # Read the entire content of the file
        content = txt_file.read()
        return content if content else 0


start = int(check_index()) + 1


def generate_url():
    for drug_id in range(start, end):
        yield drug_id


def data_object(dom, xpath):
    # Use XPath expression with select_one
    element = dom.xpath(xpath)

    if element:
        # Extract the text content of the found element
        return element[0].text.replace('\r\n', '').strip()
    else:
        print(f'No element found with the specified XPath.')


def fetch_data_from_url(url_id):
    # Replace 'url' with the URL of the product page you want to crawl
    response = requests.get(f'https://irc.fda.gov.ir/NFI/Detail/{url_id}', headers=headers, timeout=100)

    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup with lxml parser
        soup = BeautifulSoup(response.text, 'html.parser')

        dom = etree.HTML(str(soup))
        # Replace 'your_xpath' with the actual XPath expression for the desired element
        result = {
            'id': url_id,
            'general_name': data_object(dom, '/html/body/div[1]/div[5]/div[1]/div[1]/div/div/div[3]/div[1]/div[2]/bdo'),
            'certificate_owner': data_object(dom,
                                             '/html/body/div[1]/div[5]/div[1]/div[1]/div/div/div[3]/div[3]/div[1]/span'),
            'brand_owner': data_object(dom, '/html/body/div[1]/div[5]/div[1]/div[1]/div/div/div[3]/div[3]/div[2]/span'),
            'consumer_price': data_object(dom,
                                          '/html/body/div[1]/div[5]/div[1]/div[1]/div/div/div[3]/div[5]/div[1]/span[1]'),
            'unit_price': data_object(dom,
                                      '/html/body/div[1]/div[5]/div[1]/div[1]/div/div/div[3]/div[5]/div[2]/span[1]'),
            'irc': data_object(dom, '/html/body/div[1]/div[5]/div[1]/div[1]/div/div/div[3]/div[6]/div[2]/span'),
            'gtin': data_object(dom, '/html/body/div[1]/div[5]/div[1]/div[1]/div/div/div[3]/div[6]/div[1]/span'),
            'emergency_licence': data_object(dom,
                                             '/html/body/div[1]/div[5]/div[1]/div[1]/div/div/div[3]/div[7]/div[2]/span'),
            'license_expire_date': data_object(dom,
                                               '/html/body/div[1]/div[5]/div[1]/div[1]/div/div/div[3]/div[4]/div[2]/span'),
            'response_code': response.status_code
        }

        return result
    else:
        result = {
            'id': url_id,
            'general_name': '',
            'certificate_owner': '',
            'brand_owner': '',
            'consumer_price': '',
            'unit_price': '',
            'irc': '',
            'gtin': '',
            'emergency_licence': '',
            'license_expire_date': '',
            'response_code': response.status_code
        }


drug_urls = generate_url()
# Specify the file name
csv_file_name = f'output.csv'
index_file_name = f'index.txt'

fieldnames = [
    'id',
    'general_name',
    'certificate_owner',
    'brand_owner',
    'consumer_price',
    'unit_price',
    'irc',
    'gtin',
    'emergency_licence',
    'license_expire_date',
    'response_code'
]

# Open the CSV file in read mode to check if it has headers
with open(csv_file_name, 'r', newline='') as csv_file:
    # Check if the file is empty (no rows)
    file_is_empty = csv_file.read(1) == ''

with open(csv_file_name, 'a', newline='') as csv_file:
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    if file_is_empty:
        csv_writer.writeheader()

    for url in tqdm(drug_urls, desc="Processing", unit="item", total=end):
        time.sleep(0.1)
        row = fetch_data_from_url(url)
        if isinstance(row, dict):
            csv_writer.writerow(row)
        else:
            pass

        with open(index_file_name, 'w') as index_file:
            # Write the string to the file
            index_file.write(str(url))

print(f'Results have been written to {csv_file_name}.')
