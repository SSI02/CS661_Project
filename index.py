# index.py

from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from pages import temperature, emissions, sea_level, homepage, correlation



external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    "https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css",
]


# Initialize app
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

# Define layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Container(id='page-content', fluid=True, className="mt-0 p-0"),
])

# Callback to update pages
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/temperature':
        return temperature.layout
    elif pathname == '/emissions':
        return emissions.layout
    elif pathname == '/sea_level':
        return sea_level.layout
    elif pathname == '/correlation':
        return correlation.layout
    return homepage.layout  # Default page

if __name__ == '__main__':
    app.run(debug=True)
