import os
from pathlib import Path

import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import altair as alt
import dash_bootstrap_components as dbc
from dash import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd

from .data_process import (
    crops_line_dataset, gini_line_dataset, wage_dataset, map_dataset,
    number_card_dataset
    )
from .helper import calculate_change

# cwd = os.getcwd()

# # absolute path to the root of the repository
repo_root = Path(__file__).resolve().parents[1]

# search for the root of the repository
while repo_root.name != "DATA551_GreenGoldDashboard" and repo_root.parent != repo_root:
    repo_root = repo_root.parent

""">>>>>> Load data <<<<<<"""
'''Numbers data'''
# Prepare dataset.
df_agg = number_card_dataset()
gini_data = df_agg.pivot(
    index="year", columns="mun_name", values="gini"
    ).to_dict()

# Store unique values to avoid redundant calculations
unique_municipalities = sorted(df_agg["mun_name"].unique())
unique_years = sorted(df_agg["year"].unique())

'''Map data'''
# Prepare map data.
df_full, center, mich = map_dataset()
center_lon, center_lat = center.x, center.y
minx, miny, maxx, maxy = mich.total_bounds
bounds = dict(west=minx, south=miny, east=maxx, north=maxy)
base_geojson = json.loads(mich.to_json())
df_tratados = df_full[df_full['trat_2'] == 1].copy()
df_control   = df_full[df_full['trat_2'] == 0].copy()

global_min = df_full['gini'].min()
global_max = df_full['gini'].max()

# years for dropwdown
available_years = sorted(df_full['year'].unique().tolist())

# type of mun
map_type_options = [
    {"label": "Avocado Municipalities", "value": "tratados"},
    {"label": "Non-Avocado Municipalities", "value": "control"},
    {"label": "Both", "value": "both"}
]

'''Table data'''
# Define file paths
file1_path = os.path.join(
    repo_root, 'data', 'tables', 'tabla1_regresiones_mes_gini_mun_ptotrat.html'
    )
file2_path = os.path.join(
    repo_root, 'data', 'tables', 'tabla2_regresion_nivelempleo_year.html'
)

# Read HTML files
with open(file1_path, "r", encoding="utf-8") as file:
    table1_content = file.read()

with open(file2_path, "r", encoding="utf-8") as file:
    table2_content = file.read()

'''Bottom section of the dashboard including 3 grpahs (each takes 3 columns in 
a bootstrap row)
)'''

# Load crop data.
df_crop_data = crops_line_dataset()
df_gini_data = gini_line_dataset()
df_wage_data = wage_dataset()

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

""">>>>>> Callbacks <<<<<<"""
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Number card callback.
@app.callback(
    [
        Output("gini-title", "children"),
        Output("gini-value-1", "children"),
        Output("gini-value-2", "children"),
        Output("change-container", "children"),  # Outputs both arrow and percentage change
    ],
    [
        Input("mun-dropdown", "value"),
        Input("year-dropdown-1", "value"),
        Input("year-dropdown-2", "value")
        ],
)
def update_gini(selected_mun, year1, year2):
    """
    Update Gini coefficient display based on selected municipality and years.

    Args:
        selected_mun (str): Selected municipality.
        year1 (int): First selected year (before 2011).
        year2 (int): Second selected year (after 2011).

    Returns:
        tuple: Updated values for Gini title, two Gini values, and change 
        indicator.
    """

    gini_year1 = gini_data.get(selected_mun, {}).get(year1)
    gini_year2 = gini_data.get(selected_mun, {}).get(year2)
    change = calculate_change(gini_year1, gini_year2)

    if gini_year1 is None or gini_year2 is None:
        arrow, arrow_color, change_display = " ? ", "white", "N/A"
    else:
        arrow, arrow_color = (
            (" ▲ ", "red") if change > 0 else
            (" ▼ ", "green") if change < 0 else
            (" - ", "gray")
        )
        change_display = f"{abs(change):.1f}%"

    # Combine arrow and percentage change into a single display element
    change_output = html.Span(
        [arrow, " ", change_display],
        style={"color": arrow_color, "fontSize": "24px", "fontWeight": "bold"}
    )

    return (
        f"Gini {selected_mun}",
        f"{year1}: {gini_year1:.3f}" if gini_year1 is not None else f"{year1}: N/A",
        f"{year2}: {gini_year2:.3f}" if gini_year2 is not None else f"{year2}: N/A",
        change_output,  # Displays arrow + percentage
    )


