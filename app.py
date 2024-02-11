import requests
from bs4 import BeautifulSoup
from typing import List, Dict

def get_url(year: int) -> str:
    return f'https://ncrb.gov.in/accidental-deaths-suicides-in-india-table-content.html?year={year}&category=Suicides+in+India'

def parse_html(text: str) -> BeautifulSoup:
    return BeautifulSoup(text, 'html.parser')

def get_urls_of_profession_wise_suicide(year: int) -> List[str]:
    url = get_url(year)
    response = requests.get(url)

    # print(response.text)
    soup: BeautifulSoup = parse_html(response.text)
    table = soup.find('table')

    if table == None:
        print("Table could not be found")
        return []

    table_rows = table.select('tbody > tr')

    if len(table_rows) == 0:
        print('Could not find the table rows')

    urls_to_return: List[Dict[str, str]] = []

    for table_row in table_rows:
        pdf_cell = table_row.select('td')[1]

        pdf_file_name = pdf_cell.text
        pdf_file_url = pdf_cell.a['href']

        if 'Profession' in pdf_file_name:
            print(f'{pdf_file_name}: {pdf_file_url}')
            urls_to_return.append({
                'name': pdf_file_name,
                'url': pdf_file_url
            })

    return urls_to_return

import os
def make_dir(dir_name: str):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def convert_using_camelot(pdf_path: str, year: int, output_suffix: str):
    import camelot

    folder_path = f'output/camelot/{year}'
    make_dir(folder_path)
    tables = camelot.read_pdf(pdf_path, pages="all", flavor='stream')
    tables.export(f"{folder_path}/{output_suffix}", f='csv')

def convert_using_tabula(pdf_path: str, year: int, output_suffix: str):
    import tabula

    folder_path = f'output/tabula/{year}'
    make_dir(folder_path)
    tabula.convert_into(pdf_path, f"{folder_path}/{output_suffix}", output_format='csv', pages='all')

import urllib.request
def download_file(url: str, file_name):
    urllib.request.urlretrieve(url.replace(' ', '%20'), file_name)

year_start = 1950
year_end = 2022
for year in range(year_start, year_end + 1):
    links = get_urls_of_profession_wise_suicide(year)

    for link in links:
        pdf_name = link['name']
        pdf_url = link['url']

        name_suffix =  'all-india' if 'All India' in pdf_name else 'state-wise'
        make_dir(f'tmp/{year}')
        downloaded_pdf_path = f"tmp/{year}/{name_suffix}.pdf"
        output_csv_suffix = f"{name_suffix}.csv"

        download_file(pdf_url, downloaded_pdf_path)

        convert_using_tabula(downloaded_pdf_path, year, output_csv_suffix)
        convert_using_camelot(downloaded_pdf_path, year, output_csv_suffix)
