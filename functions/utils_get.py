
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
