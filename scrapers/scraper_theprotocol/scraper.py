import argparse
import json
import time
import requests

from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
service = Service('C:/WebDrivers/bin/chromedriver.exe')  # Update with your ChromeDriver path
driver = webdriver.Chrome(service=service, options=chrome_options)

main_url = "https://theprotocol.it/praca"


def parse_args():
    parser = argparse.ArgumentParser(description='Scrape job offers from TheProtocol.it')
    parser.add_argument('-num_offers', '-n', required=True, type=int, help='Number of job offers to scrape')
    parser.add_argument('-output' '-o', required=True, type=Path, help='Path to the output json file')
    return parser.parse_args()

def get_offers_urls(n_offers):
    # Set up Selenium with Chrome
  
    
    urls = set()
    page_number = 1
    
    while len(urls) < n_offers:
    #   driver.get(f"{main_url}?page={page_number}")
        driver.get(f"{main_url}?pageNumber={page_number}")
        time.sleep(2)  # Wait for the page to load
        
        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find all <a> elements with the class 'a4pzt2q'
        a_tags = soup.find_all('a', class_='a4pzt2q')
        print(f"Page {page_number}: {len(a_tags)} offers found")
        
        for a_tag in a_tags:
            if 'href' in a_tag.attrs:
                urls.add(a_tag['href'])
                if len(urls) >= n_offers:
                    break
        
        page_number += 1
    
    driver.quit()
    
    return list(urls)[:n_offers]

def extract_job_data(url):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
    else:
        print(f"Request failed with status: {response.status_code}")
    
    job_data = {}
    
    # Extract position name
    position_name = soup.find('h1', class_='r4179ok bldcnq5 ihmj1ec t1yrx4v1')
    job_data['offer_title'] = position_name.text if position_name else None
    
    # Extract company name
    company_name = soup.find('a', class_='c1vxjvoe')
    job_data['company'] = company_name.text if company_name else None
    
    # Extract work type, experience level, and location
    divs = soup.find_all('div', class_='r4179ok bldcnq5 ihmj1ec')
    job_data['contract'] = divs[0].text if len(divs) > 0 else None
    job_data['experience'] = divs[1].text if len(divs) > 1 else None
    if(soup.find('div', {'data-test': 'text-workplaceAddress'})):
        job_data['location'] = soup.find('div', {'data-test': 'text-workplaceAddress'}).text
    else:
        job_data['location'] = None
    
    # Extract technologies list
    technologies = soup.find_all('span', class_='l1sjc53z')
    job_data['expected_technologies'] = [tech.text for tech in technologies]
    #remove     "Job & technologies",       "How we work",         "Benefits & career opp.",     "About us"
    job_data['expected_technologies'] = job_data['expected_technologies'][4:]
    
    # Extract about section
    about_section = soup.find('div', {'data-test': 'section-about-project'})
    if about_section:
        about_divs = about_section.find_all('div', class_='r4179ok bldcnq5 ihmj1ec p1yi18ty')
        job_data['about'] = ' '.join([div.text for div in about_divs])
    
    # Extract duties
    responsibilities_section = soup.find('div', {'data-test': 'section-responsibilities'})
    if responsibilities_section:
        duties_divs = responsibilities_section.find_all('div', class_='r4179ok bldcnq5 ihmj1ec')
        duties_divs+=responsibilities_section.find_all('li', class_='lxul5ps')
        job_data['duties'] = [div.text for div in duties_divs]
    else:
        job_data['duties'] = []
    
    # Extract requirements
    requirements_section = soup.find('div', {'data-test': 'section-requirements'})
    if requirements_section:
        requirements_divs = requirements_section.find_all('div', class_='r4179ok bldcnq5 ihmj1ec')
        requirements_divs+=requirements_section.find_all('li', class_='lxul5ps')
        job_data['requirements'] = [div.text for div in requirements_divs]
    else:
        job_data['requirements'] = []
    
    return job_data

def scrape(n_offers=500):
    n_offers = 500
    urls = get_offers_urls(n_offers)
    job_data_list = []
    
    for relative_url in urls:
        full_url = f"https://theprotocol.it{relative_url}"
        print(f"Extracting data from {full_url}")
        job_data = extract_job_data(full_url)
        time.sleep(1)  # Be polite to the server
        job_data_list.append(job_data)

    return job_data_list
    
def save_to_json(job_data_list, output_path):
    # Save the data to a JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(job_data_list, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    args = parse_args()
    offers = scrape(args.num_offers)
    save_to_json(offers, args.output)
    print(f"Scraped {len(offers)} job offers and saved to {args.output}")