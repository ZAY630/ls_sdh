import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib.ticker import MaxNLocator

def make_plot(df, names = [], date = '', unit = '', yrange = [], plot_title = '', figsize = ()):
    df['datetime'] = pd.to_datetime(df.iloc[:, 0])

    if names == []:
        names = df.columns[1:]

    if date != '':
        df = df[df['datetime'].dt.date == pd.to_datetime(date)]

    plt.figure(figsize=figsize)

    # Plotting each column against the 'datetime'
    for column in names:
        plt.plot(df['datetime'], df[column], label = column)

    plt.title(plot_title, fontsize = 20)
    plt.legend()

    # Add units to y-tick labels
    new_ticks = np.arange(yrange[0], yrange[1] + 1, yrange[2])  # Adjust the step value as needed

    # Set the new ticks
    plt.gca().set_yticks(new_ticks)

    # Format tick labels to show only the integer part and add "units" to the last label
    tick_labels = [f"{int(tick)}" for tick in new_ticks[:-1]] + [f"{int(new_ticks[-1])}{unit}"]
    plt.gca().set_yticklabels(tick_labels)
    plt.gca().tick_params(axis='both', labelsize=18)
    
    plt.show()


def plot_hourly_heatmap(df, columns, annotation='', plot_title = '', cbar_ticks = [], cbar_label = [], figsize = ()):
    
   # Ensure datetime is the correct type for processing
    df['datetime'] = pd.to_datetime(df['datetime'])  # Convert if not already in datetime format
    
    # Set datetime as the index
    df.set_index('datetime', inplace=True)
    
    # Resample data into hourly bins and take the mean of each bin
    hourly_data = df[columns].resample('H').mean()
    
    # Prepare data for heatmap (days as rows, hours as columns)
    heatmap_data = hourly_data.pivot_table(index=hourly_data.index.date, 
                                           columns=hourly_data.index.hour, 
                                           values=columns, 
                                           aggfunc='mean')

    # Plot heatmap
    plt.figure(figsize=figsize)
    heatmap = sns.heatmap(heatmap_data, cmap='viridis_r', linewidths=0, cbar_kws={'orientation': 'horizontal', 'pad': 0.1})

    # Modify color bar label, adding units
    cbar = heatmap.collections[0].colorbar
    cbar.set_label(annotation, labelpad=-80, fontsize=16)
    cbar.ax.tick_params(labelsize=14)
    if cbar_ticks:
        cbar.set_ticks(cbar_ticks) 
        cbar.set_ticklabels(cbar_label) 

    # Identify the positions and labels for the first day of each month
    month_positions = []
    month_labels = []
    for i, date_str in enumerate(heatmap_data.index):
        date = pd.to_datetime(date_str)
        if date.day == 1:  # Check if it's the first day of the month
            month_positions.append(i)
            month_labels.append(date.strftime('%b'))

    # Set y-tick positions and labels for the first day of each month
    heatmap.set_yticks(np.array(month_positions) + 0.5)  # +0.5 centers labels
    heatmap.set_yticklabels(month_labels, rotation=0)  # Set labels with no rotation

    # Set additional labels and titles
    hours = ['12 AM', '3 AM', '6 AM', '9 AM', '12 PM', '3 PM', '6 PM', '9 PM']
    hour_positions = [0, 3, 6, 9, 12, 15, 18, 21]  # Corresponding positions in 24-hour format
    plt.xticks(hour_positions, labels=hours, rotation = 0)  # Adjust tick positions and labels
    plt.title(plot_title, fontsize=20)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlabel(xlabel=None)
    plt.show()
    df.reset_index(inplace = True)


