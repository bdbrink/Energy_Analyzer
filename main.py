import requests
import pandas as pd
from datetime import datetime
import configparser
import os


class EnergyRateAnalyzer:
    def __init__(self):
        self.api_key = self.get_api_key()
        self.base_url = "https://api.eia.gov/v2/"

    def get_api_key(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        config.read(config_path)
        return config['EIA']['api_key']

    def fetch_state_data(self, state_code):
        endpoint = f"electricity/retail-sales/data/?api_key={self.api_key}"
        params = {
            "frequency": "monthly",
            "data": ["price", "sales", "revenue", "customers"],
            "facets": {
                "sectorId": ["RES"],  # Residential sector
                "stateCode": [state_code]
            },
            "sort": [
                {"column": "period", "direction": "desc"}
            ],
            "offset": 0,
            "length": 12  # Last 12 months of data
        }
        
        response = requests.get(self.base_url + endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data: {response.status_code}")
            return None

    def process_state_data(self, data):
        if not data or 'response' not in data:
            return pd.DataFrame()

        records = []
        for entry in data['response']['data']:
            records.append({
                'date': entry['period'],
                'price': entry['price'],
                'sales': entry['sales'],
                'revenue': entry['revenue'],
                'customers': entry['customers']
            })

        df = pd.DataFrame(records)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        return df

    def analyze_rates(self, state_code):
        data = self.fetch_state_data(state_code)
        if data:
            df = self.process_state_data(data)
            if not df.empty:
                latest_rate = df.iloc[-1]['price']
                avg_rate = df['price'].mean()
                max_rate = df['price'].max()
                min_rate = df['price'].min()

                print(f"Energy Rate Analysis for {state_code}")
                print(f"Latest Rate: ${latest_rate:.4f} per kWh")
                print(f"Average Rate (12 months): ${avg_rate:.4f} per kWh")
                print(f"Maximum Rate (12 months): ${max_rate:.4f} per kWh")
                print(f"Minimum Rate (12 months): ${min_rate:.4f} per kWh")

                return df
            else:
                print("No data available for analysis.")
        return None

    def compare_with_current_rate(self, state_code, current_rate):
        df = self.analyze_rates(state_code)
        if df is not None and not df.empty:
            latest_rate = df.iloc[-1]['price']
            if current_rate > latest_rate:
                savings = (current_rate - latest_rate) * 100  # convert to cents
                print(f"\nYour current rate: ${current_rate:.4f} per kWh")
                print(f"You could save approximately {savings:.2f} cents per kWh based on the latest average rate.")
            else:
                print(f"\nYour current rate (${current_rate:.4f} per kWh) is lower than the latest average rate.")

analyzer = EnergyRateAnalyzer()

# Analyze rates for Texas
texas_data = analyzer.analyze_rates("TX")

# Compare with current rate
current_rate = 0.141  # Your rate of 14.1 cents
analyzer.compare_with_current_rate("TX", current_rate)
