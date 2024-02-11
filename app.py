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

    # table = soup.select_one("h2:-soup-contains('Accidents in India') + table")
    # table = soup.select_one("body > div > div.c-pagecontent.c-pagecontent-xs > div > div > div > div > div > table")
    table = soup.find('table')

    if table == None:
        print("Table could not be found")
        return

    table_rows = table.select('tbody > tr')

    if len(table_rows) == 0:
        print('Could not find the table rows')
        return

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

# year_start = 1950
# year_end = 2022
# for year in range(year_start, year_end + 1):
#     print(f'Year: {year}')
#     links = get_urls_of_profession_wise_suicide(year)

import os
def make_dir(dir_name: str):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def convert_using_camelot():
    make_dir('output/camelot')
    year = 2022
    import camelot
    links = get_urls_of_profession_wise_suicide(year)
    for link in links:
        pdf_name = link['name']
        pdf_url = link['url']

        name_prefix =  'all-india' if 'All India' in pdf_name else 'state-wise'
        name = f"output/camelot/{year}-{name_prefix}.csv"

        tables = camelot.read_pdf(pdf_url, pages="all", flavor='stream')
        table = tables[0]
        tables.export(name, f='csv')

def convert_using_tabula():
    make_dir('output/tabula')
    year = 2022
    import tabula
    links = get_urls_of_profession_wise_suicide(year)

    for link in links:
        pdf_name = link['name']
        pdf_url = link['url']

        name_prefix =  'all-india' if 'All India' in pdf_name else 'state-wise'

        tabula.convert_into(pdf_url, f"output/tabula/{year}-{name_prefix}.csv", output_format='csv', pages='all')

        # if 'All India' in pdf_name:

convert_using_camelot()
convert_using_tabula()
