import pdfplumber
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def extract_energy_data(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        text = first_page.extract_text()

    pattern = re.compile(r'(\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d\.\d{5})\s+\$(\d{1,3}(?:,\d{3})*\.\d{2})')
    matches = pattern.findall(text)

    if matches:
        kwh, price_per_kwh, total_cost = matches[0]
        kwh = float(kwh.replace(',', ''))
        price_per_kwh = float(price_per_kwh)
        total_cost = float(total_cost.replace(',', ''))

        return {
            "kwh": kwh,
            "price_per_kwh": price_per_kwh,
            "total_cost": total_cost
        }
    else:
        return None

def scrape_rates(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get(url)
    
    # Allow time for the JavaScript to render
    driver.implicitly_wait(10)  # seconds

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rates = []
    print(soup)

    for listing in soup.find_all('div', class_='rate-listing'):
        try:
            provider = listing.find('div', class_='provider-name').text.strip()  # Adjust the class name
            rate_text = listing.find('div', class_='rate').text.strip()  # Adjust the class name
            rate = float(rate_text.replace('¢', '').replace('/kWh', ''))
            rates.append({"provider": provider, "rate": rate / 100})  # Convert cents to dollars
        except AttributeError:
            continue
    
    driver.quit()
    return rates

def find_cheaper_rate(current_rate, available_rates):
    cheaper_rates = [rate for rate in available_rates if rate["rate"] < current_rate]
    if cheaper_rates:
        for rate in cheaper_rates:
            print(f"Provider: {rate['provider']}, Rate: ${rate['rate']:.5f} per kWh")
    else:
        print("No cheaper rates found.")

# Example usage
pdf_path = 'energy_bill.pdf'
data = extract_energy_data(pdf_path)

if data:
    current_rate = data['price_per_kwh']
    print(f"Your current rate: ${current_rate:.5f} per kWh")
    print("Searching for cheaper rates...")

    url = 'https://www.choosetexaspower.org/'
    available_rates = scrape_rates(url)
    
    find_cheaper_rate(current_rate, available_rates)
else:
    print("No data extracted")
