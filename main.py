import pdfplumber
import re

# Replace 'energy_bill.pdf' with the path to your PDF file
with pdfplumber.open('energy_bill.pdf') as pdf:
    first_page = pdf.pages[0]
    text = first_page.extract_text()

pattern = re.compile(r'(\d{1,3}(?:,\d{3})*\.\d{2})\s+(\d\.\d{5})\s+\$(\d{1,3}(?:,\d{3})*\.\d{2})')

matches = pattern.findall(text)

if matches:
    kwh, price_per_kwh, total_cost = matches[0]
    kwh = float(kwh.replace(',', ''))
    price_per_kwh = float(price_per_kwh)
    total_cost = float(total_cost.replace(',', ''))

    print(f"kWh: {kwh}")
    print(f"Price per kWh: ${price_per_kwh}")
    print(f"Total Cost: ${total_cost}")
else:
    print("No matches found")