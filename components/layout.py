from dash import html
from components.navbar import navbar
from components.sidebar import sidebar

def create_layout():
    return html.Div([
        navbar(),
        sidebar(),
        html.Div(id="main-content", style={"margin-left": "250px", "padding": "20px"})
    ])
