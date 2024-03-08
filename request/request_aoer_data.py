"""
Retreive data from WattTime API

"""
from datetime import datetime, timedelta
import csv
from tqdm import tqdm
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth

def get_intervals(start = "2022-05-01", end = "2022-09-01"):

    start_dt = datetime.strptime(start, '%Y-%m-%d')
    end_dt = datetime.strptime(end, '%Y-%m-%d')    

    # Create a list for each month interval
    current_dt = start_dt
    time_intervals = []

    while current_dt < end_dt:
        # Calculate the last moment of the current month
        next_month = current_dt + timedelta(days=32)  # Add enough days to be sure we're in the next month
        next_month = next_month.replace(day=1)  # Go to the first day of the next month
        
        # Ensure we don't go beyond the end time
        if next_month > end_dt:
            next_month = end_dt
        
        # Add the time interval to the list
        time_intervals.append((current_dt.strftime('%Y-%m-%dT%H:%M+00:00')))
        
        # Move to the next month
        current_dt = next_month

    time_intervals.append((end_dt).strftime('%Y-%m-%dT%H:%M+00:00'))

    return time_intervals

def download_raw(time_intervals, region = "CAISO", signal_type = "co2_aoer", historical = True):
    
    login_url = 'https://api.watttime.org/login'
    rsp = requests.get(login_url, auth=HTTPBasicAuth('aoyuzou36', 'aoyuzou36!'))
    TOKEN = rsp.json()['token']
    print(rsp.json())

    # get historical
    if historical:

        aoer = []

        url = "https://api.watttime.org/v3/historical"

        # import pdb; pdb.set_trace()
        
        # Provide your TOKEN here, see https://docs.watttime.org/#tag/Authentication/operation/get_token_login_get for more information
        headers = {"Authorization": f"Bearer {TOKEN}"}
        for i in tqdm(range(len(time_intervals) - 1)):
            params = {
                "region": region,
                "start": time_intervals[i],
                "end": time_intervals[i + 1],
                "signal_type": signal_type,
                "include_imputed_marker": True,
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            aoer.append(response)
    
    with open('../aoer/aoer_raw.csv', 'w', newline='') as csv_file:
        fieldnames = aoer[0].json()['data'][0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        # Write the header
        writer.writeheader()

        for i in range(len(time_intervals) - 1):
            data = aoer[i].json()['data']
            
            # Write the data
            for row in data:
                writer.writerow(row)

def aoer_15(filename):

    aoer_df = pd.read_csv(filename)
    aoer_df['datetime'] = pd.to_datetime(aoer_df['point_time'])
    aoer_df = aoer_df.drop(columns='point_time')
    aoer_df['aoer'] = aoer_df['value'] * 0.454
    aoer_df.set_index('datetime', inplace=True)
    aoer_df = aoer_df.resample('15T').mean()
    aoer_df = aoer_df.reset_index()

    return aoer_df

if __name__ == "__main__":

    start = "2023-01-01"
    end = "2023-01-02"

    time_intervals = get_intervals(start, end)
    download_raw(time_intervals, region = "CAISO", signal_type = "co2_aoer", historical = True)
    aoer_df = aoer_15("../aoer/aoer_raw.csv")

    # Save DataFrame to a CSV file
    aoer_df.to_csv("../aoer/aoer_15.csv", index=False)
    
