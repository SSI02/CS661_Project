# pages/temperature.py

from dash import html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime
import time

# — Load global data —
df_countries = pd.read_csv("data/GlobalLandTemperaturesByCountry.csv")
df_countries["dt"] = pd.to_datetime(df_countries["dt"])
df_countries["year"] = df_countries["dt"].dt.year

# Optimize data loading by pre-aggregating by year and country
df_agg = df_countries.groupby(['Country', 'year'])['AverageTemperature'].mean().reset_index()

min_year = int(df_countries["year"].min())
max_year = int(df_countries["year"].max())
year_marks = {y: str(y) for y in range(min_year, max_year + 1, 10)}

# Add more frequent marks for recent years
# for y in range(1900, max_year + 1, 20):
#     year_marks[y] = str(y)

# — Find which countries have GeoJSON files —
geo_files = [f for f in os.listdir("data/geojson") if f.endswith(".geojson")]
countries_with_geo = sorted(os.path.splitext(f)[0] for f in geo_files)

# — Layout exported for index.py to render —
layout = dbc.Container([
    # Header with info card
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H2("🌡️ Global Temperature Analysis", className="card-title text-primary"),
                    html.P(
                        "Explore temperature changes across different regions and time periods. "
                        "Use the animation controls to visualize temperature evolution over time.",
                        className="card-text"
                    )
                ]),
                className="mb-4 shadow border-0 bg-light"
            ),
            width=12
        )
    ]),

    # Control panel card
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    # Year controls with animation
                    dbc.Row([
                        dbc.Col([
                            html.Label("Time Period:", className="fw-bold mb-2"),
                            dbc.Row([
                                dbc.Col(
                                    html.Div(id="year-display", className="mt-1 fs-4 text-center"),
                                    width=2
                                ),
                                dbc.Col(
                                    dcc.Slider(
                                        id="year-slider",
                                        min=min_year,
                                        max=max_year,
                                        step=1,
                                        marks=year_marks,
                                        value=max_year,
                                        tooltip={"placement": "bottom", "always_visible": False},
                                        className="mt-2"
                                    ),
                                    width=8
                                ),
                                dbc.Col(
                                    html.Div([
                                        dbc.Button(
                                            html.I(className="fas fa-play"),
                                            id="play-button",
                                            color="success",
                                            className="me-2"
                                        ),
                                        dbc.Button(
                                            html.I(className="fas fa-stop"),
                                            id="stop-button",
                                            color="danger",
                                            disabled=True
                                        )
                                    ], className="d-flex justify-content-center"),
                                    width=2
                                )
                            ])
                        ], width=12)
                    ]),
                    
                    html.Hr(),
                    
                    # Visualization type tabs
                    dbc.Row([
                        dbc.Col([
                            html.Label("Visualization Type:", className="fw-bold mb-2"),
                            dcc.Tabs(
                                id="graph-tabs",
                                value=None,
                                className="nav-pills",
                                children=[
                                    dcc.Tab(
                                        label='🌍 Global Choropleth', 
                                        value='choropleth',
                                        className="p-2",
                                        selected_className="bg-primary text-white"
                                    ),
                                    # dcc.Tab(
                                    #     label='📍 Mapbox Explorer',
                                    #     value='mapbox',
                                    #     className="p-2",
                                    #     selected_className="bg-primary text-white"
                                    # ),
                                    dcc.Tab(
                                        label='📊 Temperature Comparison',
                                        value='scatter',
                                        className="p-2",
                                        selected_className="bg-primary text-white"
                                    ),
                                    dcc.Tab(
                                        label='🏞️ Regional Detail',
                                        value='state-choropleth',
                                        className="p-2",
                                        selected_className="bg-primary text-white"
                                    ),
                                ]
                            )
                        ], width=12)
                    ]),
                    
                    # Country dropdown - hidden by default
                    dbc.Row([
                        dbc.Col(
                            html.Div(
                                [
                                    html.Label("Select Country:", className="fw-bold mb-2"),
                                    dcc.Dropdown(
                                        id="country-dropdown",
                                        options=[{"label": c, "value": c} for c in countries_with_geo],
                                        placeholder="Select a country for regional view...",
                                        clearable=True,
                                        className="shadow-sm",
                                    ),
                                ],
                                className="mb-3",  # spacing utility in place of FormGroup
                            ),

                            width=6, className="mx-auto mt-3"
                        )
                    ], id="dropdown-row", style={"display": "none"}),
                ]),
                className="mb-4 shadow border-0"
            ),
            width=12
        )
    ]),

    # Graph with info panel
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    # Loading indicator for graph
                    dbc.Spinner(
                        dcc.Graph(
                            id="temperature-graph",
                            config={
                                "responsive": True,
                                "displayModeBar": True,
                                "scrollZoom": True
                            },
                            style={"height": "600px", "display": "none"},
                            className="border rounded"
                        ),
                        color="primary",
                        type="border",
                        fullscreen=False
                    ),
                    
                    # Temperature trends summary (hidden initially)
                    html.Div(
                        dbc.Alert(
                            id="temperature-insights",
                            color="info",
                            className="mt-3",
                            is_open=False
                        )
                    )
                ]),
                className="shadow border-0"
            ),
            width=12
        )
    ]),

    # Store to detect first tab‐click
    dcc.Store(id='tab-clicked-store', data=False),
    
    # Animation interval
    dcc.Interval(
        id='animation-interval',
        interval=1000,  # milliseconds between frame updates
        max_intervals=0,  # stop at max_year
        disabled=True
    ),
    
    # Current animation state
    dcc.Store(id='animation-state', data={"is_playing": False, "current_year": max_year}),
    
    # Store for animation speed
    dcc.Store(id='animation-speed', data=1000)  # milliseconds per frame

], fluid=True, className="p-4 bg-light")


