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