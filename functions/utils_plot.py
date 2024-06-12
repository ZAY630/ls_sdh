import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.dates as mdates

def make_plot(df, 
              axe, 
              columns = [], 
              date = '', 
              yrange = [], 
              plot_title = '', 
              color = [], 
              hide_xticks = False, 
              xlabel = '', 
              ylabel = '',
              dual_columns = [], 
              dual_ylabel = '', 
              conversion_factor = 1, 
              legend=[]):
    
    if dual_columns:
        df['datetime'] = pd.to_datetime(df.iloc[:, 0])

        if columns == []:
            columns = df.columns[1:]

        if date != '':
            df = df[df['datetime'].dt.date == pd.to_datetime(date)]

        if color:
            for idx, column in enumerate(columns):
                axe.plot(df['datetime'], df[column], lw = 4, color=color[idx], label = legend[idx])
        else:
            for idx, column in enumerate(columns):
                axe.plot(df['datetime'], df[column], lw = 4, label = legend[idx])

        plt.title(plot_title, fontsize = 24)
        axe.set_ylim(yrange[0], yrange[1])
        new_ticks = np.arange(yrange[0], yrange[1], yrange[2])  # Generate 4 evenly spaced ticks within the current range
        axe.set_yticks(new_ticks)
        axe.set_ylabel(ylabel, fontsize = 22)
        axe.set_title(plot_title, fontsize = 24)
        if hide_xticks:
            axe.set_xticklabels([])
        axe.set_xlabel(xlabel, fontsize = 22)

        if date:
            axe.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))
            axe.xaxis.set_major_formatter(mdates.DateFormatter('%-I %p'))  # '%I %p' for 12-hour clock format with AM/PM
            
        # Create the secondary y-axis for kWh/ft2
        ax2 = axe.twinx()
        ax2.set_yticks(new_ticks)
        secondary_y_tick_labels = [f'{round(y * conversion_factor)}' for y in new_ticks]
        ax2.set_yticklabels(secondary_y_tick_labels)
        ax2.set_ylim(yrange[0], yrange[1])
        ax2.set_ylabel(dual_ylabel, fontsize = 22)

        # General plot settings
        axe.tick_params(axis='y', which = 'major', length=10, width=2, labelsize=22)
        ax2.tick_params(axis='y', which = 'major', length=10, width=2, labelsize=22)
        axe.tick_params(axis='x', labelsize=22)
        ax2.tick_params(axis='x', labelsize=22)

        axe.set_xlabel(xlabel, fontsize=22)
        axe.yaxis.grid(True, linestyle='-', color='lightgrey')

        # Hide unwanted spines
        axe.spines['top'].set_visible(False)
        axe.spines['right'].set_visible(False)
        axe.spines['left'].set_visible(False)
        axe.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        
    else:

        if columns == []:
            columns = df.columns[1:]

        if date != '':
            df = df[df['datetime'].dt.date == pd.to_datetime(date)]

        # Plotting each column against the 'datetime'
        if color:
            for idx, column in enumerate(columns):
                axe.plot(df['datetime'], df[column], lw = 4, color=color[idx], label = legend[idx])
        else:
            for idx, column in enumerate(columns):
                axe.plot(df['datetime'], df[column], lw = 4, label = legend[idx])

        axe.set_title(plot_title, fontsize = 24)
        plt.legend(fontsize=18, loc='upper left')

        # Add units to y-tick labels
        new_ticks = np.arange(yrange[0], yrange[1], yrange[2])  # Adjust the step value as needed

        # Set the new ticks
        axe.set_yticks(new_ticks)
        axe.set_ylabel(ylabel, fontsize=22)

        # Format date ticks
        # Set major locator to 6 hours and use a DateFormatter for the x-axis
        if date:
            axe.xaxis.set_major_locator(mdates.HourLocator(byhour=[1, 7, 13, 19]))
            axe.xaxis.set_major_formatter(mdates.DateFormatter('%-I %p', tz=df['datetime'].dt.tz))  # '%I %p' for 12-hour clock format with AM/PM

        axe.tick_params(axis='both', labelsize=22)
        axe.tick_params(axis='y', which = 'major', length=10, width=2)
        axe.spines['top'].set_visible(False)
        axe.spines['right'].set_visible(False)
        axe.spines['left'].set_visible(False)
        axe.spines['bottom'].set_visible(False)
        axe.yaxis.grid(True, linestyle='-', color='lightgrey')


