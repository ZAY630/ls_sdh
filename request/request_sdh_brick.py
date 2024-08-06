import brickschema
from tqdm import tqdm
from smap.archiver.client import SmapClient
from smap.contrib import dtutil
import pandas as pd

def get_paths_from_tags(tags):
    paths = {key: tags[key]["Path"] for key in tags}
    paths = pd.DataFrame.from_dict(paths, orient='index', columns=['path'])
    new_cols = ["empty", "site", "device_number", "point_name", "bacnet_instance", "property_name"]

    # adjustments to dataframe
    paths[new_cols] = paths.path.str.split("/", expand=True)
    paths = paths.drop(columns=["empty"])
    paths['point_name'] = paths['point_name'].str.replace('SDH.', '', regex=False)
    paths['point_name'] = paths['point_name'].str.replace('[^a-zA-Z0-9]', '_', regex=True)
    return paths

def get_data_from_smap(points_to_download, paths, smap_client, start, end):
    df_combine = pd.merge(paths.reset_index(), points_to_download, how='inner', on=['bacnet_instance', 'point_name'])
    df_combine = df_combine[df_combine['property_name'] == 'presentValue']

    # combine the data frames

    # get data from smap
    data = smap_client.data_uuid(df_combine["index"], start, end, cache=False)
    return df_combine, data

def clean_df(data, points_to_download, query):
    df_datetime = pd.DataFrame(data[0][:, 0], columns=['datetime'])

    # Iterate over data and uuid to extract values and create separate DataFrames, then concatenate them
    df_values = pd.concat([pd.DataFrame(data[i][:, 1], columns=[points_to_download['point_name'].values[i]]) for i in range(0, len(points_to_download))], axis=1)

    # Combine datetime and values DataFrames
    df_merge = pd.concat([df_datetime, df_values], axis=1)
    
    df_merge['datetime'] = pd.to_datetime(df_merge.iloc[:, 0], unit='ms', utc=True).dt.tz_convert('US/Pacific').dt.tz_localize(None)
    df_merge.set_index('datetime', inplace=True)
    df_merge = df_merge.resample('15T').mean()
    df_merge = df_merge.reset_index()

    # Save DataFrame to a CSV file
    df_merge.to_csv('../readfiles/ls_ctr/{}'.format(query), index=False)

if __name__ == "__main__":

    start = dtutil.dt2ts(dtutil.strptime_tz("2023-01-01", "%Y-%m-%d"))
    end = dtutil.dt2ts(dtutil.strptime_tz("2024-01-01", "%Y-%m-%d"))
    query_type = "fan_energy"
    g = brickschema.Graph()
    g.load_file('2022_sdh_brick_expanded.ttl')
    url = "http://178.128.64.40:8079"
    keyStr = "B7qm4nnyPVZXbSfXo14sBZ5laV7YY5vjO19G"
    where = "Metadata/SourceName = 'Field Study 5a'"

    # Query for zone supply temperature and return temperature
    if query_type == "sat":

        query = g.query(
            """SELECT DISTINCT ?ahu ?sensor ?bacnet_id ?bacnet_instance WHERE {
            ?ahu            rdf:type                        brick:AHU .
            ?sensor         rdf:type/rdfs:subClassOf*       brick:Supply_Air_Temperature_Sensor .
            ?ahu            brick:hasPoint                  ?sensor .
            ?sensor         brick:bacnetPoint               ?bacnet_id .
            ?bacnet_id      brick:hasBacnetDeviceInstance   ?bacnet_instance .
            ?bacnet_id      brick:hasBacnetDeviceType       ?bacnet_type .
            ?bacnet_id      brick:accessedAt                ?bacnet_net .
            ?bacnet_net     sdh:connstring                  ?bacnet_addr .
        }"""
        )
    
    elif query_type == "zoneT":
        
        query = g.query(
            """SELECT DISTINCT ?ahu ?sensor ?bacnet_instance ?bacnet_id WHERE {
            ?ahu            rdf:type                        brick:AHU .
            ?zone           rdf:type                        brick:HVAC_Zone .
            ?sensor         rdf:type/rdfs:subClassOf*       brick:Zone_Air_Temperature_Sensor .
            ?ahu            brick:feeds                     ?vav .
            ?vav            rdf:type                        brick:VAV .
            ?vav            brick:feeds                     ?zone .
            ?zone           brick:hasPoint                  ?sensor .
            ?sensor         brick:bacnetPoint               ?bacnet_id .
            ?bacnet_id      brick:hasBacnetDeviceInstance   ?bacnet_instance .
            ?bacnet_id      brick:hasBacnetDeviceType       ?bacnet_type .
            ?bacnet_id      brick:accessedAt                ?bacnet_net .
            ?bacnet_net     sdh:connstring                  ?bacnet_addr .
        }"""
        )

    elif query_type == "afr":

        query = g.query(
            """SELECT DISTINCT ?ahu ?sensor ?bacnet_id ?bacnet_instance WHERE {
            ?ahu            rdf:type                        brick:AHU .
            ?sensor         rdf:type/rdfs:subClassOf*       brick:Supply_Air_Flow_Sensor .
            ?ahu            brick:hasPoint                  ?sensor .
            ?sensor         brick:bacnetPoint               ?bacnet_id .
            ?bacnet_id      brick:hasBacnetDeviceInstance   ?bacnet_instance .
            ?bacnet_id      brick:hasBacnetDeviceType       ?bacnet_type .
            ?bacnet_id      brick:accessedAt                ?bacnet_net .
            ?bacnet_net     sdh:connstring                  ?bacnet_addr .
        }"""
        )

    elif query_type == "fan_energy":

        query = g.query(
            """SELECT DISTINCT ?ahu ?sensor ?bacnet_id ?bacnet_instance WHERE {
            ?ahu            rdf:type                        brick:AHU .
            ?sensor         rdf:type/rdfs:subClassOf*       brick:Demand_Sensor .
            ?ahu            brick:hasPoint                  ?sensor .
            ?sensor         brick:bacnetPoint               ?bacnet_id .
            ?bacnet_id      brick:hasBacnetDeviceInstance   ?bacnet_instance .
            ?bacnet_id      brick:hasBacnetDeviceType       ?bacnet_type .
            ?bacnet_id      brick:accessedAt                ?bacnet_net .
            ?bacnet_net     sdh:connstring                  ?bacnet_addr .
        }"""
        )
    

    print("Return {} queries".format(len(query)))
    df = pd.DataFrame(query, columns=[str(s) for s in query.vars])
    point_name = []
    for i in range(len(df)):
        point_name.append(df.sensor.str.split("/", expand=False)[i][4].split("#")[1])
    df['point_name'] = point_name
    df["bacnet_instance"] = df["bacnet_instance"].astype(int).astype(str)
    df['point_name'] = df['point_name'].str.replace('[^a-zA-Z0-9]', '_', regex=True)
    smap_client = SmapClient(url, key=keyStr)
    # import pdb; pdb.set_trace()
    tags = smap_client.tags(where, asdict=True)
    paths = get_paths_from_tags(tags)
    points_to_download, data = get_data_from_smap(df, paths, smap_client, start, end)
    print("Return {} data sources".format(len(data)))
    clean_df(data, points_to_download, '{}.csv'.format(query_type))