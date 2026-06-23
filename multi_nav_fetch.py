import requests
import pandas as pd

schemes = {
    "SBI_Bluechip": "119551",
    "ICICI_Bluechip": "120503",
    "Nippon_LargeCap": "118632",
    "Axis_Bluechip": "119092",
    "Kotak_Bluechip": "120841"
}

for name, code in schemes.items():
    url = f"https://api.mfapi.in/mf/{code}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if "data" in data:
            df = pd.DataFrame(data["data"])

            filename = f"data/raw/{name}.csv"
            df.to_csv(filename, index=False)

            print(f"Saved: {filename}")
        else:
            print(f"No data found for {name}")
    else:
        print(f"API failed for {name}")