def plot_hourly_heatmap(df, 
                        columns, 
                        annotation='', 
                        plot_title = '', 
                        cbar_ticks = [], 
                        cbar_label = [], 
                        figsize = ()):
    
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
    heatmap = sns.heatmap(heatmap_data, cmap='viridis_r', linewidths=0, cbar_kws={'orientation': 'horizontal', 'pad': 0.1, 'shrink': 0.75})

    # Modify color bar label, adding units
    cbar = heatmap.collections[0].colorbar
    cbar.set_label(annotation, labelpad=-70, fontsize=22)
    cbar.ax.tick_params(labelsize=22)

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
    hours = ['12 AM', '6 AM', '12 PM', '6 PM']
    hour_positions = [0, 6, 12, 18]  # Corresponding positions in 24-hour format
    plt.xticks(hour_positions, labels=hours, rotation = 0)  # Adjust tick positions and labels
    plt.title(plot_title, fontsize=24)
    plt.xticks(fontsize=22)
    plt.yticks(fontsize=22)
    plt.xlabel(xlabel=None)
    plt.show()
    df.reset_index(inplace = True)


def create_box_plot(df, 
                    columns, 
                    unit, 
                    axe, 
                    plot_title='', 
                    annotation = True, 
                    hide_xticks = False, 
                    xlabel = '', 
                    ylabel = '',
                    yrange = [], 
                    color = [], 
                    type = False, 
                    dual_columns = [], 
                    dual_ylabel = '', 
                    conversion_factor = 1):

    # Calculate and print mean and median on the plot
    if dual_columns:
        if annotation == True:
            if type:
                medians = df.groupby([columns + ['type']])[columns].median().reset_index()
                for _, row in medians.iterrows():
                    # Adjust the text position (x, y) and alignment as necessary
                    axe.text(row['hour'] - 0.15 if row['type'] == 'high' else row['hour'] + 0.15, 
                            median * 1.01, 
                            f'{median:.0f}', 
                            horizontalalignment='center', size='large', color='black', fontsize = 18)

            else:
                for i, col in enumerate(columns):
                    # Calculate statistics
                    mean = df[col].mean()
                    median = df[col].median()   
                    
                    # Annotate the statistics on the plot
                    axe.text(i, median * 1.025, f'{median:.0f}', horizontalalignment='center', color='black', fontsize = 18)


        # Map median values to colors
        if type:
            axe = sns.boxplot(x='hour', y=columns[0], hue=type, data=df, width=0.75, ax=axe, showfliers=False, palette=['#d8e219', '#253494'], boxprops=dict(alpha=.7))
            plt.legend(fontsize=22, loc='lower right')
        elif color:
            axe = sns.boxplot(data=df[columns], width=0.5, ax=axe, showfliers=False, palette=color)
        else:
            axe = sns.boxplot(data=df[columns], width=0.5, ax=axe, showfliers=False, color="#a6bddb")


        axe.set_ylim(yrange[0], yrange[1])
        new_ticks = np.arange(yrange[0], yrange[1], yrange[2])  # Generate 4 evenly spaced ticks within the current range
        axe.set_yticks(new_ticks)
        axe.set_ylabel(ylabel, fontsize = 22)
        axe.set_title(plot_title, fontsize = 24)
        if hide_xticks:
            axe.set_xticklabels([])
        axe.set_xlabel(xlabel, fontsize = 22)
        axe.yaxis.grid(True, linestyle='-', color='lightgrey')

        # Create the secondary y-axis for kWh/ft2
        ax2 = axe.twinx()
        ax2.set_yticks(new_ticks)
        secondary_y_tick_labels = [f'{round(y * conversion_factor)}' for y in new_ticks]
        ax2.set_yticklabels(secondary_y_tick_labels)
        ax2.set_ylim(yrange[0], yrange[1])
        ax2.set_ylabel(dual_ylabel, fontsize = 22)

        # General plot settings
        axe.tick_params(axis='y', which = 'major', length=10, width=2, labelsize=22)
        ax2.tick_params(axis='y', which = 'major', length=10, width=2, labelsize=22)
        axe.tick_params(axis='x', labelsize=22)
        ax2.tick_params(axis='x', labelsize=22)

        axe.set_xlabel(xlabel, fontsize=22)

        # Hide unwanted spines
        axe.spines['top'].set_visible(False)
        axe.spines['right'].set_visible(False)
        axe.spines['left'].set_visible(False)
        axe.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        plt.setp(axe.collections, alpha=.5)


    else:
        if annotation == True:
            if type:
                medians = df.groupby([columns + ['type']])[columns].median().reset_index()
                for _, row in medians.iterrows():
                    # Adjust the text position (x, y) and alignment as necessary
                    axe.text(row['hour'] - 0.15 if row['type'] == 'high' else row['hour'] + 0.15, 
                            median * 1.01, 
                            f'{median:.0f}', 
                            horizontalalignment='center', color='black', fontsize = 18)

            else:
                for i, col in enumerate(columns):
                    # Calculate statistics
                    mean = df[col].mean()
                    median = df[col].median()   
                    
                    # Annotate the statistics on the plot
                    axe.text(i, median * 1.025, f'{median:.0f}', horizontalalignment='center', color='black', fontsize = 18)


        # Map median values to colors
        if type:
            sns.boxplot(x='hour', y=columns[0], hue=type, data=df, width=0.75, ax=axe, showfliers=False, palette=['#d8e219', '#253494'], boxprops=dict(alpha=.7))
            plt.legend(fontsize=22, loc='lower right')
        elif color:
            sns.boxplot(data=df[columns], width=0.5, ax=axe, showfliers=False, palette=color)
        else:
            sns.boxplot(data=df[columns], width=0.5, ax=axe, showfliers=False, color="#a6bddb")


        axe.set_ylim(yrange[0], yrange[1])
        new_ticks = np.arange(yrange[0], yrange[1], yrange[2])  # Generate 4 evenly spaced ticks within the current range
        axe.set_yticks(new_ticks)

        axe.set_ylabel(ylabel, fontsize = 22)
        axe.set_title(plot_title, fontsize = 24)
        if hide_xticks:
            axe.set_xticklabels([])
        axe.set_xlabel(xlabel, fontsize = 22)
        axe.tick_params(axis='y', which = 'major', length=10, width=2, labelsize=22)
        axe.tick_params(axis='x', labelsize=22)

        axe.spines['top'].set_visible(False)
        axe.spines['right'].set_visible(False)
        axe.spines['left'].set_visible(False)
        axe.spines['bottom'].set_visible(False)

