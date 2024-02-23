
import numpy as np
import pandas as pd
import glob

def get_pump(df, loop = "CHW"):

    if loop == "CHW":
    # Get chilled water loop
        keywords = {"pump":["CHP", "SCHWP"]}

        columns_with_keywords = {}
        # Identify columns containing the keywords
        for keyword in keywords:
            # Initialize a list to hold column names for this keyword
            columns_with_keywords[keyword] = []
            
            # Inner loop iterates over each column name in the DataFrame
            for col in df.columns:
                # Check if the keyword is in the column name

                for word in keywords[keyword]:
                    if word in col:
                        # If yes, append the column name to the list for this keyword
                        columns_with_keywords[keyword].append(col)


        # Create sub DataFrames based on identified columns
        sub_dataframes = {}
        for keyword, cols in columns_with_keywords.items():
            # Include the first column ('ID') and the columns with the keyword
            selected_cols = ['datetime'] + cols
            sub_dataframes[keyword] = df[selected_cols]

        df_pump = sub_dataframes['pump'] 
    
    elif loop == "CW":
    # Get chilled water loop
        keywords = {"pump":["CWP"]}

        columns_with_keywords = {}
        # Identify columns containing the keywords
        for keyword in keywords:
            # Initialize a list to hold column names for this keyword
            columns_with_keywords[keyword] = []
            
            # Inner loop iterates over each column name in the DataFrame
            for col in df.columns:
                # Check if the keyword is in the column name

                for word in keywords[keyword]:
                    if word in col:
                        # If yes, append the column name to the list for this keyword
                        columns_with_keywords[keyword].append(col)


        # Create sub DataFrames based on identified columns
        sub_dataframes = {}
        for keyword, cols in columns_with_keywords.items():
            # Include the first column ('ID') and the columns with the keyword
            selected_cols = ['datetime'] + cols
            sub_dataframes[keyword] = df[selected_cols]

        df_pump = sub_dataframes['pump']
    
    return df_pump


def get_CT(df):
    keywords = {"current":["CURRENT", "CT"]}

    columns_with_keywords = {}
    # Identify columns containing the keywords
    for keyword in keywords:
        # Initialize a list to hold column names for this keyword
        columns_with_keywords[keyword] = []
        
        # Inner loop iterates over each column name in the DataFrame
        for col in df.columns:
            # Check if the keyword is in the column name

            for word in keywords[keyword]:
                if word in col:
                    # If yes, append the column name to the list for this keyword
                    columns_with_keywords[keyword].append(col)


    # Create sub DataFrames based on identified columns
    sub_dataframes = {}
    for keyword, cols in columns_with_keywords.items():
        # Include the first column ('ID') and the columns with the keyword
        selected_cols = ['datetime'] + cols
        sub_dataframes[keyword] = df[selected_cols]

    df_current = sub_dataframes['current'] 
    return df_current

def get_power(df, unit = "W"):
    keywords = {"power":['POWER', 'PWR']}

    columns_with_keywords = {}
    # Identify columns containing the keywords
    for keyword in keywords:
        # Initialize a list to hold column names for this keyword
        columns_with_keywords[keyword] = []
        
        # Inner loop iterates over each column name in the DataFrame
        for col in df.columns:
            # Check if the keyword is in the column name

            for word in keywords[keyword]:
                if word in col:
                    # If yes, append the column name to the list for this keyword
                    columns_with_keywords[keyword].append(col)


    # Create sub DataFrames based on identified columns
    sub_dataframes = {}
    for keyword, cols in columns_with_keywords.items():
        # Include the first column ('ID') and the columns with the keyword
        selected_cols = ['datetime'] + cols
        sub_dataframes[keyword] = df[selected_cols]

    df_pwr = sub_dataframes['power']

    if unit == "W":
        df_pwr.iloc[:, 1:] = df_pwr.iloc[:, 1:] / 1000
    
    return df_pwr

