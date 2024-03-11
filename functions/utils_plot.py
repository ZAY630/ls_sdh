import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

def make_plot(df, names = [], date = '', unit = '', plot_title = '', figsize = ()):
    df['datetime'] = pd.to_datetime(df.iloc[:, 0])

    if names == []:
        names = df.columns[1:]

    if date != '':
        df = df[df['datetime'].dt.date == pd.to_datetime(date)]

    plt.figure(figsize=figsize)

    # Plotting each column against the 'datetime'
    for column in names:
        plt.plot(df['datetime'], df[column], label = column)

    plt.title(plot_title, fontsize = 18)
    plt.legend()

    # Add units to y-tick labels
    ax = plt.gca()  # Get the current Axes instance
    y_ticks = ax.get_yticks()  # Get the current y-tick values
    ax.set_yticklabels([f'{y:.2f}{unit}' for y in y_ticks])
    
    plt.show()


def plot_hourly_heatmap(df, columns, annotation='', figsize = ()):
    
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
    heatmap = sns.heatmap(heatmap_data, cmap='viridis_r', linewidths=0)

    # Modify color bar label, adding units
    color_bar = heatmap.collections[0].colorbar
    color_bar.set_label(annotation, rotation=270, labelpad=24, fontsize=15)
    color_bar.ax.set_aspect(40)

    # Identify the positions and labels for the first day of each month
    first_days = pd.date_range(start=heatmap_data.index.min(), 
                               end=heatmap_data.index.max(), 
                               freq='MS').date  # 'MS' means month start
    first_days_positions = [i for i, date in enumerate(heatmap_data.index) if date in first_days]
    first_days_labels = [date.strftime('%Y-%m-%d') for date in first_days if date in heatmap_data.index]

    # Set y-tick positions and labels for the first day of each month
    heatmap.set_yticks(np.array(first_days_positions) + 0.5)  # +0.5 centers labels
    heatmap.set_yticklabels(first_days_labels, rotation=0)  # Set labels with no rotation
    heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=0)  # Ensures labels are not rotated

    # Set additional labels and titles
    hours = list(range(24))  # 0 to 23
    plt.xticks(np.arange(len(hours)) + 0.5, labels=hours)  # Adjust tick positions and labels
    plt.xlabel('Hour of the Day', fontsize=15)
    plt.title('Hourly Heatmap', fontsize=18)

    plt.show()
    df.reset_index(inplace = True)


def create_violin_plot(df, columns, unit, axe, plot_title='', annotation = True, hide_xticks = False, xlabel = '', ylim = []):
    # Create the violin plot
    # plt.figure(figsize=figsize)
    sns.violinplot(data=df[columns], ax=axe, inner=None, width=0.4, linewidth=0, saturation=0.4)
    sns.boxplot(data=df[columns], width=0.1, boxprops={'zorder': 2}, ax=axe, showfliers=False)

    # Calculate and print mean and median on the plot
    if annotation == True:
        for i, col in enumerate(columns):
            # Calculate statistics
            mean = df[col].mean()
            median = df[col].median()
            
            # Annotate the statistics on the plot
            # plt.text(i + 0.1, mean, f'Mean: {mean:.2f}', horizontalalignment='center', size='small', color='black', weight='semibold')
            axe.text(i + 0.1, median, f'{median:.0f}{unit}', horizontalalignment='left', size='large', color='black', weight='bold', fontsize = 14)
    # Set the x and y labels
    # ax = plt.gca()  # Get the current Axes instance
    y_ticks = axe.get_yticks()  # Get the current y-tick values
    axe.set_yticklabels([f'{y:.2f}{unit}' for y in y_ticks])
    axe.set_title(plot_title, fontsize = 16)
    if hide_xticks:
        axe.set_xticklabels([])
    axe.set_xlabel(xlabel, fontsize = 16)
    axe.tick_params(axis='both', labelsize=14)
    axe.spines['top'].set_visible(False)
    axe.spines['right'].set_visible(False)
    axe.spines['left'].set_visible(False)
    axe.spines['bottom'].set_visible(False)
    if ylim:
        axe.set_ylim(ylim[0], ylim[1])
    plt.setp(axe.collections, alpha=.5)
    