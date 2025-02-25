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

    df_wage = pd.read_csv("../data/imss_minimumwages.csv", index_col=0)

    df_wage['rs_group'] = df_wage['rs'].apply(lambda x: _map_wage_level(x))

    wage_group = df_wage.drop(
        columns=['mun', 'pto', 'q_minwages', 'rs']
        ).groupby(
            by=['rs_group', 'trat', 'year']
        )
    data = wage_group.aggregate('sum').reset_index()
    return data