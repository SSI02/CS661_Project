# pages/homepage.py

import dash_bootstrap_components as dbc
from dash import html

layout = html.Div(
    style={
        "backgroundImage": "linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.7)), url('https://images.unsplash.com/photo-1503264116251-35a269479413?auto=format&fit=crop&w=1470&q=80')",
        "backgroundSize": "cover",
        "backgroundPosition": "center",
        "minHeight": "100vh",
        "color": "white",
        "margin": "0",
        "padding": "0",
        "fontFamily": "'Poppins', sans-serif"
    },
    children=[
        html.Div(
            style={
                "backgroundColor": "rgba(0, 0, 0, 0.4)",
                "padding": "2rem",
                "minHeight": "100vh"
            },
            children=[
                dbc.Container(
                    fluid=True,
                    children=[
                        dbc.Row(
                            dbc.Col([
                                html.Div([
                                    html.H1("Climate Change Dashboard", 
                                           className="display-3 text-center mt-4 mb-0 fw-bold"),
                                    html.Div("🌍 Data-Driven Insights on Our Changing Planet", 
                                            className="lead text-center mb-3 fs-4 text-info"),
                                    html.Hr(className="my-4 bg-info opacity-75"),
                                ], style={"animation": "fadeIn 1s ease-in"})
                            ])
                        ),

                        # Information banner
                        dbc.Row([
                            dbc.Col(
                                dbc.Alert(
                                    [
                                        html.I(className="fas fa-info-circle me-2"),
                                        "Explore interactive visualizations showing the real impact of climate change through global data"
                                    ],
                                    color="info",
                                    className="d-flex align-items-center text-center py-2 rounded-pill shadow"
                                ),
                                width={"size": 10, "offset": 1},
                                className="mb-4"
                            )
                        ]),

                        # Cards row - uses Bootstrap card deck style
                        dbc.Row([
                            # Temperature card
                            dbc.Col(
                                dbc.Card(
                                    [
                                        dbc.CardBody([
                                            html.Div([
                                                html.Span("🌡️", className="display-5"),
                                                html.H4("Temperature Changes", className="card-title ms-2 d-inline-block")
                                            ], className="d-flex align-items-center mb-3"),
                                            html.P("Visualize global temperature trends and analyze geographic patterns with interactive maps.", 
                                                  className="card-text text-dark"),
                                        ]),
                                        dbc.CardFooter(
                                            dbc.Button("Explore Data", href="/temperature", color="primary", 
                                                      className="w-100 rounded-pill shadow-sm")
                                        )
                                    ],
                                    className="h-100 shadow-lg border-0 rounded-3 card-hover",
                                    style={
                                        "background": "linear-gradient(145deg, #A3D8F4, #7CC2E5)",
                                        "color": "#343a40"
                                    }
                                ),
                                lg=3, md=6, 
                                className="mb-4"
                            ),
                            
                            # CO2 Emissions card
                            dbc.Col(
                                dbc.Card(
                                    [
                                        dbc.CardBody([
                                            html.Div([
                                                html.Span("🏭", className="display-5"),
                                                html.H4("CO2 Emissions", className="card-title ms-2 d-inline-block")
                                            ], className="d-flex align-items-center mb-3"),
                                            html.P("Examine carbon emission trends by country and sector with comparative analysis tools.", 
                                                  className="card-text text-dark"),
                                        ]),
                                        dbc.CardFooter(
                                            dbc.Button("Explore Data", href="/emissions", color="danger", 
                                                      className="w-100 rounded-pill shadow-sm")
                                        )
                                    ],
                                    className="h-100 shadow-lg border-0 rounded-3 card-hover",
                                    style={
                                        "background": "linear-gradient(145deg, #D9EAD3, #A8D08D)",
                                        "color": "#343a40"
                                    }
                                ),
                                lg=3, md=6, 
                                className="mb-4"
                            ),
                            
                            # Sea Level card
                            dbc.Col(
                                dbc.Card(
                                    [
                                        dbc.CardBody([
                                            html.Div([
                                                html.Span("🌊", className="display-5"),
                                                html.H4("Rising Sea Levels", className="card-title ms-2 d-inline-block")
                                            ], className="d-flex align-items-center mb-3"),
                                            html.P("Track sea level rise and its impacts on coastal regions with predictive models.", 
                                                  className="card-text text-dark"),
                                        ]),
                                        dbc.CardFooter(
                                            dbc.Button("Explore Data", href="/sea_level", color="info", 
                                                      className="w-100 rounded-pill shadow-sm")
                                        )
                                    ],
                                    className="h-100 shadow-lg border-0 rounded-3 card-hover",
                                    style={
                                        "background": "linear-gradient(145deg, #FAD02E, #F5C211)",
                                        "color": "#343a40"
                                    }
                                ),
                                lg=3, md=6, 
                                className="mb-4"
                            ),
                            
                            # Correlation card
                            dbc.Col(
                                dbc.Card(
                                    [
                                        dbc.CardBody([
                                            html.Div([
                                                html.Span("🔗", className="display-5"),
                                                html.H4("Correlation Analysis", className="card-title ms-2 d-inline-block")
                                            ], className="d-flex align-items-center mb-3"),
                                            html.P("Discover relationships between temperature changes, CO2 emissions, and rising sea levels.", 
                                                  className="card-text text-dark"),
                                        ]),
                                        dbc.CardFooter(
                                            dbc.Button("Explore Data", href="/correlation", color="secondary", 
                                                      className="w-100 rounded-pill shadow-sm")
                                        )
                                    ],
                                    className="h-100 shadow-lg border-0 rounded-3 card-hover",
                                    style={
                                        "background": "linear-gradient(145deg, #FFB6C1, #FF99AC)",
                                        "color": "#343a40"
                                    }
                                ),
                                lg=3, md=6, 
                                className="mb-4"
                            )
                        ], className="mt-3"),
                        
                        # Footer information
                        dbc.Row([
                            dbc.Col(
                                html.Div([
                                    html.P("Climate data sourced from scientific research organizations", 
                                          className="text-center text-light-50 small")
                                ], className="mt-4 pt-3"),
                                width=12
                            )
                        ])
                    ]
                )
            ]
        )
    ]
)