from dash import Dash
import dash_bootstrap_components as dbc
from components.layout import create_layout

# Initialize Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Set up layout
app.layout = create_layout()

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
