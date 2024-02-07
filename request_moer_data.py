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

def download(time_intervals, region = "CAISO_NORTH", signal_type = "co2_moer", historical = True):
    
    login_url = 'https://api.watttime.org/login'
    rsp = requests.get(login_url, auth=HTTPBasicAuth('aoyuzou', 'aoyuzou36!'))
    TOKEN = rsp.json()['token']
    print(rsp.json())

    # get historical
    if historical:

        moer = []

        url = "https://api.watttime.org/v3/historical"

        
        # Provide your TOKEN here, see https://docs.watttime.org/#tag/Authentication/operation/get_token_login_get for more information
        headers = {"Authorization": f"Bearer {TOKEN}"}
        for i in tqdm(range(len(time_intervals) - 1)):
            params = {
                "region": region,
                "start": time_intervals[i],
                "end": time_intervals[i + 1],
                "signal_type": signal_type
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            moer.append(response)
    
    with open('moer.csv', 'w', newline='') as csv_file:
        fieldnames = moer[0].json()['data'][0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        # Write the header
        writer.writeheader()

        for i in range(len(time_intervals) - 1):
            data = moer[i].json()['data']
            
            # Write the data
            for row in data:
                writer.writerow(row)

def get_moer(time_intervals, region = "CAISO_NORTH", signal_type = "co2_moer", historical = True):

    download(time_intervals, region = region, signal_type = signal_type, historical = True)
    moer_df = pd.read_csv("moer.csv")
    moer_df['datetime'] = pd.to_datetime(moer_df['point_time'])
    moer_df = moer_df.drop(columns='point_time')
    moer_df['moer'] = moer_df['value'] * 0.454
    moer_df.set_index('datetime', inplace=True)
    moer_df = moer_df.resample('15T').mean()
    moer_df = moer_df.reset_index()

    return moer_df
    