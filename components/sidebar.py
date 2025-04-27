from dash import html, dcc

def sidebar():
    return html.Div([
        html.H2("Filters"),
        html.Label("Select Year:"),
        dcc.Slider(id="year-slider", min=1990, max=2023, step=1, value=2018,
                   marks={i: str(i) for i in range(1990, 2024, 5)}),
        html.Label("Select Country:"),
        dcc.Dropdown(id="country-dropdown", options=[], value=None, multi=True)
    ], style={"width": "250px", "position": "fixed", "height": "100vh", "background-color": "#f8f9fa", "padding": "20px"})
