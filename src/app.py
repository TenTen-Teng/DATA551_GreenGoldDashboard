import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import altair as alt
import dash_bootstrap_components as dbc

from data_process import crops_line_dataset


"""Bottom section of the dashboard including 3 grpahs (each takes 3 columns in 
a bootstrap row)
)"""

# Load crop data.
crop_data = crops_line_dataset()

# Mapping column names to value names.
value_types = {
    'production_value': 'Production value',
    'price': 'Price',
    'yield': 'Yield', 
    'production_volume': 'Production volume', 
    'harvested': 'Harvested', 
    'damaged': 'Damaged',
    'sown': 'Sown'
}

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        # Graph 1: line plot with multiple crops.
                        dcc.Dropdown(
                                id='ycol-crop-line-widget',
                                value='production_value',
                                options=[
                                    {
                                        'label': name, 'value': col
                                        } for col, name in value_types.items()
                                ]
                            ),
                        html.Iframe(
                                id='crop_line',
                                style={
                                    'border-width': '0',
                                    'width': '100%',
                                    'height': '400px'
                                    },
                            )
                    ],
                    md=4,
                    style={
                        'border': '1px solid #d3d3d3',
                        'border-radius': '10px'
                        }
                ),
                dbc.Col(
                    # Graph 2: line chart of gini trend over time between 
                    # avocado-growing and non-avocado-growing municipalities. 
                ),
                dbc.Col(
                    # Graph 3: bar chart of wage, biabia #TODO
                )
            ]
        )
    ]
)

@app.callback(
    Output('crop_line', 'srcDoc'),
    Input('ycol-crop-line-widget', 'value')
)
def plot_crop_value_lines(ycol):
    """Plot line chart for 3 different crops: 
    blueburry - Arándano;
    corn - Maíz grano;
    acovodo - Aguacate

    Args:
        ycol (str): The value, such as production value, yield, etc.

    Returns:
        Altair plot: The altair chart.
    """

    line = alt.Chart(crop_data).transform_filter(
        {
            'field': 'name_unitmes',
            'oneOf': ['Arándano', 'Maíz grano', 'Aguacate']
            }
    ).mark_line().encode(
        x=alt.X('year:N', title='Year'),
        y=alt.Y(
            f'{ycol}:Q',
            title=f'{value_types[ycol]} (Michoacán)',
            axis=alt.Axis(format='$s')
            ),
        color=alt.Color('name_unitmes:N')
    ).interactive()

    return line.to_html()

if __name__ == '__main__':
    app.run_server(debug=True)