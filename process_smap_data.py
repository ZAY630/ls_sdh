import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

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

def make_plot(df, names = [], date = ''):
    df['datetime'] = pd.to_datetime(df.iloc[:, 0])

    if names == []:
        names = df.columns[1:]

    if date != '':
        df = df[df['datetime'].dt.date == pd.to_datetime(date)]

    plt.figure(figsize=(20, 10))

    # Plotting each column against the 'datetime'
    for column in names:
        plt.plot(df['datetime'], df[column], label = column)
        plt.title(f"{column}")
        plt.xlabel('Datetime')
        plt.ylabel('Value')
        plt.legend()

    plt.show()


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

def create_daily_heatmap(df):
    # Pivot the DataFrame to get dates on one axis and times on another
    df['date'] = df['datetime'].dt.date
    df['time'] = df['datetime'].dt.time
    df_pivot = df.pivot_table(index='date', columns='time', values=df.columns[1:], aggfunc='mean')

    # Create a heatmap
    plt.figure(figsize=(15, 7))  # You may want to adjust the size depending on your actual data
    sns.heatmap(df_pivot, cmap='viridis', linewidths=.5)
    
    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.title('Daily Heatmap')
    plt.tight_layout()  # Adjust layout to fit everything nicely
    plt.show()

    return plt

def plot_hourly_heatmap(df, columns):
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Set datetime as the index
    df.set_index('datetime', inplace=True)
    
    # Resample data into hourly bins and take the mean of each bin
    hourly_data = df[columns].resample('H').mean()
    
    # Prepare data for heatmap (days as rows, hours as columns)
    heatmap_data = hourly_data.pivot_table(index=hourly_data.index.date, 
                                           columns=hourly_data.index.hour, 
                                           values=columns, 
                                           aggfunc='mean')


    df = df.reset_index()

    # Plot heatmap
    plt.figure(figsize=(18, 10))
    heatmap = sns.heatmap(heatmap_data, cmap='viridis', linewidths=.5)
    heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=0)  # Ensures labels are not rotated
    hours = list(range(24))  # 0 to 23
    plt.xticks(np.arange(len(hours)) + .5, labels=hours)  # Adjust tick positions and labels

    plt.ylabel('Day')
    plt.xlabel('Hour of the Day')
    plt.title('Hourly Heatmap')

    plt.show()
