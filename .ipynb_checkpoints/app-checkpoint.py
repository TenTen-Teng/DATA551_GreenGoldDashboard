# app.py

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd
from dash.dependencies import Input, Output

# Load dataset and clean column names
df = pd.read_csv("data/gini_mun_month_clean.csv")

# Aggregate and sort Gini data by municipality
df_agg = df.groupby(["year", "mun_name"])["gini"].mean().reset_index().sort_values(by="mun_name")
gini_data = df_agg.pivot(index="year", columns="mun_name", values="gini").to_dict()

# Store unique values to avoid redundant calculations
unique_municipalities = sorted(df_agg["mun_name"].unique())
unique_years = sorted(df_agg["year"].unique())

# Initialize Dash app with a dark theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

def calculate_change(old, new):
    """
    Compute the percentage change from old to new value.
    
    Args:
        old (float): Initial Gini value.
        new (float): New Gini value.
    
    Returns:
        float or None: Percentage change if both values exist, otherwise None.
    """
    if not old or not new:
        return None
    return ((new - old) / old) * 100

# Define app layout
app.layout = dbc.Container(
    [
        # Title
        html.H3("Mexico | Michoacán", style={"textAlign": "center", "color": "white"}),

        dbc.Row(
            [
                dbc.Col(
                    [
                        # Municipality selection dropdown
                        html.Label("Select Municipality:", style={"color": "white"}),
                        dcc.Dropdown(
                            id="mun-dropdown",
                            options=[{"label": mun, "value": mun} for mun in unique_municipalities],
                            value=unique_municipalities[0],
                            clearable=False,
                            style={"color": "black"},
                        ),
                        html.Br(),

                        # Year selection dropdowns (pre and post 2011)
                        html.Label("Select Two Years (Pre & Post 2011):", style={"color": "white"}),
                        dcc.Dropdown(
                            id="year-dropdown-1",
                            options=[{"label": str(y), "value": y} for y in unique_years if y <= 2011],
                            value=2010,
                            clearable=False,
                            style={"color": "black"},
                        ),
                        dcc.Dropdown(
                            id="year-dropdown-2",
                            options=[{"label": str(y), "value": y} for y in unique_years if y > 2011],
                            value=2018,
                            clearable=False,
                            style={"color": "black"},
                        ),

                        html.Br(),

                        # Display Gini coefficient information
                        html.H3(id="gini-title", style={"textAlign": "center", "color": "white"}),
                        html.Div(
                            [
                                html.P(id="gini-value-1", style={"textAlign": "center", "fontSize": "18px", "color": "white"}),
                                html.P(id="gini-value-2", style={"textAlign": "center", "fontSize": "18px", "color": "white"}),

                                # Display change indicator (arrow + percentage)
                                html.Div(
                                    id="change-container",
                                    style={"textAlign": "center", "fontSize": "24px", "fontWeight": "bold"},
                                ),
                            ]
                        ),

                        html.Br(),

                        # Background information
                        html.P("Background:", style={"color": "white", "textAlign": "center"}),
                        html.P("2011 (Full U.S. market access gained)", style={"color": "gold", "textAlign": "center"}),

                        html.Br(),

                        # Explanation of the Gini coefficient
                        html.P("Gini Number: Measures income inequality", style={"color": "white", "textAlign": "center"}),
                        html.P("Higher = more inequality (▲ Red = worsening)", style={"color": "white", "textAlign": "center", "fontSize": "15px"}),
                        html.P("Lower = more equality (▼ Green = improving)", style={"color": "white", "textAlign": "center", "fontSize": "15px"}),

                    ], width=7  # Centered content with limited width
                )
            ],
            justify="center"  # Center the row
        )
    ],
    fluid=False,  # Constrain layout width
    style={"backgroundColor": "black", "padding": "20px", "maxWidth": "600px", "margin": "auto"},
)

@app.callback(
    [
        Output("gini-title", "children"),
        Output("gini-value-1", "children"),
        Output("gini-value-2", "children"),
        Output("change-container", "children"),  # Outputs both arrow and percentage change
    ],
    [Input("mun-dropdown", "value"), Input("year-dropdown-1", "value"), Input("year-dropdown-2", "value")],
)
def update_gini(selected_mun, year1, year2):
    """
    Update Gini coefficient display based on selected municipality and years.

    Args:
        selected_mun (str): Selected municipality.
        year1 (int): First selected year (before 2011).
        year2 (int): Second selected year (after 2011).

    Returns:
        tuple: Updated values for Gini title, two Gini values, and change indicator.
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

if __name__ == "__main__":
    app.run_server(debug=True)