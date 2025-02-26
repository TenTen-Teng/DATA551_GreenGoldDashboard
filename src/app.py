import dash
from dash import html
from dash.dependencies import Input, Output

# Define file paths
file1_path = "./tables/tabla1_regresiones_mes_gini_mun_ptotrat.html"
file2_path = "./tables/tabla2_regresion_nivelempleo_year.html"

# Read HTML files
with open(file1_path, "r", encoding="utf-8") as file:
    table1_content = file.read()

with open(file2_path, "r", encoding="utf-8") as file:
    table2_content = file.read()

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    # Container for buttons and table together
    html.Div([
        # Buttons positioned above the table
        html.Div([
            html.Button("Gini", id="btn-table1", n_clicks=0, style={"margin": "5px"}),
            html.Button("Employment Rate", id="btn-table2", n_clicks=0, style={"margin": "5px"})
        ], style={'textAlign': 'right', 'padding-right': '20px'}),

        # Visualization container - Positioned in the top-right
        html.Div(id="output-table", style={
            "position": "absolute", 
            "top": "50px",  # Shifted down to fit buttons
            "right": "10px", 
            "width": "30%", 
            "height": "350px",
            "border": "1px solid #ddd",
            "padding": "10px",
            "backgroundColor": "#f8f9fa",
            "boxShadow": "2px 2px 10px rgba(0,0,0,0.1)"
        })
    ])
])

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

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
