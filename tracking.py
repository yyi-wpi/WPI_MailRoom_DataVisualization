import pandas as pd
import requests

# Read the CSV file into a DataFrame
print("Reading CSV file...")
df = pd.read_csv('packages.csv')
print("CSV file loaded successfully.")

# Define the API token and base URL
api_token = 'shippo_live_59d15a9e675bf94ac1f7487697a6a1e34f29f8d3'
base_url = 'https://api.goshippo.com/tracks'

# Add new columns to the DataFrame
df['Origin City'] = ''
df['Origin State'] = ''
df['Origin Zip'] = ''
df['Origin Country'] = ''
print("Added new columns for origin address.")


# Function to get origin address from Shippo API
def get_origin_address(carrier, tracking_number):
    url = f"{base_url}/{carrier}/{tracking_number}"
    headers = {
        "Authorization": f"ShippoToken {api_token}"
    }
    print(f"Making API request for carrier: {carrier}, tracking number: {tracking_number}")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        address_from = data.get('address_from')
        if address_from:
            print(f"Received address from API: {address_from}")
            return (
                address_from.get('city', ''),
                address_from.get('state', ''),
                address_from.get('zip', ''),
                address_from.get('country', '')
            )
        else:
            print("No 'address_from' found in the response.")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {carrier} {tracking_number}: {e}")
    return '', '', '', ''


# Iterate over the DataFrame rows
print("Processing each row in the DataFrame...")
for index, row in df.iterrows():
    carrier = row['Carrier'].strip().lower()
    tracking_number = row['Tracking #'].strip().rstrip('_')

    # Check if the carrier is USPS, UPS, or FedEx
    if carrier in ['usps', 'ups', 'fedex']:
        print(f"Processing row {index}: Carrier = {carrier}, Tracking Number = {tracking_number}")
        city, state, zip_code, country = get_origin_address(carrier, tracking_number)
        df.at[index, 'Origin City'] = city
        df.at[index, 'Origin State'] = state
        df.at[index, 'Origin Zip'] = zip_code
        df.at[index, 'Origin Country'] = country
    else:
        print(f"Skipping row {index}: Carrier {carrier} is not USPS, UPS, or FedEx.")

# Save the updated DataFrame to a new CSV file
output_file = 'updated_packages.csv'
df.to_csv(output_file, index=False)
print(f"Updated DataFrame saved to {output_file}.")