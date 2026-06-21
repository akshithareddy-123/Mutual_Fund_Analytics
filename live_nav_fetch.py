import requests
import pandas as pd

scheme_code = "125497"

url = f"https://api.mfapi.in/mf/{scheme_code}"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    if "data" in data:
        df = pd.DataFrame(data["data"])
        df.to_csv("data/raw/live_nav_data.csv", index=False)
        print("Live NAV data saved successfully!")
    else:
        print("No NAV data found")
else:
    print("API request failed")