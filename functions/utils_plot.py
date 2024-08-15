import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator

def make_plot(df, 
              axe, 
              columns = [], 
              date = '',
              tz = '', 
              yrange = [], 
              plot_title = '', 
              color = [], 
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

        if date:
            df = df[df['datetime'].dt.date == pd.to_datetime(date)]
            axe.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 6), tz = tz))
            axe.xaxis.set_major_formatter(mdates.DateFormatter('%-I %p', tz = tz))

        if color:
            for idx, column in enumerate(columns):
                axe.plot(df['datetime'], df[column], lw = 4, color=color[idx], label = legend[idx])
        else:
            for idx, column in enumerate(columns):
                axe.plot(df['datetime'], df[column], lw = 4, label = legend[idx])

        axe.set_ylim(yrange[0], yrange[1])
        new_ticks = np.arange(yrange[0], yrange[1], yrange[2])
        axe.set_yticks(new_ticks)
        axe.set_ylabel(ylabel, fontsize = 22)   
        
        # set dual column
        ax2 = axe.twinx()
        ax2.set_yticks(new_ticks)

        if dual_columns != "temp":
            secondary_y_tick_labels = [f'{round(y * conversion_factor)}' for y in new_ticks]    
        else:
            secondary_y_tick_labels = [f'{round(y * 9/5 + 32)}' for y in new_ticks]
 
        ax2.set_yticklabels(secondary_y_tick_labels)
        ax2.set_ylim(yrange[0], yrange[1])
        ax2.set_ylabel(dual_ylabel, fontsize = 22)
        
        ax2.tick_params(axis='y', which = 'major', length=10, width=2, labelsize=22)
        ax2.tick_params(axis='x', labelsize=22)

        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        
    else:

        if columns == []:
            columns = df.columns[1:]

        if date:
            df = df[df['datetime'].dt.date == pd.to_datetime(date)]
            axe.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 6), tz = tz))
            axe.xaxis.set_major_formatter(mdates.DateFormatter('%-I %p', tz = tz)) 

        if color:
            for idx, column in enumerate(columns):
                axe.plot(df['datetime'], df[column], lw = 4, color=color[idx], label = legend[idx])
        else:
            for idx, column in enumerate(columns):
                axe.plot(df['datetime'], df[column], lw = 4, label = legend[idx])

        new_ticks = np.arange(yrange[0], yrange[1], yrange[2]) 
        axe.set_yticks(new_ticks)
        axe.set_ylabel(ylabel, fontsize=22)
    
    axe.set_xlabel(xlabel, fontsize=22)

    axe.set_title(plot_title, fontsize = 24)
    axe.legend(fontsize=18, loc='best', frameon=False)
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
    
    df['datetime'] = pd.to_datetime(df['datetime']) 
    df.set_index('datetime', inplace=True)
    
    hourly_data = df[columns].resample('H').mean()
    
    heatmap_data = hourly_data.pivot_table(index=hourly_data.index.date, 
                                           columns=hourly_data.index.hour, 
                                           values=columns, 
                                           aggfunc='mean')

    plt.figure(figsize=figsize)
    heatmap = sns.heatmap(heatmap_data, cmap='viridis_r', linewidths=0, cbar_kws={'orientation': 'horizontal', 'pad': 0.1, 'shrink': 0.75})

    cbar = heatmap.collections[0].colorbar
    cbar.set_label(annotation, labelpad=-75, fontsize=22)
    cbar.ax.tick_params(labelsize=22)

    if cbar_ticks:
        cbar.set_ticks(cbar_ticks) 
        cbar.set_ticklabels(cbar_label) 

    month_positions = []
    month_labels = []
    for i, date_str in enumerate(heatmap_data.index):
        date = pd.to_datetime(date_str)
        if date.day == 1: 
            month_positions.append(i)
            month_labels.append(date.strftime('%b'))

    heatmap.set_yticks(np.array(month_positions) + 0.5)
    heatmap.set_yticklabels(month_labels, rotation=0)

    hours = ['12 AM', '6 AM', '12 PM', '6 PM', "12 AM"]
    hour_positions = [0, 6, 12, 18, 24]
    plt.xticks(hour_positions, labels=hours, rotation = 0)
    plt.title(plot_title, fontsize=24)
    plt.xticks(fontsize=22)
    plt.yticks(fontsize=22)
    plt.xlabel(xlabel=None)
    plt.show()
    df.reset_index(inplace = True)


