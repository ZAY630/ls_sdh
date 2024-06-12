"""
Retreive data from the sMap database

Carlos Duarte <cduarte@berkeley.edu>
"""
from os.path import join

import pandas as pd
import numpy as np
import sys, re
sys.path.append("/mnt/c/Users/duar3/Documents/github/smap/python")
sys.path.append("/mnt/c/Users/duar3/Documents/github/smap/python/smap")

from smap.archiver.client import SmapClient
from smap.contrib import dtutil

# create plots
from bokeh.palettes import Spectral8, Category20
from bokeh.io import show, save, output_file
from bokeh.layouts import column
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, RangeTool, LinearAxis, Range1d, BoxAnnotation, Legend


def get_paths_from_tags(tags):
    paths = {key: tags[key]["Path"] for key in tags}
    paths = pd.DataFrame.from_dict(paths, orient='index', columns=['path'])
    new_cols = ["empty", "site", "device_number", "point_name", "bacnet_instance", "property_name"]

    # adjustments to dataframe
    paths[new_cols] = paths.path.str.split("/", expand=True)
    paths = paths.drop(columns=["empty"])

    return paths

def add_columns_to_df_paths(paths, tags, info_tuples):
    """
    Add more columns to the path dataframe by specifying the keywords of
    the nested dictionary found in tags. Format name as a tuple starting
    with the preferred column name e.g. (<col_name>, 'Metadata', 'Extra', 'Description')
    """
    for cur_tuple in info_tuples:
        col_values = []
        col_name = cur_tuple[0]
        kwords = cur_tuple[1:]
        for point_id in paths.index:
            cur_info = tags[point_id]
            for kword in kwords:
                if kword in cur_info.keys():
                   cur_info = cur_info[kword]
                else:
                    cur_info = np.nan
                    break
            col_values.append(cur_info)
        paths[col_name] = col_values

    return paths


def plot_multiple_entities(data, start, end, filename, df_metadata=None):

        # plot settings
        plt_colors = Category20[20]

        x_range_str_time = pd.to_datetime(start, unit='s', utc=True).tz_convert('US/Pacific').tz_localize(None)
        x_range_end_time = pd.to_datetime(end, unit='s', utc=True).tz_convert('US/Pacific').tz_localize(None)

        x_plot_range = (x_range_str_time, x_range_end_time)

        p = figure(
            plot_height=300, plot_width=1500,
            x_axis_type='datetime', x_axis_location='below',
            x_range=x_plot_range,
            )
        p.add_layout(Legend(), 'right')


        #df_subset = [data[x] for x in in_data_index]

        for i, dd in enumerate(data):
            if df_metadata is not None:
                legend_name = df_metadata.iloc[i]['point_name']
                if 'unit' in df_metadata.columns:
                    legend_name += f" [{df_metadata.iloc[i]['unit']}]"
            else:
                legend_name = ''

            p.step(
                pd.to_datetime(dd[:, 0], unit='ms', utc=True).tz_convert("US/Pacific").tz_localize(None),
                dd[:, 1], legend_label=legend_name,
                color = plt_colors[i % len(plt_colors)], line_width=2,
                mode = 'after'
                )

        p.legend.click_policy = "hide"

        p.legend.label_text_font_size = "6px"
        p.legend.label_height = 5
        p.legend.glyph_height = 5
        p.legend.spacing = 5

        output_file(filename)
        save(p)


def plot_rah_ccv(df):
    """
    plot rah's cooling coil valve positions
    """
    df_present_vals = df.loc[df['property_name'].isin(['presentValue'])]
    df_rahs_bool = df_present_vals['point_name'].str.contains('RAH', flags=re.IGNORECASE, regex=True)
    df_rahs = df_present_vals.loc[df_rahs_bool]

    # get only cooling coil valves
    df_rahs_ccv_bool = df_rahs['point_name'].str.contains('CCV', flags=re.IGNORECASE, regex=True)
    df_rahs_ccv = df_rahs.loc[df_rahs_ccv_bool]

    df_rahs_ccv_data = smap_client.data_uuid(df_rahs_ccv.index, start, end, cache=False)
    plot_multiple_entities(df_rahs_ccv_data, start, end, "RAHs Cooling Coil Valve Position.html", df_metadata=df_rahs_ccv)

    return df_rahs_ccv

