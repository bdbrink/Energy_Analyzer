import pdfplumber

# Replace 'energy_bill.pdf' with the path to your PDF file
with pdfplumber.open('energy_bill.pdf') as pdf:
    first_page = pdf.pages[0]
    text = first_page.extract_text()

print(text)