def create_box_plot(df, columns, unit, axe, plot_title='', annotation = True, hide_xticks = False, xlabel = '', yrange = [], type = False):

    # Calculate and print mean and median on the plot
    if annotation == True:
        if type:
            medians = df.groupby([columns + ['type']])[columns].median().reset_index()
            for _, row in medians.iterrows():
                # Adjust the text position (x, y) and alignment as necessary
                axe.text(row['hour'] - 0.15 if row['type'] == 'high' else row['hour'] + 0.15, 
                        median * 1.01, 
                        f'{median:.0f}{unit}', 
                        horizontalalignment='center', size='large', color='black', weight='bold', fontsize = 14)

        else:
            for i, col in enumerate(columns):
                # Calculate statistics
                mean = df[col].mean()
                median = df[col].median()   
                
                # Annotate the statistics on the plot
                axe.text(i, median * 1.025, f'{median:.0f}{unit}', horizontalalignment='center', size='large', color='black', weight='bold', fontsize = 14)


    # Map median values to colors
    if type:
        sns.boxplot(x='hour', y=columns[0], hue=type, data=df, width=0.75, ax=axe, showfliers=False, palette=['#a8ddb5', '#fe9929'])
        plt.legend(fontsize='18', loc='lower right')
    else:
        sns.boxplot(data=df[columns], width=0.5, ax=axe, showfliers=False, color="#a6bddb")


    axe.set_ylim(yrange[0], yrange[1])
    new_ticks = np.arange(yrange[0], yrange[1] + 1, yrange[2])  # Generate 4 evenly spaced ticks within the current range
    axe.set_yticks(new_ticks)

    # Change tick labels to show only the integer part
    tick_labels = [f"{int(tick)}" for tick in new_ticks[:-1]] + [f"{int(new_ticks[-1])}{unit}"]  # Convert to integer and add "units" to the last label
    axe.set_yticklabels(tick_labels)
    axe.set_ylabel(None)
    axe.set_title(plot_title, fontsize = 22)
    if hide_xticks:
        axe.set_xticklabels([])
    axe.set_xlabel(xlabel, fontsize = 20)
    axe.tick_params(axis='y', which = 'major', length=10, width=2, labelsize=20)
    axe.tick_params(axis='x', labelsize=20)

    axe.spines['top'].set_visible(False)
    axe.spines['right'].set_visible(False)
    axe.spines['left'].set_visible(False)
    axe.spines['bottom'].set_visible(False)
    plt.setp(axe.collections, alpha=.5)

def create_bar_plot(df, columns, unit, plot_title='', annotation = True, xlabel = '', yrange = [], dual_columns = [], dual_unit = '', figsize = (), conversion_factor = 1):

    if dual_columns:

        # Create the primary y-axis for the bar plot
        ax1 = df[columns].plot(kind='bar', figsize=figsize)

        # Adjust y-tick labels for primary y-axis
        new_ticks = np.arange(yrange[0], yrange[1] + 1, yrange[2])  # Ensure max value is included
        ax1.set_yticks(new_ticks)
        tick_labels = [f"{int(tick)}" for tick in new_ticks[:-1]] + [f"{int(new_ticks[-1])}{unit}"]
        ax1.set_yticklabels(tick_labels)
        plt.xticks(rotation=0)  # Set x-ticks if df.index is not numeric

        # Annotate the primary bars with values
        if annotation:
            for i, anno in enumerate(df[columns]):
                    
                    # Annotate the statistics on the plot
                    plt.text(i, anno * 1.025, f'{anno:.0f}{unit}', horizontalalignment='center', size='large', color='black', fontsize = 14)

        # Create the secondary y-axis for kWh/ft2
        ax2 = ax1.twinx()
        ax2.plot(df[columns].index, df[dual_columns], marker='', linestyle='')  # Plot as points
        new_ticks = np.arange(round(yrange[0] * conversion_factor), round((yrange[1] + 1) * conversion_factor), round(yrange[2] * conversion_factor / 5) * 5)  # Ensure max value is included
        ax2.set_yticks(new_ticks)
        tick_labels = [f"{round(tick)}" for tick in new_ticks[:-1]] + [f"{round(new_ticks[-1])}{dual_unit}"]
        ax2.set_yticklabels(tick_labels)

        # General plot settings
        ax1.tick_params(axis='y', which = 'major', length=10, width=2, labelsize=16)
        ax2.tick_params(axis='y', which = 'major', length=10, width=2, labelsize=16)
        ax1.tick_params(axis='x', labelsize=16)
        ax2.tick_params(axis='x', labelsize=16)

        ax1.set_xlabel(xlabel, fontsize=16)
        ax1.set_title(plot_title, fontsize=18)

        # Hide unwanted spines
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)

        # Show the plot
        plt.show()

    else:
        df[columns].plot(kind='bar', figsize = figsize)
        # Add units to y-tick labels
        new_ticks = np.arange(yrange[0], yrange[1], yrange[2])  # Adjust the step value as needed
        plt.gca().set_yticks(new_ticks)
        tick_labels = [f"{int(tick)}" for tick in new_ticks[:-1]] + [f"{int(new_ticks[-1])}{unit}"]
        plt.gca().set_yticklabels(tick_labels)
        plt.gca().tick_params(axis='both', which = 'major', length=10, width=2, labelsize=16)
        plt.xticks(rotation = 0)
        plt.xlabel(xlabel)
        plt.title(plot_title, fontsize = 18)
        if annotation:
            for i, anno in enumerate(df[columns]):
                    
                    # Annotate the statistics on the plot
                    plt.text(i, anno * 1.025, f'{anno:.0f}{unit}', horizontalalignment='center', size='large', color='black', fontsize = 14)

        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(False)
        plt.show()