def create_box_plot(df, 
                    columns, 
                    axe, 
                    plot_title='', 
                    annotation = True, 
                    xlabel = '', 
                    ylabel = '',
                    yrange = [], 
                    reduce_xlabel = False, 
                    color = [], 
                    type = False, 
                    dual_columns = [], 
                    dual_ylabel = '', 
                    conversion_factor = 1):

    if dual_columns:
        if annotation == True:
            if type:
                medians = df.groupby([columns + ['type']])[columns].median().reset_index()
                for _, row in medians.iterrows():
                    axe.text(row['hour'] - 0.15 if row['type'] == 'high' else row['hour'] + 0.15, 
                            median * 1.01, 
                            f'{median:.0f}', 
                            horizontalalignment='center', size='large', color='black', fontsize = 18)

            else:
                for i, col in enumerate(columns):
                    median = df[col].median()   
                    axe.text(i, median * 1.02, f'{median:.0f}', horizontalalignment='center', color='black', fontsize = 18)

        if type:
            axe = sns.boxplot(x='hour', y=columns[0], hue=type, data=df, width=0.75, ax=axe, showfliers=False, palette=['#d8e219', '#253494'], boxprops=dict(alpha=.7))
            plt.legend(fontsize=22, loc='best', frameon=False)
        elif color:
            axe = sns.boxplot(data=df[columns], width=0.5, ax=axe, showfliers=False, palette=color)
        else:
            axe = sns.boxplot(data=df[columns], width=0.5, ax=axe, showfliers=False, color="#a6bddb")


        axe.set_ylim(yrange[0], yrange[1])
        new_ticks = np.arange(yrange[0], yrange[1], yrange[2]) 
        axe.set_yticks(new_ticks)
        axe.set_ylabel(ylabel, fontsize = 22)

        ax2 = axe.twinx()
        ax2.set_yticks(new_ticks)
        secondary_y_tick_labels = [f'{round(y * conversion_factor)}' for y in new_ticks]
        ax2.set_yticklabels(secondary_y_tick_labels)
        ax2.set_ylim(yrange[0], yrange[1])
        ax2.set_ylabel(dual_ylabel, fontsize = 22)

        ax2.tick_params(axis='y', which = 'major', length=10, width=2, labelsize=22)
        ax2.tick_params(axis='x', labelsize=22)

        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)


    else:
        if annotation == True:
            if type:
                medians = df.groupby([columns + ['type']])[columns].median().reset_index()
                for _, row in medians.iterrows():
                    axe.text(row['hour'] - 0.15 if row['type'] == 'high' else row['hour'] + 0.15, 
                            median * 1.01, 
                            f'{median:.0f}', 
                            horizontalalignment='center', color='black', fontsize = 18)

            else:
                for i, col in enumerate(columns):
                    median = df[col].median()   
                    axe.text(i, median * 1.02, f'{median:.0f}', horizontalalignment='center', color='black', fontsize = 18)

        if type:
            sns.boxplot(x='hour', y=columns[0], hue=type, data=df, width=0.75, ax=axe, showfliers=False, palette=['#d8e219', '#253494'], boxprops=dict(alpha=.7))
            plt.legend(fontsize=22, loc='best', frameon=False)
        elif color:
            sns.boxplot(data=df[columns], width=0.5, ax=axe, showfliers=False, palette=color)
        else:
            sns.boxplot(data=df[columns], width=0.5, ax=axe, showfliers=False, color="#a6bddb")


        axe.set_ylim(yrange[0], yrange[1])
        new_ticks = np.arange(yrange[0], yrange[1], yrange[2])
        axe.set_yticks(new_ticks)
        axe.set_ylabel(ylabel, fontsize = 22)

    axe.tick_params(axis='y', which = 'major', length=10, width=2, labelsize=22)
    axe.tick_params(axis='x', labelsize=22)

    axe.spines['top'].set_visible(False)
    axe.spines['right'].set_visible(False)
    axe.spines['left'].set_visible(False)
    axe.spines['bottom'].set_visible(False)

    axe.set_title(plot_title, fontsize = 24)
    axe.yaxis.grid(True, linestyle='-', color='lightgrey')
    if reduce_xlabel:
        axe.xaxis.set_major_locator(MultipleLocator(6))
    axe.set_xlabel(xlabel, fontsize=22)
        

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

        if color:
            axe = df[columns].plot(kind='bar', figsize=figsize, color=color, width = 0.8)
        else:
            axe = df[columns].plot(kind='bar', figsize=figsize, width = 0.8)

        new_ticks = np.arange(yrange[0], yrange[1], yrange[2])
        axe.set_yticks(new_ticks)
        axe.set_ylim(yrange[0], yrange[1])
        plt.xticks(rotation=0) 

        if annotation:
            for i, anno in enumerate(df[columns]):
                    plt.text(i, anno * 1.02, f'{anno:.0f}', horizontalalignment='center', color='black', fontsize = 18)

        ax2 = axe.twinx()
        ax2.set_yticks(new_ticks)
        secondary_y_tick_labels = [f'{round(y * conversion_factor)}' for y in new_ticks]
        ax2.set_yticklabels(secondary_y_tick_labels)
        ax2.set_ylim(yrange[0], yrange[1])
        ax2.set_ylabel(dual_ylabel, fontsize = 22)

        ax2.tick_params(axis='y', which = 'major', length=10, width=2, labelsize=22)
        ax2.tick_params(axis='x', labelsize=22)

        axe.set_ylabel(ylabel, fontsize = 22)

        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)

    else:
        if color:
            axe = df[columns].plot(kind='bar', figsize=figsize, color=color, width = 0.8)
        else:
            axe = df[columns].plot(kind='bar', figsize=figsize, width = 0.8)
        new_ticks = np.arange(yrange[0], yrange[1], yrange[2]) 
        plt.xticks(rotation=0)
        axe.set_yticks(new_ticks)
        axe.set_ylabel(ylabel, fontsize = 22)
        if annotation:
            for i, anno in enumerate(df[columns]):
                    plt.text(i, anno * 1.02, f'{anno:.0f}', horizontalalignment='center', color='black', fontsize = 18)

    axe.yaxis.grid(True, linestyle='-', color='lightgrey')
    axe.tick_params(axis='y', which = 'major', length=10, width=2, labelsize=22)
    axe.tick_params(axis='x', which = 'major', labelsize=22)
    axe.set_xlabel(xlabel, fontsize=22)
    axe.set_title(plot_title, fontsize=22, pad=20)
    axe.spines['top'].set_visible(False)
    axe.spines['right'].set_visible(False)
    axe.spines['left'].set_visible(False)
    axe.spines['bottom'].set_visible(False)
    plt.show()