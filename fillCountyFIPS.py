# pip install pandas addfips

import pandas as pd
import addfips

# Initialize addfips
af = addfips.AddFIPS()

# Input and output CSV file names
input_file = "Cleaned_Package_Data_County.csv"  # Replace with your actual file name
output_file = "Cleaned_Package_Data_County_FIPS.csv"

# Read CSV into a DataFrame
df = pd.read_csv(input_file)

# Function to get FIPS code
def get_fips(county, state):
    if pd.notna(state) and pd.notna(county):
        return af.get_county_fips(county.strip(), state=state.strip()) or "Unknown"
    return ""

# Apply function to each row
df["County FIPS"] = df.apply(lambda row: get_fips(row["Origin County"], row["Origin State"]), axis=1)

# Save the updated DataFrame to a new CSV file
df.to_csv(output_file, index=False)

print(f"Updated CSV with County FIPS saved as {output_file}")