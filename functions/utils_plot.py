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
    
    # Set datetime as the index
    df.set_index('datetime', inplace=True)
    
    # Resample data into hourly bins and take the mean of each bin
    hourly_data = df[columns].resample('H').mean()
    
    # Prepare data for heatmap (days as rows, hours as columns)
    heatmap_data = hourly_data.pivot_table(index=hourly_data.index.date, 
                                           columns=hourly_data.index.hour, 
                                           values=columns, 
                                           aggfunc='mean')


    df.reset_index(inplace=True)

    # Plot heatmap
    plt.figure(figsize=figsize)
    heatmap = sns.heatmap(heatmap_data, cmap='viridis_r', linewidths=.5)
    heatmap.set_xticklabels(heatmap.get_xticklabels(), rotation=0)  # Ensures labels are not rotated

    # Modify color bar label, adding units
    color_bar = heatmap.collections[0].colorbar  # Get the colorbar instance of the heatmap
    color_bar.set_label(annotation, rotation=270, labelpad=24, fontsize = 15)  # Set label with units
    color_bar.ax.set_aspect(40)

    # Get the current position of the color bar (returns [left, bottom, width, height])
    cbar_pos = color_bar.ax.get_position()

    # Modify the position parameters as needed (e.g., move closer by decreasing 'left')
    # Here '0.05' is just an example value for how much you want to move it closer; adjust as necessary
    new_pos = [cbar_pos.x0 - 0.025, cbar_pos.y0, cbar_pos.width, cbar_pos.height]

    # Set the new position
    color_bar.ax.set_position(new_pos)

    hours = list(range(24))  # 0 to 23
    plt.xticks(np.arange(len(hours)) + .5, labels=hours)  # Adjust tick positions and labels
    plt.xlabel('Hour of the Day', fontsize = 15)
    plt.title('Hourly Heatmap', fontsize = 18)

    plt.show()


def create_violin_plot(df, columns, unit, plot_title, figsize = (), annotation = True):
    # Create the violin plot
    plt.figure(figsize=figsize)
    ax = sns.violinplot(data=df[columns], inner=None, linewidth=0, saturation=0.4)
    sns.boxplot(data=df[columns], width=0.1, boxprops={'zorder': 2}, ax=ax, showfliers=False)

    # Calculate and print mean and median on the plot
    if annotation == True:
        for i, col in enumerate(columns):
            # Calculate statistics
            mean = df[col].mean()
            median = df[col].median()
            
            # Annotate the statistics on the plot
            # plt.text(i + 0.1, mean, f'Mean: {mean:.2f}', horizontalalignment='center', size='small', color='black', weight='semibold')
            plt.text(i + 0.15, median, f'{median:.0f}{unit}', horizontalalignment='center', size='large', color='black', weight='bold')
    # Set the x and y labels
    ax = plt.gca()  # Get the current Axes instance
    y_ticks = ax.get_yticks()  # Get the current y-tick values
    ax.set_yticklabels([f'{y:.2f}{unit}' for y in y_ticks])
    ax.set_title(plot_title, fontsize = 20)
    plt.setp(ax.collections, alpha=.5)
 
    # Show the plot
    plt.show()
