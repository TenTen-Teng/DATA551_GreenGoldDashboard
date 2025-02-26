import dash
from dash import dcc, html, Input, Output
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
from unidecode import unidecode
from shapely.ops import transform
import pyproj
from pathlib import Path

# absolute path to the root of the repository
repo_root = Path(__file__).resolve().parent

# search for the root of the repository
while repo_root.name != "DATA551_GreenGoldDashboard" and repo_root.parent != repo_root:
    repo_root = repo_root.parent

# build the path to the data file
data_path_gini = repo_root / "data" / "gini_mun_month_clean.csv"
data_path_shapefile = repo_root / "data" / "shapefiles_mich" /"16mun.shp"


# 1. Load and preprocess Gini data 
gini = pd.read_csv(data_path_gini)
#gini['trat_1'] = gini.groupby('mun_name')['trat_2'].transform('max')
gini_anual = gini.groupby(['mun_name', 'year'], as_index=False)['gini'].mean()
tratamiento = gini[['mun_name', 'trat_2']].drop_duplicates()
gini_anual = pd.merge(gini_anual, tratamiento, on='mun_name', how='left')

# 2. Load and prepare shapefile 
mich = gpd.read_file(data_path_shapefile)
def limpiar_nombres(nombre):
    nombre = unidecode(nombre).replace(' de Vazquez Pallares', '').replace(' de Nicolas Romero', '')
    return nombre.strip()
mich['mun_name'] = mich['NOMGEO'].apply(limpiar_nombres)
mich = mich.to_crs(epsg=4326)
mich_projected = mich.to_crs(epsg=3857)
center_projected = mich_projected.geometry.union_all().centroid
center = gpd.GeoSeries([center_projected], crs="EPSG:3857").to_crs(epsg=4326).iloc[0]
center_lon, center_lat = center.x, center.y
minx, miny, maxx, maxy = mich.total_bounds
bounds = dict(west=minx, south=miny, east=maxx, north=maxy)
base_geojson = json.loads(mich.to_json())

df_full = gini_anual.drop_duplicates(subset=['mun_name', 'year'])
df_tratados = df_full[df_full['trat_2'] == 1].copy()
df_control   = df_full[df_full['trat_2'] == 0].copy()

global_min = df_full['gini'].min()
global_max = df_full['gini'].max()

# years for dropwdown
available_years = sorted(df_full['year'].unique())
# type of mun
map_type_options = [
    {"label": "Avocado Municipalities", "value": "tratados"},
    {"label": "Non-Avocado Municipalities", "value": "control"},
    {"label": "Both", "value": "both"}
]

# 5. dash app
app = dash.Dash(__name__)
app.layout = html.Div(
    style={'fontFamily': 'Open Sans, sans-serif', 'maxWidth': '1000px', 'margin': 'auto'},
    children=[
        html.H2("Interactive Municipal Gini Map", style={'textAlign': 'center'}),
        
        html.Div([
            html.Label("Select Year:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{"label": str(year), "value": year} for year in available_years],
                value=available_years[0],
                clearable=False,
                style={'width': '100px',
                       'height': '25px',         
                       'padding': '2px',         
                       'fontSize': '15px',       
                       'display': 'inline-block'}
            )
        ], style={'padding': '10px', 'textAlign': 'center'}),
        
        html.Div([
            html.Label("Select Map Type:", style={'fontWeight': 'bold', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='map-type-dropdown',
                options=map_type_options,
                value="tratados",
                clearable=False,
                style={'width': '300px',
                       'height': '25px',
                       'padding': '2px',
                       'fontSize': '15px',
                       'display': 'inline-block'}
            )
        ], style={'padding': '10px', 'textAlign': 'center'}),
        
        html.Div([
            dcc.Graph(id='graph-map')
        ], style={'padding': '10px'})
    ]
)

# 6. Callback to update the map based on selected year and map type
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

if __name__ == '__main__':
    app.run_server(debug=True)