def create_bar_plot(df, 
                    columns, 
                    plot_title='', 
                    annotation = True, 
                    xlabel = '', 
                    ylabel = '',
                    yrange = [], 
                    dual_columns = [], 
                    dual_ylabel = '', 
                    figsize = (), 
                    color = [], 
                    conversion_factor = 1):

    if dual_columns:

        # Create the primary y-axis for the bar plot
        if color:
            axe = df[columns].plot(kind='bar', figsize=figsize, color=color)
        else:
            axe = df[columns].plot(kind='bar', figsize=figsize)

        # Adjust y-tick labels for primary y-axis
        new_ticks = np.arange(yrange[0], yrange[1], yrange[2])  # Ensure max value is included
        axe.set_yticks(new_ticks)
        plt.xticks(rotation=0)  # Set x-ticks if df.index is not numeric
        axe.set_ylim(yrange[0], yrange[1])

        # Annotate the primary bars with values
        if annotation:
            for i, anno in enumerate(df[columns]):
                    
                    # Annotate the statistics on the plot
                    plt.text(i, anno * 1.025, f'{anno:.0f}', horizontalalignment='center', color='black', fontsize = 22)

        # Create the secondary y-axis for kWh/ft2
        ax2 = axe.twinx()
        ax2.set_yticks(new_ticks)
        secondary_y_tick_labels = [f'{round(y * conversion_factor)}' for y in new_ticks]
        ax2.set_yticklabels(secondary_y_tick_labels)
        ax2.set_ylim(yrange[0], yrange[1])
        ax2.set_ylabel(dual_ylabel, fontsize = 22)

        # General plot settings
        axe.tick_params(axis='y', which = 'major', length=10, width=2, labelsize=22)
        ax2.tick_params(axis='y', which = 'major', length=10, width=2, labelsize=22)
        axe.tick_params(axis='x', labelsize=22)
        ax2.tick_params(axis='x', labelsize=22)

        axe.set_xlabel(xlabel, fontsize=22)
        axe.set_title(plot_title, fontsize=22)
        axe.set_ylabel(ylabel, fontsize = 22)

        # Hide unwanted spines
        axe.spines['top'].set_visible(False)
        axe.spines['right'].set_visible(False)
        axe.spines['left'].set_visible(False)
        axe.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)

        axe.yaxis.grid(True, linestyle='-', color='lightgrey')

        # Show the plot
        plt.show()

    else:
        if color:
            axe = df[columns].plot(kind='bar', figsize=figsize, color=color)
        else:
            axe = df[columns].plot(kind='bar', figsize=figsize)
        # Add units to y-tick labels
        new_ticks = np.arange(yrange[0], yrange[1], yrange[2])  # Adjust the step value as needed
        axe.set_yticks(new_ticks)
        axe.set_ylabel(ylabel, fontsize = 22)
        axe.tick_params(axis='y', which = 'major', length=10, width=2, labelsize=22)
        axe.tick_params(axis='x', which = 'major', labelsize=22)
        plt.xticks(rotation = 0)
        plt.xlabel(xlabel, fontsize = 22)
        plt.title(plot_title, fontsize = 24)
        if annotation:
            for i, anno in enumerate(df[columns]):
                    
                    # Annotate the statistics on the plot
                    plt.text(i, anno * 1.025, f'{anno:.0f}', horizontalalignment='center', color='black', fontsize = 22)

        axe.spines['top'].set_visible(False)
        axe.spines['right'].set_visible(False)
        axe.spines['left'].set_visible(False)
        axe.spines['bottom'].set_visible(False)
        axe.yaxis.grid(True, linestyle='-', color='lightgrey')
        plt.show()