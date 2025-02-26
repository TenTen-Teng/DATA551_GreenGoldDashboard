import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import altair as alt
import dash_bootstrap_components as dbc

from data_process import crops_line_dataset, gini_line_dataset, wage_dataset


"""Bottom section of the dashboard including 3 grpahs (each takes 3 columns in 
a bootstrap row)
)"""

# Load crop data.
crop_data = crops_line_dataset()
gini_data = gini_line_dataset()
wage_data = wage_dataset()

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

# crop lines.
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
            'oneOf': ['Blueburry', 'Corn', 'Acovodo']
            }
    ).mark_line().encode(
        x=alt.X('year:N', title=None),
        y=alt.Y(
            f'{ycol}:Q',
            title=f'{value_types[ycol]} (Michoacán)',
            axis=alt.Axis(format='$s')
            ),
        color=alt.Color(
            'name_unitmes:N',
            title="Crops",
            legend=alt.Legend(
                titleFontSize=15, labelFontSize=15,
                orient='top-left',
                labelLimit=0
                )
            )
    ).interactive().properties(
        width=350,
        height=410,
        title=alt.Title(
            text=f"{value_types[ycol]} for Different Crops",
            fontSize=20,
            anchor='middle'
        )
    )

    return line.to_html()

# Gini lines.
def plot_gini_value_lines():
    """Plot line chart for gini between treatment groups and non-treatment 
    groups over years.

    Returns:
        Altair plot: The altair chart.
    """

    base = alt.Chart(gini_data).mark_line().encode(
        x=alt.X('date:T', title=None),
        y=alt.Y('gini:Q', title="Gini Coefficients"),
        color=alt.Color(
            'trat_2:N',
            title="Treatment groups",
            # legend=alt.Legend(
            #     titleFontSize=15, labelFontSize=15,
            #     orient='bottom',
            #     )
            legend=None
            )
    )

    brush = alt.selection_interval(encodings=['x'])
    lower = base.properties(height=60, width=330).add_params(brush)

    upper = base.encode(
        alt.X('date:T', title=None, scale=alt.Scale(domain=brush))
    ).properties(
        width=330,
        height=300,
        title=alt.Title(
            text="Gini Coeffeicents",
            # subtitle="avocado-growing vs. non-avocado-growing municipalities",
            # subtitleFontSize=15,
            fontSize=20,
            anchor='middle'
        )
    )

    return (upper & lower).to_html()

# Wage bar.
@app.callback(
    Output('wage-bar', 'srcDoc'),
    Input('col-wage-bar-widget', 'value')
)
def plot_wage_bars(year):
    click = alt.selection_point(fields=['trat'], bind='legend')

    bar = alt.Chart(wage_data).mark_bar(opacity=0.7).transform_filter(
        f"datum.year == {year}"
    ).transform_joinaggregate(
        Total='sum(value)',
    ).transform_calculate(
        PercentOfTotal="datum.value / datum.Total"
    ).encode(
        x=alt.X('rs_group:N', title='Wage Levels'),
        y=alt.Y(
            'PercentOfTotal:Q', 
            title="Percentage of total", 
            axis=alt.Axis(format='.0%'),
            ),
        color=alt.Color(
            'trat:N',
            title="Treatment groups",
            legend=alt.Legend(
                titleFontSize=15, labelFontSize=15,
                orient='top-right',
                labelLimit=0
                )
            ),
        opacity=alt.condition(click, alt.value(0.9), alt.value(0.2))
    ).add_params(click).properties(
        width=350,
        height=420,
        title=alt.Title(
            text="Wage Levels",
            # subtitle="avocado-growing vs. non-avocado-growing municipalities",
            # subtitleFontSize=15,
            fontSize=20,
            anchor='middle'
        )
    )

    return bar.to_html()

app.layout = dbc.Container(
    [

        dbc.Row(
            [
                dbc.Col(
                    [
                        # Graph 1: line plot with multiple crops.
                        html.Iframe(
                                id='crop_line',
                                style={
                                    'border-width': '0',
                                    'width': '100%',
                                    'height': '500px'
                                    },
                            ),
                        dcc.Dropdown(
                                id='ycol-crop-line-widget',
                                value='production_value',
                                options=[
                                    {
                                        'label': name, 'value': col
                                        } for col, name in value_types.items()
                                ]
                            ),
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
                    html.Iframe(
                            id='gini_line',
                            style={
                                'border-width': '0',
                                'width': '100%',
                                'height': '500px'
                                },
                            srcDoc=plot_gini_value_lines()
                        ),
                                        md=4,
                    style={
                        'border': '1px solid #d3d3d3',
                        'border-radius': '10px'
                        }
                ),
                dbc.Col(
                    # Graph 3: bar chart of wage, precentage of wage levels for
                    # selected year in treatment group and non-treatment group.
                    [

                        html.Iframe(
                                id='wage-bar',
                                style={
                                    'border-width': '0',
                                    'width': '100%',
                                    'height': '500px'
                                    },
                            ),
                        dcc.Dropdown(
                                id='col-wage-bar-widget',
                                value=2011,
                                options=[
                                    {'label': yr, 'value': yr} for yr in \
                                        wage_data['year'].unique().tolist()
                                ]
                            ),
                    ],
                    md=4,
                    style={
                        'border': '1px solid #d3d3d3',
                        'border-radius': '10px'
                        }
                )
            ]
        )
    ]
)


if __name__ == '__main__':
    app.run_server(debug=True)