import os
from pathlib import Path

import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import altair as alt
import dash_bootstrap_components as dbc
from dash import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import json
import pandas as pd

from data_process import (
    crops_line_dataset, gini_line_dataset, wage_dataset, map_dataset,
    number_card_dataset
    )
from helper import calculate_change

# absolute path to the root of the repository
repo_root = Path(__file__).resolve().parents[1]

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
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
    )
app.title = "Green Gold Dashboard"

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
        fig.add_trace(go.Choroplethmapbox(
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
        fig.add_trace(go.Choroplethmapbox(
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
    domain = ['Blueburry', 'Corn', 'Acovodo']
    colors = ['#464196', '#fbec5d', '#1B9E77']
    line = alt.Chart(df_crop_data).transform_filter(
        {
            'field': 'name_unitmes',
            'oneOf': ['Blueburry', 'Corn', 'Acovodo']
            }
    ).mark_line(point=True).encode(
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
                orient='right',
                labelLimit=0
                ),
            ).scale(domain=domain, range=colors),
        tooltip=[
            alt.Tooltip('name_unitmes:N', title='Crops'),
            alt.Tooltip('year:T', title='Year'), 
            alt.Tooltip(f'{ycol}', title=f'{ycol}'.title())
            ],
    ).interactive().properties(
        width=900,
        height=400,
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
    width = 900
    line = alt.Chart(df_gini_data).mark_line(point=True).encode(
        x=alt.X('date:T', title=None),
        y=alt.Y('gini:Q', title="Gini Coefficients"),
        color=alt.Color(
            'trat_2:N',
            title="Treatment groups",
            legend=alt.Legend(
                titleFontSize=15, labelFontSize=15,
                orient='right',
                labelLimit=0
                ),
            scale=alt.Scale(scheme="dark2"),
            ),
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
    lower = base.properties(
        height=50, width=width
        ).add_params(brush)

    upper = base.encode(
        alt.X('date:T', title=None, scale=alt.Scale(domain=brush)),
        tooltip=[
            alt.Tooltip('date:T', title="Date"), 
            alt.Tooltip('trat_2:N', title='Group'),
            alt.Tooltip('gini:Q', title='Gini', format='.3f'),
            ]
    ).properties(
        width=width,
        height=350,
        title=alt.Title(
            text="Gini Coeffeicents",
            subtitle="avocado-growing vs. non-avocado-growing municipalities",
            subtitleFontSize=15,
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
                orient='right',
                labelLimit=0
                ),
            scale=alt.Scale(scheme="dark2"),
            ),
        opacity=alt.condition(click, alt.value(0.9), alt.value(0.2)),
        tooltip=[
            alt.Tooltip('trat:N', title='Group'),
            alt.Tooltip('rs_group:N', title='Wage level'),
            alt.Tooltip(
                'PercentOfTotal:Q', title='Percentage of total', format='.2%'
                ),
        ]
    ).add_params(click).interactive().properties(
        width=900,
        height=400,
        title=alt.Title(
            text="Wage Levels",
            subtitle="avocado-growing vs. non-avocado-growing municipalities",
            subtitleFontSize=15,
            fontSize=20,
            anchor='middle'
        )
    )

    return bar.to_html()

@app.callback(
    Output("collapse", "is_open"),
    [Input("gini-def", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

""">>>>>> Dashboard <<<<<<"""
app.layout = dbc.Container(
    [
        dbc.Row(
            html.H2(
                "Green Gold, Unequal Gains 🥑",
                style={'textAlign': 'center', 'color': '#D4AF37'},
                className="display-3"
            )
        ),
        dbc.Row(
            [
                    dbc.Col(
                        [
                        dbc.Button(
                            "Gini Coefficient",
                            id="gini-def",
                            n_clicks=0,
                            style={"backgroundColor": "#D4AF37",  
                                    "color": "#1B3B1A",  
                                    "border": "2px solid #D4AF37",  
                                    "borderRadius": "5px",
                                    "padding": "10px 15px",
                                    "fontWeight": "bold",
                                    "width": "100%",
                                    "height": "100%"
                                },
                        ),
                ],
                width=2
                    ),
                    dbc.Col(
                        dbc.Collapse(
                            dbc.Card(
                                dbc.CardBody(
                                    "❗The Gini coefficient is a measure of income or "
                                    "wealth inequality in an economy. It ranges from 0 "
                                    "to 1, where 0 represents perfect equality, and 1 represents "
                                    "maximum inequality.",
                                    style={
                                        'margin-top': '-10px',
                                        'margin-bottom': '-10px',
                                        'margin-left': '-10px',
                                        'margin-right': '-10px',
                                        'fontSize': '12px'
                                    }
                                )
                            ),
                            id="collapse",
                            is_open=False,
                        ),
                        width=8
                        ),
                    dbc.Col(
                        dbc.Button(
                            "Switch Page", 
                            id="page-toggle-button", 
                            n_clicks=0,
                            style={
                                "backgroundColor": "#FFFFFF",  
                                "color": "#D4AF37",  
                                "border": "2px solid #D4AF37",  
                                "borderRadius": "5px",
                                "padding": "10px 15px",
                                "fontWeight": "bold",
                                "width": "100%",
                                "height": "100%",
                                }
                        ),
                        width=2,
                    ),
                ],
            # className="mb-2",
            className="g-0",
            style={
                'margin-bottom': '10px',
                'height': '100%',
            },
        ),
        dbc.Row(
            html.Div(id="page-content"),
            className="mb-2",
            style={
                'height': '100%',
            },
            )
    ],
    fluid=True,
    style={
        "backgroundColor": "#013220",
        "padding": "30px",
        'height': '100%',
        },
)

def page1():
    # Explanation of the Gini coefficient
    return dbc.Row(
        [
        # Number card.
        dbc.Col(
                [
                    html.H3(
                        "Mexico | Michoacán",
                        style={"textAlign": "center", "color": "#D4AF37"}
                    ),
                    html.Label(
                            "Select Municipality:",
                            style={
                                "color": "#D4AF37", 
                                "display": "block", 
                                "textAlign": "center", 
                                "margin-bottom": "3px"
                                }
                            ),
                    dcc.Dropdown(
                        id="mun-dropdown",
                        options=[{"label": mun, "value": mun} for mun in unique_municipalities],
                        value=unique_municipalities[0],
                        clearable=False,
                        style={
                                "color": "black",
                                "width": "80%", "margin": "0 auto", "height": "30px"
                                }
                    ),
                    html.Br(),

                    # Year selection dropdowns (pre and post 2011)
                    html.Label("Select Two Years (Pre & Post 2011):", style={"color": "#D4AF37"}),
                    dbc.Row([
                        dbc.Col(
                            dcc.Dropdown(
                                id="year-dropdown-1",
                                options=[
                                    {"label": str(y), "value": y} \
                                        for y in unique_years if y <= 2011
                                ],
                                value=2010,
                                clearable=False,
                                style={"color": "black", "width": "100%", "height": "30px"},
                            ), width=6, style={"padding-left": "5px", "padding-right": "2px"}
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="year-dropdown-2",
                                options=[
                                    {"label": str(y), "value": y} \
                                        for y in unique_years if y > 2011
                                ],
                                value=2018,
                                clearable=False,
                                style={"color": "black", "width": "100%", "height": "30px"},
                            ), width=6, style={"padding-left": "2px", "padding-right": "5px"}
                        ),
                    ], style={"margin": "0px", "justify-content": "center"}),

                    html.Br(),

                    # Display Gini coefficient information
                    html.H3(
                        id="gini-title",
                        style={"textAlign": "center", "color": "#D4AF37", "margin-bottom": "5px"}
                    ),

                    dbc.Row([
                        dbc.Col(
                            html.P(
                                id="gini-value-1",
                                style={"textAlign": "center", "fontSize": "18px", "color": "#D4AF37", "margin-bottom": "0px", "line-height": "0.5"}
                            ), width=6, style={"padding-right": "3px"}
                        ),
                        dbc.Col(
                            html.P(
                                id="gini-value-2",
                                style={"textAlign": "center", "fontSize": "18px", "color": "#D4AF37", "margin-bottom": "0px", "line-height": "0.5"}
                            ), width=6, style={"padding-right": "3px"}
                        ),
                    ], style={"justify-content": "center", "margin-bottom": "0px", "padding": "0px"}),

                            # Display change indicator (arrow + percentage + hover tooltip)
                            html.Div([
                                html.Span(
                                    id="change-container",
                                    style={
                                        "textAlign": "center",
                                        "fontSize": "55px",
                                        "fontWeight": "bold",
                                        "margin-top": "2px",
                                        "margin-bottom": "1px",
                                        "line-height": "0.5"
                                    }
                                ),

                                html.Span(
                                    "  ❔",
                                    id="tooltip-question",
                                    style={"cursor": "pointer", "fontSize": "15px", "verticalAlign": "super"}
                                ),

                                # Tooltip that appears on hover
                                dbc.Tooltip(
                                    [
                                        "Higher = more inequality", 
                                        html.Br(),
                                        "(▲ Red = worsening)", 
                                        html.Br(),
                                        "Lower = more equality", 
                                        html.Br(),
                                        "(▼ Green = improving)"
                                    ],
                                    target="tooltip-question",
                                    placement="right",
                                    style={"fontSize": "14px", "maxWidth": "300px", "whiteSpace": "normal"}
                                )
                            ], style={"display": "flex", "alignItems": "center", "justifyContent": "center"}),

                    html.Br(),

                    # Background information
                    html.P(
                        "Background:",
                        style={"color": "white", "textAlign": "center", "margin-top": "0px", "margin-bottom": "1px"}),
                    html.P(
                        "2011 (Full U.S. market access gained)",
                        style={"color": "gold", "textAlign": "center", "margin-top": "0px", "margin-bottom": "1px"}
                        ),

                        html.Br(),
                    ],
                    
                    width=3,
                    style={
                        'border': '1px solid #D4AF37',
                        'border-radius': '10px',
                        'backgroundColor': "#1B3B1A"
                        },
                ),

        # Map chart.
        dbc.Col(
        html.Div(
            style={
                'fontFamily': 'Open Sans, sans-serif',
                # 'maxWidth': '1000px',
                'margin': 'auto',
                'height': '600px',
                'width': '100%'
            },
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            # html.Div(
                                [
                                    # html.Label(
                                    #     "Select Year:",
                                    #     style={
                                    #         'fontWeight': 'bold',
                                    #         'marginRight': '8px',
                                    #         "color": "#D4AF37"
                                    #     }
                                    # ),
                                    dcc.Dropdown(
                                        id='year-dropdown',
                                        placeholder='Select a year...',
                                        options=[
                                            {"label": str(year), "value": year}
                                            for year in available_years
                                        ],
                                        value=available_years[8],
                                        clearable=False,
                                        style={
                                            'width': '100%',  
                                            'height': '30px',
                                            'padding': '2px',
                                            'fontSize': '15px',
                                            'display': 'inline-block'
                                        }
                                    ),
                                ],
                                style={
                                    # 'padding': '10px', 
                                    'textAlign': 'center'
                                    },
                            # ),
                            width=6,
                            className="md-2" 
                        ),
                        dbc.Col(
                            html.Div(
                                [
                                    # html.Label(
                                    #     "Select Map Type:",
                                    #     style={
                                    #         'fontWeight': 'bold',
                                    #         'marginRight': '8px',
                                    #         'color': '#D4AF37'
                                    #     }
                                    # ),
                                    dcc.Dropdown(
                                        id='map-type-dropdown',
                                        placeholder='Select Map Type...',
                                        options=map_type_options,
                                        value="both",
                                        clearable=False,
                                        style={
                                            'width': '100%', 
                                            'height': '30px',
                                            'padding': '2px',
                                            'fontSize': '15px',
                                            'display': 'inline-block'
                                        }
                                    )
                                ],
                                style={'padding': '5px', 'textAlign': 'center'}
                            ),
                            width=6,
                            className="md-2"
                        )
                    ],
                    justify="center",  
                    align="center",  
                    className="g-0"
                ),
                dbc.Row(
                    dcc.Graph(id='graph-map'),
                    style={
                            'padding': '5px',
                            'height': '90%'
                            }
                    # )
                )
            ]
        ),
        width=9,
        style={
            'border': '1px solid #D4AF37',
            'border-radius': '5px',
            'backgroundColor': "#1B3B1A",
            },
    ),        
],
    style={
        # "backgroundColor": "black", 
        # "padding": "20px", 
        # "maxWidth": "600px", 
        "margin": "auto"
        },
)

def page2():
    return dbc.Row(
        [
            dbc.Col(width=1),
            dbc.Col(
                dbc.Tabs(
                    [
                        dbc.Tab(
                            [
                                # Graph 1: line chart of gini trend over time between 
                                # avocado-growing and non-avocado-growing municipalities. 
                                html.Iframe(
                                        id='gini_line',
                                        style={
                                            'border-width': '0',
                                            'width': '100%',
                                            'height': '585px',
                                            'backgroundColor':'white'
                                            },
                                        srcDoc=plot_gini_value_lines(),  
                                    )
                                                     
                            ],
                            id='gini-line-tab',
                            label='Gini Coefficients Trend ❔',
                            active_label_style={
                                "color": "#1B3B1A",
                                "fontWeight": "bold",
                                },
                            label_style={
                                "color": "#FFFFFF",
                            }
                        ),
                        dbc.Popover(
                            'Display the trend of Gini Coefficients from '
                            '2003 to 2020 between avocado-growing '
                            'municipalities and non-avocado-growing '
                            'municipalities. Drag the lower line chart to '
                            'view detailed information for a specific '
                            'year.',
                            target="gini-line-tab",
                            body=True,
                            trigger="hover",
                        ),
                        dbc.Tab(
                            [
                                # Graph 2: line plot with multiple crops.
                                dcc.Dropdown(
                                        id='ycol-crop-line-widget',
                                        value='production_value',
                                        options=[
                                            {'label': name, 'value': col
                                                } for col, name in \
                                                    value_types.items()
                                        ],
                                        style={'width': '100%'}
                                    ),
                                html.Iframe(
                                        title='Values for Different Crops',
                                        id='crop_line',
                                        style={
                                            'border-width': '0',
                                            'width': '100%',
                                            'height': '550px',
                                            'backgroundColor':'white'
                                            },
                                    )
                            ],
                            label='Values for Different Crops ❔',
                            id='crop-line-tab',
                            active_label_style={
                                "color": "#1B3B1A",
                                "fontWeight": "bold",
                                },
                            label_style={
                                "color": "#FFFFFF",
                            }
                        ),
                        dbc.Popover(
                            'Compare different values, such as production '
                            'value, price, yield, and production volume, '
                            'across various crops.',
                            target="crop-line-tab",
                            body=True,
                            trigger="hover",
                        ),
                        dbc.Tab(
                            [
                                dcc.Dropdown(
                                    id='col-wage-bar-widget',
                                    value=2011,
                                    options=[
                                        {'label': yr, 'value': yr} for yr in \
                                            df_wage_data['year'].unique().tolist()
                                    ],
                                    style={'width': '100%'}
                                ),
                                html.Iframe(
                                        id='wage-bar',
                                        style={
                                            'border-width': '0',
                                            'width': '100%',
                                            'height': '550px',
                                            'backgroundColor':'white'
                                            },
                                ),
                            ],
                            label='Wage Level ❔',
                            id='wage-bar-tab',
                            active_label_style={
                                "color": "#1B3B1A",
                                "fontWeight": "bold",
                                },
                            label_style={
                                "color": "#FFFFFF",
                            }
                        ),
                        dbc.Popover(
                            'Display wage level between avocado-growing '
                            'municipalities and non-avocado-growing '
                            'municipalities. Wage level 0 is the lowest '
                            'wage level and 5 is the hightest. Click '
                            'legend to highlight specific group and level.',
                            target="wage-bar-tab",
                            body=True,
                            trigger="hover",
                        ),
                    ]
                ),

                width=10
            ),
            dbc.Col(width=1),
        ],
    style={
            'border': '1px solid #D4AF37',
            'border-radius': '5px',
            'backgroundColor': "#1B3B1A",
            'border-radius': '10px',
            'height': '100%',
            'weight': '100%'
            },
    className='md-2'
)

@app.callback(
    Output("page-content", "children"),
    Input("page-toggle-button", "n_clicks"),
    State("page-content", "children")
)
def toggle_page(n_clicks, current_content):
    return page2() if n_clicks % 2 else page1()

server = app.server 
if __name__ == '__main__':
    app.run_server(
        debug=False,
        host='0.0.0.0', port=int(os.environ.get('PORT', 8050)),
    )