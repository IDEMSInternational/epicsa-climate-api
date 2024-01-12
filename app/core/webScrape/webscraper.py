import requests
from bs4 import BeautifulSoup

mw_seasonal_forecast_list_url = "https://www.metmalawi.gov.mw/docs/district_fcsts/"

def scrape_webpage(url):
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        link_href_dict = {}

        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                for cell in cells:
                    # Find all anchor tags (a) in the cell and append their text to the list
                    links = cell.find_all('a')
                    for link in links:
                        link_text = link.text.split('_')[0]
                        if link_text.lower() not in ["old", "parent directory"]: 
                            link_href_dict[link_text] = url + link.get('href')

        return link_href_dict

    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None