def get_demand(df):
    # split into peak demand and power dataframe
    # Define the keywords
    keywords = ['DEMAND']

    # Identify columns containing the keywords
    columns_with_keywords = {keyword: [col for col in df.columns if keyword in col] for keyword in keywords}


    # Create sub DataFrames based on identified columns
    sub_dataframes = {}
    for keyword, cols in columns_with_keywords.items():
        # Include the first column ('ID') and the columns with the keyword
        selected_cols = ['datetime'] + cols
        sub_dataframes[keyword] = df[selected_cols]

    df_DEMAND = sub_dataframes['DEMAND']
    return df_DEMAND

def get_substation(df, keyword = 'MSA.'):

    # Identify columns containing the keywords
    columns_with_keywords = {keyword: [col for col in df.columns if keyword in col]}

    # Create sub DataFrames based on identified columns
    sub_dataframes = {}
    for keyword, cols in columns_with_keywords.items():
        # Include the first column ('ID') and the columns with the keyword
        selected_cols = ['datetime'] + cols
        sub_dataframes[keyword] = df[selected_cols]

    df_substation = sub_dataframes[keyword]
    return df_substation

# Define the function to process a single CSV file
def read_grid_demand(filepath):

    df = pd.read_csv(filepath)
    df = df[df['TAC_AREA_NAME'] == 'CA ISO-TAC']
    df = df[['INTERVALSTARTTIME_GMT', 'MW']]
    df['datetime'] = pd.to_datetime(df['INTERVALSTARTTIME_GMT'])
    df['datetime'] = df['datetime'].dt.tz_convert('America/Los_Angeles')
    df.drop(columns='INTERVALSTARTTIME_GMT', inplace=True)
    df.sort_values(by='datetime', inplace=True)
    return df

def get_grid_demand(filepaths):
    # Get all CSV file paths from the folder

    filepaths = glob.glob(filepaths)

    # Process each CSV file and collect the DataFrames
    dfs = [read_grid_demand(filepath) for filepath in filepaths]

    # Combine all DataFrames vertically
    combined_df = pd.concat(dfs, ignore_index=True)

    # Sort the combined DataFrame by datetime just in case
    combined_df.sort_values(by='datetime', inplace=True)

    # If you want to reset the index of the combined DataFrame
    combined_df.reset_index(drop=True, inplace=True)

    # Now combined_df is ready for use
    combined_df.set_index('datetime', inplace=True)
    combined_df.reset_index(inplace=True)
    combined_df.columns = ['datetime', 'demand']

    return combined_df

# Define the function to process a single CSV file
def read_grid_renew(filepath, type):

    df = pd.read_csv(filepath)
    df = df[['INTERVALSTARTTIME_GMT', 'RENEWABLE_TYPE', 'MW']]
    df = df[df['RENEWABLE_TYPE'] == type]
    df['datetime'] = pd.to_datetime(df['INTERVALSTARTTIME_GMT'])
    df['datetime'] = df['datetime'].dt.tz_convert('America/Los_Angeles')
    df.drop(columns=['INTERVALSTARTTIME_GMT', 'RENEWABLE_TYPE'], inplace=True)
    df.sort_values(by='datetime', inplace=True)
    return df

def get_grid_renew(filepaths, type):
    # Get all CSV file paths from the folder

    filepaths = glob.glob(filepaths)

    # Process each CSV file and collect the DataFrames
    dfs = [read_grid_renew(filepath, type) for filepath in filepaths]

    # Combine all DataFrames vertically
    combined_df = pd.concat(dfs, ignore_index=True)

    # Sort the combined DataFrame by datetime just in case
    combined_df.sort_values(by='datetime', inplace=True)

    # If you want to reset the index of the combined DataFrame
    combined_df.reset_index(drop=True, inplace=True)

    # Now combined_df is ready for use
    combined_df.set_index('datetime', inplace=True)
    combined_df.reset_index(inplace=True)
    combined_df.columns = ['datetime', type]

    return combined_df