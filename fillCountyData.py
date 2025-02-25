# pip install pandas geopy

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Dictionary to cache city-state-county lookups
# Should greatly speed up the process if you have many rows with the same city-state
county_cache = {}

# Function to get the county using city and state
def get_county(city, state):
    global county_cache
    key = (city, state)

    # Check if the county is already cached
    if key in county_cache:
        return county_cache[key]

    geolocator = Nominatim(user_agent="geo_lookup")
    try:
        location = geolocator.geocode(f"{city}, {state}, USA", timeout=10)
        if location and "county" in location.raw["display_name"].lower():
            parts = location.raw["display_name"].split(",")
            for part in parts:
                if "County" in part:
                    county_name = part.replace("County", "").strip()  # Remove "County"
                    county_cache[key] = county_name  # Store in cache
                    return county_name  # Return cleaned county name
        county_cache[key] = "Not found"  # Cache result even if not found
        return "Not found"
    except GeocoderTimedOut:
        return None  # Return None so we can retry later

# Load the CSV file
file_path = "Cleaned_Package_Data.csv"  # File checked for missing data, use written file to continue from last time
export_path = "Cleaned_Package_Data_County.csv"  # File written to, can be same as origin file but I like preserving input data
df = pd.read_csv(file_path)

# Get total row count for tracking progress
total_rows = len(df)

# Process each row
for index, row in df.iterrows():
    if pd.isna(row["Origin County"]) and pd.notna(row["Origin City"]) and pd.notna(row["Origin State"]):
        county = get_county(row["Origin City"], row["Origin State"])

        # Only update if we found a valid county
        if county and county != "Not found":
            df.at[index, "Origin County"] = county

            # Save progress after each update
            df.to_csv(export_path, index=False)

            # Print progress with row count
            print(f"Saved County: {county} for {row['Origin City']}, {row['Origin State']} (Row {index+1} of {total_rows})")

print("Missing counties have been filled and saved.")