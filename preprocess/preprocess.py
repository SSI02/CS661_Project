import pandas as pd
import os

# Load the full dataset
df = pd.read_csv("data/GlobalLandTemperaturesByState.csv")

# Get all unique countries (ignoring missing values)
countries = df["Country"].dropna().unique()

# Create the target directory: 'data/Country Temperature'
output_dir = "data/Country Temperature"
os.makedirs(output_dir, exist_ok=False)

# Create a separate CSV for each country inside 'data/Country Temperature'
for country in countries:
    filename = f"{output_dir}/{country.replace(' ', '_')}_Temperature.csv"
    country_df = df[df["Country"] == country]
    country_df.to_csv(filename, index=False)