# Callback to update the map based on selected year and map type
@app.callback(
    Output('graph-map', 'figure'),
    Input('year-dropdown', 'value'),
    Input('map-type-dropdown', 'value')
)
def update_map(selected_year, map_type):
    if map_type == "tratados":
        df = df_tratados[df_tratados['year'] == selected_year]
        title = f"Avocado Municipalities - {selected_year}"
        fig = px.choropleth_map(
            df,
            geojson=base_geojson,
            locations='mun_name',
            color='gini',
            featureidkey="properties.mun_name",
            color_continuous_scale="Greens",
            range_color=(global_min, global_max),
            center={"lat": center_lat, "lon": center_lon},
            zoom=6,
            opacity=0.5,
            title=title,
            map_style="carto-positron"
        )
        # Hover: mostrar "Municipio" y "Gini" a 3 decimales
        fig.update_traces(hovertemplate="Municipality: %{location}<br>Gini: %{z:.3f}<extra></extra>")
        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                center={"lat": center_lat, "lon": center_lon},
                zoom=6
            ),
            margin={"r":0, "t":40, "l":0, "b":0},
            title=title
        )
    elif map_type == "control":
        df = df_control[df_control['year'] == selected_year]
        title = f"Non-Avocado Municipalities - {selected_year}"
        fig = px.choropleth_map(
            df,
            geojson=base_geojson,
            locations='mun_name',
            color='gini',
            featureidkey="properties.mun_name",
            color_continuous_scale="Reds",
            range_color=(global_min, global_max),
            center={"lat": center_lat, "lon": center_lon},
            zoom=6,
            opacity=0.5,
            title=title,
            map_style="carto-positron"
        )
        fig.update_traces(hovertemplate="Municipality: %{location}<br>Gini: %{z:.3f}<extra></extra>")
        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                center={"lat": center_lat, "lon": center_lon},
                zoom=6
            ),
            margin={"r":0, "t":40, "l":0, "b":0},
            title=title
        )
    else:  # map_type == "both"
        title = f"Avocado and Non-Avocado Municipalities - {selected_year}"
        fig = go.Figure()
        # Avocado Municipalities
        df_trat = df_tratados[df_tratados['year'] == selected_year]
        fig.add_trace(go.Choroplethmap(
            geojson=base_geojson,
            locations=df_trat['mun_name'],
            z=df_trat['gini'],
            colorscale="Greens",
            zmin=global_min,
            zmax=global_max,
            marker_opacity=0.5,
            featureidkey="properties.mun_name",
            name="Avocado Municipalities",
            colorbar=dict(title="Gini", x=0.85),
            hovertemplate="Municipality: %{location}<br>Type: Avocado Municipality<br>Gini: %{z:.3f}<extra></extra>"
        ))
        # Non-Avocado Municipalities
        df_ctrl = df_control[df_control['year'] == selected_year]
        fig.add_trace(go.Choroplethmap(
            geojson=base_geojson,
            locations=df_ctrl['mun_name'],
            z=df_ctrl['gini'],
            colorscale="Reds",
            zmin=global_min,
            zmax=global_max,
            marker_opacity=0.5,
            featureidkey="properties.mun_name",
            name="Non-Avocado Municipalities",
            colorbar=dict(title="Gini", x=0.95),
            hovertemplate="Municipality: %{location}<br>Type: Non-Avocado Municipality<br>Gini: %{z:.3f}<extra></extra>"
        ))
        # notes
        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                center={"lat": center_lat, "lon": center_lon},
                zoom=6
            ),
            margin={"r":0, "t":40, "l":0, "b":0},
            title=title,
            annotations=[
                dict(
                    text="Green: Avocado Municipalities",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.02, y=0.02,
                    font=dict(color="green", size=12)
                ),
                dict(
                    text="Red: Non-Avocado Municipalities",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.02, y=0.00,
                    font=dict(color="red", size=12)
                )
            ]
        )
    return fig


