"""Process data for altair graphs"""
import pandas as pd

def crops_line_dataset():
    """Load agricultural dataset

    Returns:
        DataFrame: Grouped dataset by year and crop type.
    """
    df_ag = pd.read_csv("../data/agricultural_clean.csv", index_col=0)

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
    df_gini = pd.read_csv("../data/gini_mun_month_clean.csv", index_col=0)

    df_gini['date'] = pd.to_datetime(df_gini['date'])
    df_gini['date'] = df_gini['date'].dt.strftime('%Y-%m')
    gini_group = df_gini.drop(
        columns=['year', 'cve', 'mun_name']
        ).groupby(by=['trat_2', 'date'])

    data = gini_group.aggregate('mean').reset_index()[
        [
        'gini', 'date', 'trat_2'
        ]
    ]

    return data