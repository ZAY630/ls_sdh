import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

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

def create_daily_heatmap(df):
    # Pivot the DataFrame to get dates on one axis and times on another
    df['date'] = df['datetime'].dt.date
    df['time'] = df['datetime'].dt.time
    df_pivot = df.pivot_table(index='date', columns='time', values=df.columns[1:], aggfunc='mean')

    # Create a heatmap
    plt.figure(figsize=(18, 20))  # You may want to adjust the size depending on your actual data
    sns.heatmap(df_pivot, cmap='viridis_r', linewidths=.5)
    
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
    plt.figure(figsize=(18, 20))
    heatmap = sns.heatmap(heatmap_data, cmap='viridis_r', linewidths=.5)
    heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=0)  # Ensures labels are not rotated
    hours = list(range(24))  # 0 to 23
    plt.xticks(np.arange(len(hours)) + .5, labels=hours)  # Adjust tick positions and labels

    plt.ylabel('Day')
    plt.xlabel('Hour of the Day')
    plt.title('Hourly Heatmap')

    plt.show()


def create_violin_plot(df, columns):
    # Create the violin plot
    plt.figure(figsize=[20, 10])
    ax = sns.violinplot(data=df[columns])
    
    # Calculate and print mean and median on the plot
    for i, col in enumerate(columns):
        # Calculate statistics
        mean = df[col].mean()
        median = df[col].median()
        
        # Annotate the statistics on the plot
        # plt.text(i + 0.1, mean, f'Mean: {mean:.2f}', horizontalalignment='center', size='small', color='black', weight='semibold')
        plt.text(i - 0.1, median, f'Median: {median:.2f}', horizontalalignment='center', size='small', color='black', weight='semibold')
    
    # Set the x and y labels
    ax.set_xlabel('Column')
    ax.set_ylabel('Values')
    
    # Show the plot
    plt.show()