# Callback to switch between tables
@app.callback(
    Output("output-table", "children"),
    [Input("btn-table1", "n_clicks"),
     Input("btn-table2", "n_clicks")]
)
def display_table(n1, n2):
    ctx = dash.callback_context  # To identify which button was clicked
    if not ctx.triggered:
        return "Click a button to display a table."
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "btn-table1":
        return html.Div([
            html.H3("Table 1: Gini Regression", style={"font-size": "14px"}),
            html.Iframe(srcDoc=table1_content, width="100%", height="300px", style={"border": "none"})
        ])
    elif button_id == "btn-table2":
        return html.Div([
            html.H3("Table 2: Employment Regression", style={"font-size": "14px"}),
            html.Iframe(srcDoc=table2_content, width="100%", height="300px", style={"border": "none"})
        ])
    
    return "Click a button to display a table."


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

    line = alt.Chart(df_crop_data).transform_filter(
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

    line = alt.Chart(df_gini_data).mark_line().encode(
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

    # Add a vertical reference line for 2011 to indicate the policy change.
    rule = alt.Chart(
        pd.DataFrame(
            {
                'Date': ['2011-01-01'],
                'color': ['red'],
                }
            )
        ).mark_rule().encode(
            x='Date:T',
            color=alt.Color('color:N', scale=None)
    )

    base = alt.layer(line, rule)

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

    bar = alt.Chart(df_wage_data).mark_bar(opacity=0.7).transform_filter(
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

""">>>>>> Dashboard <<<<<<"""
app.layout = dbc.Container(
    [
        html.Br(),
        dbc.Row(
            [
                # Number card.
                dbc.Col(
                    [
                        html.H3(
                            "Mexico | Michoacán",
                            style={"textAlign": "center", "color": "white"}
                            # style={"textAlign": "center"}
                            ),
                        # Municipality selection dropdown
                        html.Label(
                            "Select Municipality:",
                            style={"color": "white"}
                            ),
                        dcc.Dropdown(
                            id="mun-dropdown",
                            options=[
                                {"label": mun, "value": mun} \
                                    for mun in unique_municipalities
                                    ],
                            value=unique_municipalities[0],
                            clearable=False,
                            style={"color": "black"},
                        ),
                        html.Br(),

                        # Year selection dropdowns (pre and post 2011)
                        html.Label(
                            "Select Two Years (Pre & Post 2011):",
                            style={"color": "white"}
                            ),
                        dcc.Dropdown(
                            id="year-dropdown-1",
                            options=[
                                {"label": str(y), "value": y} \
                                    for y in unique_years if y <= 2011
                                    ],
                            value=2010,
                            clearable=False,
                            style={"color": "black"},
                        ),
                        dcc.Dropdown(
                            id="year-dropdown-2",
                            options=[
                                {"label": str(y), "value": y} \
                                    for y in unique_years if y > 2011
                                    ],
                            value=2018,
                            clearable=False,
                            style={"color": "black"},
                        ),

                        html.Br(),

                        # Display Gini coefficient information
                        html.H3(
                            id="gini-title",
                            style={"textAlign": "center", "color": "white"}
                            ),
                        html.Div(
                            [
                                html.P(
                                    id="gini-value-1",
                                    style={
                                        "textAlign": "center", 
                                        "fontSize": "18px", 
                                        "color": "white"
                                        }
                                    ),
                                html.P(
                                    id="gini-value-2", 
                                    style={
                                        "textAlign": "center", 
                                        "fontSize": "18px", 
                                        "color": "white"
                                        }
                                    ),

                                # Display change indicator (arrow + percentage)
                                html.Div(
                                    id="change-container",
                                    style={
                                        "textAlign": "center", 
                                        "fontSize": "24px", 
                                        "fontWeight": "bold"
                                        },
                                ),
                            ]
                        ),

                        html.Br(),

                        # Background information
                        html.P(
                            "Background:",
                            style={"color": "white", "textAlign": "center"}),
                        html.P(
                            "2011 (Full U.S. market access gained)",
                            style={"color": "gold", "textAlign": "center"}
                            ),

                        html.Br(),

                        # Explanation of the Gini coefficient
                        html.P(
                            "Gini Number: Measures income inequality",
                            style={"color": "white", "textAlign": "center"}
                            ),
                        html.P(
                            "Higher = more inequality (▲ Red = worsening)", 
                            style={
                                "color": "white", 
                                "textAlign": "center", 
                                "fontSize": "15px"
                                }
                            ),
                        html.P(
                            "Lower = more equality (▼ Green = improving)", 
                            style={
                                "color": "white", 
                                "textAlign": "center", 
                                "fontSize": "15px"
                                }
                            ),
                    ],
                    width=3,
                    style={
                        'border': '1px solid #d3d3d3',
                        'border-radius': '10px',
                        'backgroundColor': "black", 
                        },
                ),

                #Map chart.
                dbc.Col(
                    html.Div(
                        style={
                            'fontFamily': 'Open Sans, sans-serif',
                            'maxWidth': '1000px',
                            'margin': 'auto'
                            },
                        children=[
                            html.H2(
                                "Interactive Municipal Gini Map", 
                                style={'textAlign': 'center'}
                                ),
                            html.Div(
                                [
                                    html.Label(
                                        "Select Year:",
                                        style={
                                            'fontWeight': 'bold',
                                            'marginRight': '10px'
                                            }
                                        ),
                                    dcc.Dropdown(
                                        id='year-dropdown',
                                        options=[
                                            {"label": str(year), "value": year} \
                                                for year in available_years
                                                ],
                                        value=available_years[0],
                                        clearable=False,
                                        style={
                                            'width': '100px',
                                            'height': '25px',         
                                            'padding': '2px',         
                                            'fontSize': '15px',       
                                            'display': 'inline-block'
                                            }
                                    )
                                ],
                                style={'padding': '10px', 'textAlign': 'center'}
                                ),
                            html.Div(
                                [
                                    html.Label(
                                        "Select Map Type:",
                                        style={'fontWeight': 'bold', 'marginRight': '10px'}
                                        ),
                                    dcc.Dropdown(
                                        id='map-type-dropdown',
                                        options=map_type_options,
                                        value="tratados",
                                        clearable=False,
                                        style={
                                            'width': '300px',
                                            'height': '25px',
                                            'padding': '2px',
                                            'fontSize': '15px',
                                            'display': 'inline-block'
                                            }
                                    )
                                ],
                                style={'padding': '10px', 'textAlign': 'center'}
                                ),
                            html.Div(
                                [dcc.Graph(id='graph-map')], style={
                                'padding': '10px'
                                }
                            )
                        ]
                    ),
                    width=7,
                    style={
                        'border': '1px solid #d3d3d3',
                        'border-radius': '10px',
                        },
                ),
                
                # Tables.
                dbc.Col(
                    # Container for buttons and table together
                    html.Div(
                        [
                        # Buttons positioned above the table
                        html.Div(
                            [
                                html.H3(
                                    "Information Tables", 
                                    style={'textAlign': 'center'}
                                ),
                                html.Button(
                                    "Gini", id="btn-table1", n_clicks=0,
                                    style={
                                        'fontWeight': 'bold',
                                        'marginRight': '10px'
                                        }
                                    ),
                                html.Button(
                                    "Employment Rate", id="btn-table2", 
                                    n_clicks=0,
                                    style={
                                        'fontWeight': 'bold',
                                        'marginRight': '10px'
                                        }
                                    )
                            ],
                            style={
                                'textAlign': 'right', 'padding-right': '2px'
                                }
                        ),
                        # Visualization container - Positioned in the top-right
                        html.Div(
                            id="output-table",
                            style={
                                # "position": "absolute", 
                                # "top": "100px",  # Shifted down to fit buttons
                                # "right": "10px", 
                                "height": "500px",
                                "border": "1px solid #ddd",
                                "padding": "1px",
                                "backgroundColor": "#f8f9fa",
                                "boxShadow": "2px 2px 10px rgba(0,0,0,0.1)"
                                }
                            )
                        ]
                    ),
                    width=2,
                    style={
                        'border': '1px solid #d3d3d3',
                        'border-radius': '10px',
                        },
                ),
            ],
        ),
        html.Br(),
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
                                ],
                            ),
                    ],
                    md=4,
                    style={
                        'border': '1px solid #d3d3d3',
                        'border-radius': '10px',
                        },
                    width=4
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
                        'border-radius': '10px',
                        },
                    width=4
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
                                        df_wage_data['year'].unique().tolist()
                                ]
                            ),
                    ],
                    md=4,
                    style={
                        'border': '1px solid #d3d3d3',
                        'border-radius': '10px',
                        },
                    width=4
                )
            ]
        )
    ],
    fluid=False,  # Constrain layout width
    style={
        # "backgroundColor": "black", 
        # "padding": "20px", 
        # "maxWidth": "600px", 
        "margin": "auto"
        },
)

server = app.server 
if __name__ == '__main__':
    app.run_server(
        debug=False,
        host='0.0.0.0', port=int(os.environ.get('PORT', 8050))
        )
