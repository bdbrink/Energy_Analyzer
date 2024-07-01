import pdfplumber
import re
import subprocess
import json

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

def run_puppeteer_script():
    result = subprocess.run(['node', 'scrape.js'], capture_output=True, text=True)
    return json.loads(result.stdout)

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

    available_rates = run_puppeteer_script()
    
    find_cheaper_rate(current_rate, available_rates)
else:
    print("No data extracted")
