import json
# import re
import pandas as pd
with open("dataset/aedwtdata2-en.json", "r", encoding="utf-8") as file:
    data = json.load(file)

records = data["waitTime"]
# print("data type:", type(data))
# print("top-level keys:",list(data.keys()) if isinstance(data, dict) else "JSON is a list")

# if isinstance(data, dict) and "results" in data:
#     results = data["results"]
# elif isinstance(data, dict) and "data" in data:
#     results = data["data"]
# elif isinstance(data, list):
#     results = data
# else:
#     records =None

# if records is not None:
df = pd.json_normalize(records)
print("Dataset shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())
print("\nColumns:", df.columns.tolist())
df.to_csv("dataset/aed_waiting_time.csv", index=False, encoding="utf-8")
print("\nCSV file created successfully!!!")

# else:
#     print("JSON structure needs inspection before conversion!!")
   