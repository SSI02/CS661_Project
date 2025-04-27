# import os
# import json
# import pandas as pd

# # 1. Load your temperature CSV
# temps_df = pd.read_csv("E:/2024-2025 - II Courses/CS661 - Big Data Visual Analytics/Group_Project/Final Project/Final Project/data/GlobalLandTemperaturesByState.csv")

# # 2. Build a lookup list by walking your GeoJSONs
# lookup = []
# for fname in os.listdir("E:/2024-2025 - II Courses/CS661 - Big Data Visual Analytics/Group_Project/Final Project/Final Project/data"):
#     if not fname.lower().endswith('.geojson'):
#         continue
#     country = os.path.splitext(fname)[0]        # e.g. "Brazil", "China"
#     with open(os.path.join('data/geojson', fname), encoding='utf-8') as f:
#         gj = json.load(f)                       # parse geojson :contentReference[oaicite:0]{index=0}
#     for feat in gj.get('features', []):
#         props = feat.get('properties', {})
#         state = props.get('name', '')
#         cid   = props.get('cartodb_id')
#         if state and cid is not None:
#             lookup.append({
#                 'country': country.lower(),
#                 'state':   state.lower(),
#                 'cartodb_id': cid
#             })

# # 3. Turn that into a DataFrame
# lookup_df = pd.DataFrame(lookup)

# # 4. Normalize your temps DataFrame
# temps_df['country_lc'] = temps_df['Country'].str.lower()
# temps_df['state_lc']   = temps_df['State']  .str.lower()

# # 5. Merge on the two lowercase keys
# merged = temps_df.merge(
#     lookup_df,
#     left_on = ['country_lc','state_lc'],
#     right_on= ['country',  'state'],
#     how='left'
# )

# # 6. Clean up
# merged = (
#     merged
#     .drop(columns=['country_lc','state_lc','country','state'])
#     .rename(columns={'cartodb_id':'cartodb_id'})
# )

# # 7. Save
# merged.to_csv('data/temps_with_cartodb_id.csv', index=False)
# print("Done – saved temps_with_cartodb_id.csv")  




import os
import json
import pandas as pd

# 1. Configuration
CSV_PATH    = "E:/2024-2025 - II Courses/CS661 - Big Data Visual Analytics/Group_Project/Final Project/Final Project/data/Country Temperature/United_States_Temperature.csv"         # your raw CSV
GEOJSON_DIR = "E:/2024-2025 - II Courses/CS661 - Big Data Visual Analytics/Group_Project/Final Project/Final Project/data/united states.geojson"           # folder containing one .geojson per country
OUTPUT_DIR  = 'data/by_country'        # output folder for per-country CSVs

# 2. Read the raw temperature data
temps = pd.read_csv(CSV_PATH, parse_dates=['dt'])
# Normalize casing for join keys
temps['country_lc'] = temps['Country'].str.lower()
temps['state_lc']   = temps['State']  .str.lower()

# 3. Build a global lookup of (country, state) → cartodb_id
lookup_rows = []

fname = GEOJSON_DIR

country = "United States"      # e.g. "Brazil", "China"
path    = fname
with open(path, encoding='utf-8') as f:
    gj = json.load(f)
for feat in gj.get('features', []):
    props = feat.get('properties', {})
    state = props.get('name', '')
    cid   = props.get('cartodb_id')
    if state and cid is not None:
        lookup_rows.append({
            'country_lc': country.lower(),
            'state_lc':   state.lower(),
            'cartodb_id': cid
        })

lookup = pd.DataFrame(lookup_rows)

# 4. Merge cartodb_id into temps
merged = temps.merge(
    lookup,
    on=['country_lc', 'state_lc'],
    how='left'
)

# 5. Prepare output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 6. Split by country and write out
for country, group in merged.groupby('Country'):
    # sanitize country name for filename
    safe = "".join(ch if ch.isalnum() or ch in " _-" else "_" for ch in country).strip()
    filename = f"{safe}.csv"
    outpath  = os.path.join(OUTPUT_DIR, filename)
    group.drop(columns=['country_lc','state_lc']).to_csv(outpath, index=False)
    print(f"Wrote {len(group)} rows to {outpath}")
    
    
missing_states = (
merged
.loc[merged['cartodb_id'].isna(), 'State']   # select rows with no cartodb_id
.dropna()                                     # just in case there are NaNs in State
.str.strip()                                  # clean up whitespace
.unique()                                     # unique names only
)

# 2. Print them out
print("States without a cartodb_id:")
for state in missing_states:
    print(f" - {state}")