def plot_rah_sat(df):
    """
    plot rah's cooling coil valve positions
    """
    df_present_vals = df.loc[df['property_name'].isin(['presentValue'])]
    df_equip_bool = df_present_vals['point_name'].str.contains('RAH', flags=re.IGNORECASE, regex=True)
    df_equip = df_present_vals.loc[df_equip_bool]

    # get only cooling coil valves
    df_equip_sat_bool = df_equip['point_name'].str.contains('SAT', flags=re.IGNORECASE, regex=True)
    df_equip_stp_bool = df_equip['point_name'].str.contains('SAT.STP', flags=re.IGNORECASE, regex=True)
    df_equip_alm_bool = df_equip['point_name'].str.contains('SAT.ALM', flags=re.IGNORECASE, regex=True)
    df_equip_sat = df_equip.loc[(df_equip_sat_bool & ~df_equip_stp_bool & ~df_equip_alm_bool)]

    df_equip_sat_data = smap_client.data_uuid(df_equip_sat.index[:-1], start, end, cache=False)
    plot_multiple_entities(df_equip_sat_data, start, end, "RAH supply air temperature.html", df_metadata=df_equip_sat)

    return df_equip_sat

def get_uuid(file):
    # get uuid from csv files
    df = pd.read_csv(file)
    
    name = df.dropna(subset=['point name'])['point name']
    uuid = df.dropna(subset=['uuid'])['uuid']

    return name, uuid

def download_df(df, name, uuid, parameter, filename):
    # Extract datetime from the first array and create a DataFrame
    df_datetime = pd.DataFrame(df[0][:, 0], columns=['datetime'])

    # Iterate over data and uuid to extract values and create separate DataFrames, then concatenate them
    df_values = pd.concat([pd.DataFrame(df[i][:, 1], columns=[uuid[i]]) for i in range(0, len(uuid))], axis=1)

    # Combine datetime and values DataFrames
    data = pd.concat([df_datetime, df_values], axis=1)

    # Change timezone
    data['datetime'] = pd.to_datetime(data.iloc[:, 0], unit='ms', utc=True).dt.tz_convert('US/Pacific').dt.tz_localize(None)
    data.set_index('datetime', inplace=True)
    data = data.resample('15T').mean()
    data = data.reset_index()

    # Change column name
    data.rename(columns = dict(zip(uuid, name)), inplace = True)

    # Save DataFrame to a CSV file
    data.to_csv('../readfiles/{}/{}'.format(parameter, filename), index=False)


if __name__ == "__main__":
    # database settings
    url = "http://178.128.64.40:8079"
    keyStr = "B7qm4nnyPVZXbSfXo14sBZ5laV7YY5vjO19G"
    where = "Metadata/SourceName = 'Field Study 5a'"

    # set file names
    exp_brick_model_file = "./schema_and_models/2022_sdh_brick_expanded.ttl"

    # set save folder names
    # plot_folder = "./figures"

    # get uuid
    parameter = "sw"
    name, uuid = get_uuid("../{}/smap_points - {}.csv".format(parameter, parameter))

    # time interval for to download data
    start = dtutil.dt2ts(dtutil.strptime_tz("2023-01-01", "%Y-%m-%d"))
    end   = dtutil.dt2ts(dtutil.strptime_tz("2024-01-01", "%Y-%m-%d"))

    # initiate smap client and download tags
    smap_client = SmapClient(url, key=keyStr)
    tags = smap_client.tags(where, asdict=True)

    # retrieve relevant tags from smap database
    paths = get_paths_from_tags(tags)

    # add additional infomation columns to path dataframe
    info_tuples = [('description', 'Metadata', 'Extra', 'Description'), ('unit', 'Properties', 'UnitofMeasure')]
    paths = add_columns_to_df_paths(paths, tags, info_tuples)

    # plot RAHs cooling coil valve positions
    # df_rahs_ccv = plot_rah_ccv(paths)

    # import pdb; pdb.set_trace()

    # data = smap_client.data_uuid(['c83051be-4074-5abf-9a32-1b6b86f1fcbf', '6507fdc4-3f09-529c-b84b-41bdf1fb572e'], start, end, cache=False)
    data = smap_client.data_uuid(uuid, start, end, cache=False)

    download_df(data, name, uuid, parameter, '{}.csv'.format(parameter))

    # import pdb; pdb.set_trace()
    # plot_multiple_entities(data, start, end, "test.html")
    