# — Callbacks —

@callback(
    Output('tab-clicked-store', 'data'),
    Input('graph-tabs', 'value'),
    prevent_initial_call=True
)
def mark_tab_clicked(_):
    return True


@callback(
    Output("dropdown-row", "style"),
    Input("graph-tabs", "value")
)
def toggle_dropdown(selected_tab):
    if selected_tab == "state-choropleth":
        return {"display": "block"}
    return {"display": "none"}


@callback(
    Output("year-display", "children"),
    Input("year-slider", "value")
)
def update_year_display(year):
    return f"Year: {year}"


# Animation control callbacks
@callback(
    Output("animation-interval", "disabled"),
    Output("animation-state", "data"),
    Output("play-button", "disabled"),
    Output("stop-button", "disabled"),
    Output("year-slider", "value"),
    Input("play-button", "n_clicks"),
    Input("stop-button", "n_clicks"),
    Input("animation-interval", "n_intervals"),
    State("animation-state", "data"),
    State("year-slider", "value"),
    prevent_initial_call=True
)
def control_animation(play_clicks, stop_clicks, intervals, animation_state, current_year):
    # Get the ID of the component that triggered the callback
    ctx = dash.callback_context
    if not ctx.triggered:
        return True, animation_state, False, True, current_year
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Handle play button click
    if trigger_id == "play-button":
        animation_state["is_playing"] = True
        animation_state["current_year"] = current_year
        return False, animation_state, True, False, current_year
    
    # Handle stop button click
    elif trigger_id == "stop-button":
        animation_state["is_playing"] = False
        return True, animation_state, False, True, animation_state["current_year"]
    
    # Handle interval update (animation frame)
    elif trigger_id == "animation-interval":
        # If we've reached the max year, stop the animation
        if animation_state["current_year"] >= max_year:
            animation_state["is_playing"] = False
            return True, animation_state, False, True, max_year
        
        # Otherwise, increment the year
        animation_state["current_year"] += 1
        return False, animation_state, True, False, animation_state["current_year"]
    
    # Default return
    return True, animation_state, False, True, current_year


