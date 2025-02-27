"""Process data for altair graphs"""
from pathlib import Path
import os
import geopandas as gpd
from unidecode import unidecode
import pandas as pd

# Build CSV paths.
# absolute path to the root of the repository
repo_root = Path(__file__).resolve().parent

# search for the root of the repository
while repo_root.name != "DATA551_GreenGoldDashboard" and repo_root.parent != repo_root:
    repo_root = repo_root.parent

# build the path to the data file
data_path_gini = os.path.join(repo_root, 'data', 'gini_mun_month_clean.csv')
data_path_ag = os.path.join(repo_root, 'data', 'agricultural_clean.csv')
data_path_wage = os.path.join(repo_root, 'data', 'imss_minimumwages.csv')

data_path_shapefile = os.path.join(
    repo_root, "data", "shapefiles_mich", "16mun.shp"
    )

def number_card_dataset():
    df = pd.read_csv(data_path_gini)

    # Aggregate and sort Gini data by municipality
    df_agg = df.groupby(
        ["year", "mun_name"]
        )["gini"].mean().reset_index().sort_values(by="mun_name")
    
    return df_agg

def map_dataset():
    # 1. Load and preprocess Gini data 
    gini = pd.read_csv(data_path_gini)

    #gini['trat_1'] = gini.groupby('mun_name')['trat_2'].transform('max')
    gini_anual = gini.groupby(
        ['mun_name', 'year'], as_index=False
        )['gini'].mean()
    tratamiento = gini[['mun_name', 'trat_2']].drop_duplicates()
    gini_anual = pd.merge(gini_anual, tratamiento, on='mun_name', how='left')

    # 2. Load and prepare shapefile 
    mich = gpd.read_file(data_path_shapefile)

    def _limpiar_nombres(nombre):
        nombre = unidecode(nombre).replace(' de Vazquez Pallares', '').replace(' de Nicolas Romero', '')
        return nombre.strip()
    
    mich['mun_name'] = mich['NOMGEO'].apply(_limpiar_nombres)
    mich = mich.to_crs(epsg=4326)
    mich_projected = mich.to_crs(epsg=3857)
    center_projected = mich_projected.geometry.union_all().centroid
    center = gpd.GeoSeries([center_projected], crs="EPSG:3857").to_crs(epsg=4326).iloc[0]
    # center_lon, center_lat = center.x, center.y
    # minx, miny, maxx, maxy = mich.total_bounds
    # bounds = dict(west=minx, south=miny, east=maxx, north=maxy)
    # base_geojson = json.loads(mich.to_json())

    df_full = gini_anual.drop_duplicates(subset=['mun_name', 'year'])
    return df_full, center, mich


def map_treatment_groups(name):
    if name == 0:
        return 'Avocado Municipalituy'
    else:
        return 'Non-avocado Municipality'


def crops_line_dataset():
    """Load agricultural dataset

    Returns:
        DataFrame: Grouped dataset by year and crop type.
    """
    def _map_crop(name):
        if name == 'Arándano':
            return 'Blueburry'
        elif name == 'Maíz grano':
            return 'Corn'
        elif name == 'Aguacate':
            return 'Acovodo'
        else:
            return name

    df_ag = pd.read_csv(data_path_ag, index_col=0)
    df_ag['name_unitmes'] = df_ag['name_unitmes'].apply(lambda x: _map_crop(x))

    ag_group = df_ag.groupby(by=['name_unitmes', 'year'])

    data = ag_group.aggregate('sum').reset_index()[
        [
            'name_unitmes', 'year', 'production_value', 'price', 'yield', 
            'production_volume', 'harvested', 'damaged','sown'
        ]
    ]

    return data

def gini_line_dataset():
    """Load gini dataset

    Return:
        DataFrame: Grouped dataset by treatment groups, cities, and city codes. 
    """
    df_gini = pd.read_csv(data_path_gini, index_col=0)


    df_gini['date'] = pd.to_datetime(df_gini['date'])
    df_gini['date'] = df_gini['date'].dt.strftime('%Y-%m')
    df_gini['trat_2'] = df_gini['trat_2'].apply(lambda x: map_treatment_groups(x))

    gini_group = df_gini.drop(
        columns=['year', 'cve', 'mun_name']
        ).groupby(by=['trat_2', 'date'])

    data = gini_group.aggregate('mean').reset_index()[
        [
        'gini', 'date', 'trat_2'
        ]
    ]

    return data

def wage_dataset():
    """Load gini dataset.

    Return:
        DataFrame: Grouped dataset by wage level groups, treatment groups, and
        year.
        The wage levels are split into 5 groups (rs_w1 - 5, rs_w6 - 10, 
        rs_w11 - 15, rs_w16 - 20, rs_w21 - 25)
    """

    def _map_wage_level(level):
        if len(level) == 5:
            lvl = int(level[-1]) // 5
        else:
            lvl = int(level[-2:]) // 5
        return lvl
    
    df_wage = pd.read_csv(data_path_wage, index_col=0)

    df_wage['trat'] = df_wage['trat'].apply(lambda x: map_treatment_groups(x))
    df_wage['rs_group'] = df_wage['rs'].apply(lambda x: _map_wage_level(x))

    wage_group = df_wage.drop(
        columns=['mun', 'pto', 'q_minwages', 'rs']
        ).groupby(
            by=['rs_group', 'trat', 'year']
        )
    data = wage_group.aggregate('sum').reset_index()
    return data