@callback(
    Output("temperature-graph", "figure"),
    Output("temperature-graph", "style"),
    Output("temperature-insights", "children"),
    Output("temperature-insights", "is_open"),
    Input("year-slider", "value"),
    Input("graph-tabs", "value"),
    Input("country-dropdown", "value"),
    Input("tab-clicked-store", "data")
)
def update_graph(selected_year, selected_tab, selected_country, tab_clicked):
    if not tab_clicked or not selected_tab:
        return no_update, {"display": "none"}, no_update, False

    # Filter data by year using the pre-aggregated data
    df_year = df_agg[df_agg["year"] == selected_year]
    
    # Calculate insights for the alert panel - handle NaN values properly
    df_year_clean = df_year.dropna(subset=["AverageTemperature"])
    
    if len(df_year_clean) > 0:
        global_avg = df_year_clean["AverageTemperature"].mean()
        # Get the full row for min/max temperature
        coldest_idx = df_year_clean["AverageTemperature"].idxmin()
        hottest_idx = df_year_clean["AverageTemperature"].idxmax()
        coldest_country = df_year_clean.loc[coldest_idx]
        hottest_country = df_year_clean.loc[hottest_idx]
    else:
        # Handle empty dataset gracefully
        global_avg = float('nan')
        coldest_country = {"Country": "No data", "AverageTemperature": float('nan')}
        hottest_country = {"Country": "No data", "AverageTemperature": float('nan')}
    
    insights_html = html.Div([
        html.H5(f"Temperature Insights for {selected_year}"),
        html.Ul([
            html.Li([
                html.Strong("Global Average Temperature: "),
                f"{global_avg:.2f}°C" if not pd.isna(global_avg) else "No data"
            ]),
            html.Li([
                html.Strong("Coldest Country: "),
                f"{coldest_country['Country']} ({coldest_country['AverageTemperature']:.2f}°C)" 
                if not pd.isna(coldest_country['AverageTemperature']) else "No data"
            ]),
            html.Li([
                html.Strong("Hottest Country: "),
                f"{hottest_country['Country']} ({hottest_country['AverageTemperature']:.2f}°C)"
                if not pd.isna(hottest_country['AverageTemperature']) else "No data"
            ])
        ])
    ])

    # Global choropleth
    if selected_tab == "choropleth":
        fig = px.choropleth(
            df_year,
            locations="Country",
            locationmode="country names",
            color="AverageTemperature",
            title=f"Global Temperature Distribution ({selected_year})",
            color_continuous_scale="RdBu_r",  # Blue (cold) to Red (hot)
            template="plotly_white",
            range_color=[-10, 30]  # Fixed temperature range for better comparison
        )
        fig.update_layout(
            coloraxis_colorbar=dict(
                title="Temp (°C)",
                ticks="outside",
                tickvals=[-10, 0, 10, 20, 30],
                ticktext=["-10°C", "0°C", "10°C", "20°C", "30°C"]
            ),
            geo=dict(
                showcoastlines=True,
                coastlinecolor="Black",
                showland=True,
                landcolor="lightgray",
                showcountries=True,
                countrycolor="gray"
            )
        )

    # Global scatter‐geo
    elif selected_tab == "mapbox":
        fig = px.scatter_geo(
            df_year.dropna(subset=["AverageTemperature"]),
            locations="Country",
            locationmode="country names",
            color="AverageTemperature",
            size="AverageTemperature",
            size_max=15,
            hover_name="Country",
            title=f"Global Temperature Distribution ({selected_year})",
            color_continuous_scale="Plasma",
            template="plotly_white",
            range_color=[-10, 30]  # Fixed temperature range
        )
        fig.update_layout(
            geo=dict(
                showcoastlines=True,
                coastlinecolor="Black",
                showland=True,
                landcolor="lightgray",
                showcountries=True,
                countrycolor="gray",
                projection_type="natural earth"
            )
        )

    # Global temperature‐by‐country scatter
    elif selected_tab == "scatter":
        # Sort by temperature for better visualization
        sorted_df = df_year.sort_values("AverageTemperature")
        
        fig = px.bar(
            sorted_df,
            x="Country",
            y="AverageTemperature",
            title=f"Average Temperature by Country ({selected_year})",
            template="plotly_white",
            color="AverageTemperature",
            color_continuous_scale="RdBu_r",
            range_color=[-20, 40],
            hover_data={"Country": True, "AverageTemperature": ":.2f"}
        )
        fig.update_layout(
            xaxis=dict(
                tickangle=45,
                title="Country",
                categoryorder="total ascending"
            ),
            yaxis=dict(
                title="Temperature (°C)"
            ),
            height=600
        )

    # State‐level choropleth for one country
    elif selected_tab == "state-choropleth" and selected_country:
        try:
            # load geojson & CSV
            with open(f"data/geojson/{selected_country}.geojson", encoding='utf-8') as f:
                gj = json.load(f)
            df_state = pd.read_csv(f"data/by_country_temp/{selected_country}.csv")
            df_state["dt"] = pd.to_datetime(df_state["dt"])
            df_state["year"] = df_state["dt"].dt.year
            dff = df_state[df_state["year"] == selected_year]
            
            # Get state names from geojson and create hover data
            hover_data = pd.DataFrame()
            for feature in gj['features']:
                state_id = feature['properties']['cartodb_id']
                # Try different property fields for state name
                for name_field in ['name', 'NAME', 'state', 'STATE', 'province', 'PROVINCE']:
                    if name_field in feature['properties']:
                        feature['properties']['state_name'] = feature['properties'][name_field]
                        break
                # If no name found, use a placeholder
                if 'state_name' not in feature['properties']:
                    feature['properties']['state_name'] = f"Region {state_id}"
                
                # Add to hover data frame
                hover_data = pd.concat([
                    hover_data, 
                    pd.DataFrame({'cartodb_id': [state_id], 'state_name': [feature['properties']['state_name']]})
                ])
            
            # Merge with temperature data
            dff = dff.merge(hover_data, on='cartodb_id', how='left')
            
            # Create choropleth with proper hover names
            fig = px.choropleth(
                dff,
                geojson=gj,
                locations="cartodb_id",
                featureidkey="properties.cartodb_id",
                color="AverageTemperature",
                hover_name="state_name",  # Use the state name for hover
                hover_data={"cartodb_id": False, "AverageTemperature": ":.1f", "state_name": False},
                color_continuous_scale="RdBu_r",
                range_color=[-10, 30],
                title=f"{selected_country} - Regional Temperatures ({selected_year})",
                template="plotly_white"
            )
            
            # Customize hover template
            fig.update_traces(
                hovertemplate="<b>%{hovertext}</b><br>Temp: %{z:.1f}°C<extra></extra>"
            )
            
            # Calculate country bounds
            lats = []
            lons = []
            for feature in gj['features']:
                if feature['geometry']['type'] == 'Polygon':
                    for coord in feature['geometry']['coordinates'][0]:
                        lons.append(coord[0])
                        lats.append(coord[1])
                elif feature['geometry']['type'] == 'MultiPolygon':
                    for polygon in feature['geometry']['coordinates']:
                        for coord in polygon[0]:
                            lons.append(coord[0])
                            lats.append(coord[1])
            
            # Set geo layout to focus on country only
            if lats and lons:
                # Add some padding
                padding = 0.5  # reduced padding for tighter focus
                lat_min, lat_max = min(lats) - padding, max(lats) + padding
                lon_min, lon_max = min(lons) - padding, max(lons) + padding
                
                fig.update_geos(
                    visible=False,  # Hide the base map
                    showcoastlines=False,
                    showland=False,
                    showocean=False,
                    showcountries=False,
                    # Set bounds to focus on country
                    lataxis=dict(range=[lat_min, lat_max], showgrid=False),
                    lonaxis=dict(range=[lon_min, lon_max], showgrid=False),
                    showframe=False,
                    bgcolor='rgba(0,0,0,0)'  # Transparent background
                )
                
                # Add specific layout settings to restrict view
                fig.update_layout(
                    geo=dict(
                        scope=None,  # Remove default scope
                        projection_scale=1.2,  # Zoom in slightly
                    )
                )
                
            # Update insights with state/region level data - handle NaN values
            dff_clean = dff.dropna(subset=["AverageTemperature"])
            
            if len(dff_clean) > 0:
                state_avg = dff_clean["AverageTemperature"].mean()
                # Get the full row with min/max temperature
                coldest_idx = dff_clean["AverageTemperature"].idxmin()
                hottest_idx = dff_clean["AverageTemperature"].idxmax()
                coldest_state = dff_clean.loc[coldest_idx]
                hottest_state = dff_clean.loc[hottest_idx]
            else:
                # Handle empty dataset
                state_avg = float('nan')
                coldest_state = {"state_name": "No data", "AverageTemperature": float('nan')}
                hottest_state = {"state_name": "No data", "AverageTemperature": float('nan')}
            
            insights_html = html.Div([
                html.H5(f"Temperature Insights for {selected_country} ({selected_year})"),
                html.Ul([
                    html.Li([
                        html.Strong("Country Average Temperature: "),
                        f"{state_avg:.2f}°C" if not pd.isna(state_avg) else "No data"
                    ]),
                    html.Li([
                        html.Strong("Coldest Region: "),
                        f"{coldest_state['state_name']} ({coldest_state['AverageTemperature']:.2f}°C)"
                        if not pd.isna(coldest_state['AverageTemperature']) else "No data"
                    ]),
                    html.Li([
                        html.Strong("Hottest Region: "),
                        f"{hottest_state['state_name']} ({hottest_state['AverageTemperature']:.2f}°C)"
                        if not pd.isna(hottest_state['AverageTemperature']) else "No data"
                    ])
                ])
            ])
                        
        except Exception as e:
            fig = px.scatter(
                title=f"Error loading {selected_country}: {e}",
                template="plotly_white"
            )
    else:
        return no_update, {"display": "none"}, no_update, False

    fig.update_layout(
        margin={"r":30,"t":50,"l":30,"b":30},
        paper_bgcolor="white",
        plot_bgcolor="rgba(0,0,0,0)",
        title=dict(
            font=dict(size=20),
            x=0.5
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        coloraxis_colorbar=dict(title="Temp (°C)")
    )
    
    return fig, {"height":"600px", "display":"block"}, insights_html, True

# Fix missing dash import
import dash
