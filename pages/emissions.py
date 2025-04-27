from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Fix missing dash import
import dash
from dash.exceptions import PreventUpdate


# Load dataset
df = pd.read_csv("data/Historical_Emissions.csv")

# Keep only relevant columns: Country + yearly emissions (1990-2018)
year_columns = [str(year) for year in range(1990, 2019)]
df_filtered = df[["Country"] + year_columns]

# Convert year columns to numeric
df_filtered[year_columns] = df_filtered[year_columns].apply(pd.to_numeric, errors="coerce")

# Calculate total emissions and sort
df_filtered["Total Emissions"] = df_filtered[year_columns].sum(axis=1)
df_filtered = df_filtered.dropna(subset=["Total Emissions"])
df_filtered = df_filtered.sort_values(by="Total Emissions", ascending=False)

# Get top emitters for quick filter options
top_emitters = df_filtered.head(10)["Country"].tolist()

# Calculate global total emissions per year for trend analysis
yearly_totals = pd.DataFrame({
    "Year": [int(year) for year in year_columns],
    "Global Emissions": [df_filtered[year].sum() for year in year_columns]
})

# Layout with modern UI
layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H2("🏭 Global CO₂ Emissions Analysis", className="card-title text-danger"),
                    html.P(
                        "Explore carbon emission trends by country and region from 1990 to 2018.",
                        className="card-text"
                    )
                ]),
                className="mb-4 shadow border-0"
            ),
            width=12
        )
    ]),
    
    # Controls card
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        # Visualization type selector
                        dbc.Col([
                            html.Label("Visualization Type:", className="fw-bold mb-2"),
                            dbc.RadioItems(
                                id="emissions-viz-type",
                                options=[
                                    {"label": "Country Comparison", "value": "country"},
                                    {"label": "Time Series Trends", "value": "trend"},
                                    {"label": "Regional Analysis", "value": "region"}
                                ],
                                value="country",
                                inline=True,
                                className="mb-3"
                            )
                        ], width=6),
                        
                        # Country/Region selector
                        dbc.Col([
                            html.Label("Select Countries:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="emissions-country-selector",
                                options=[{"label": country, "value": country} for country in df_filtered["Country"]],
                                value=top_emitters[:5],  # Default to top 5 emitters
                                multi=True,
                                placeholder="Select countries to compare...",
                                className="mb-3"
                            ),
                            
                            # Quick filter buttons
                            html.Div([
                                dbc.Button("Top 10", id="top10-btn", color="primary", size="sm", className="me-2"),
                                dbc.Button("G7", id="g7-btn", color="secondary", size="sm", className="me-2"),
                                dbc.Button("BRICS", id="brics-btn", color="success", size="sm", className="me-2"),
                                dbc.Button("Clear", id="clear-countries-btn", color="danger", size="sm")
                            ], className="d-flex")
                        ], width=6)
                    ]),
                    
                    html.Hr(),
                    
                    dbc.Row([
                        # Year range selector
                        dbc.Col([
                            html.Label("Year Range:", className="fw-bold mb-2"),
                            dcc.RangeSlider(
                                id="emissions-year-range",
                                min=1990,
                                max=2018,
                                value=[1990, 2018],
                                marks={i: str(i) for i in range(1990, 2019, 5)},
                                step=1,
                                className="mb-3"
                            )
                        ], width=12),
                    ]),
                    
                    # Apply filters button
                    dbc.Row([
                        dbc.Col(
                            dbc.Button(
                                "Update Visualization",
                                id="update-emissions-btn",
                                color="primary",
                                className="w-100"
                            ),
                            width={"size": 4, "offset": 4}
                        )
                    ])
                ]),
                className="mb-4 shadow border-0"
            ),
            width=12
        )
    ]),
    
    # Main visualization
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4(id="emissions-chart-title", className="card-title text-center mb-4"),
                    dbc.Spinner(
                        dcc.Graph(
                            id="emissions-chart",
                            config={"responsive": True},
                            style={"height": "600px"}
                        ),
                        color="danger",
                        type="border"
                    )
                ]),
                className="mb-4 shadow border-0"
            ),
            width=12
        )
    ]),
    
    # Insights row
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Emissions Insights", className="card-title"),
                    html.Div(id="emissions-insights", className="mt-2")
                ]),
                className="shadow border-0"
            ),
            width=12
        )
    ]),
    
    # Store for country group presets
    dcc.Store(id="country-groups", data={
        "G7": ["United States", "United Kingdom", "Canada", "France", "Germany", "Italy", "Japan"],
        "BRICS": ["Brazil", "Russia", "India", "China", "South Africa"]
    })
    
], fluid=True, className="py-4 bg-light")


# Callbacks for interactive functionality
@callback(
    Output("emissions-country-selector", "value"),
    [
        Input("top10-btn", "n_clicks"),
        Input("g7-btn", "n_clicks"),
        Input("brics-btn", "n_clicks"),
        Input("clear-countries-btn", "n_clicks")
    ],
    [
        State("country-groups", "data")
    ],
    prevent_initial_call=True
)
def update_country_selection(top10_clicks, g7_clicks, brics_clicks, clear_clicks, country_groups):
    # Determine which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "top10-btn":
        return top_emitters
    elif button_id == "g7-btn":
        return country_groups["G7"]
    elif button_id == "brics-btn":
        return country_groups["BRICS"]
    elif button_id == "clear-countries-btn":
        return []
    
    return dash.no_update


@callback(
    [
        Output("emissions-chart", "figure"),
        Output("emissions-chart-title", "children"),
        Output("emissions-insights", "children")
    ],
    [
        Input("update-emissions-btn", "n_clicks")
    ],
    [
        State("emissions-viz-type", "value"),
        State("emissions-country-selector", "value"),
        State("emissions-year-range", "value")
    ],
    prevent_initial_call=False
)
def update_emissions_chart(n_clicks, viz_type, selected_countries, year_range):
    # Filter for selected years
    start_year, end_year = year_range
    
    if viz_type == "country":
        # Country comparison visualization
        if not selected_countries:
            # If no countries selected, show top 10
            selected_countries = top_emitters
        
        # Create dataframe for selected countries
        countries_df = df_filtered[df_filtered["Country"].isin(selected_countries)].copy()
        
        # Calculate total emissions within selected year range
        year_cols = [str(y) for y in range(start_year, end_year + 1)]
        countries_df["Selected Range Emissions"] = countries_df[year_cols].sum(axis=1)
        countries_df = countries_df.sort_values("Selected Range Emissions", ascending=True)
        
        # Create horizontal bar chart
        fig = px.bar(
            countries_df,
            y="Country",
            x="Selected Range Emissions",
            color="Selected Range Emissions",
            color_continuous_scale="Reds",
            title=f"CO₂ Emissions by Country ({start_year}-{end_year})",
            template="plotly_white",
            orientation="h"
        )
        
        fig.update_layout(
            yaxis=dict(title=""),
            xaxis=dict(title="Total CO₂ Emissions"),
            coloraxis_showscale=False
        )
        
        title = f"Country Emissions Comparison ({start_year}-{end_year})"
        
        # Generate insights
        highest_country = countries_df.iloc[-1]["Country"]
        highest_value = countries_df.iloc[-1]["Selected Range Emissions"]
        lowest_country = countries_df.iloc[0]["Country"]
        lowest_value = countries_df.iloc[0]["Selected Range Emissions"]
        
        insights = html.Div([
            dbc.Alert([
                html.H5("Key Findings"),
                html.Ul([
                    html.Li([
                        f"Highest emissions: ",
                        html.Strong(f"{highest_country} ({highest_value:,.0f} units)")
                    ]),
                    html.Li([
                        f"Lowest emissions: ",
                        html.Strong(f"{lowest_country} ({lowest_value:,.0f} units)")
                    ]),
                    html.Li([
                        f"Difference between highest and lowest: ",
                        html.Strong(f"{(highest_value - lowest_value):,.0f} units"),
                        f" ({(highest_value / lowest_value):.1f}x higher)"
                    ])
                ])
            ], color="danger")
        ])
        
    elif viz_type == "trend":
        # Time series trend visualization
        fig = go.Figure()
        
        if not selected_countries:
            # If no countries selected, show global trend
            fig.add_trace(go.Scatter(
                x=yearly_totals["Year"],
                y=yearly_totals["Global Emissions"],
                mode="lines+markers",
                name="Global Total",
                line=dict(width=4, color="#dc3545")
            ))
            
            # Add trendline
            x = yearly_totals["Year"]
            y = yearly_totals["Global Emissions"]
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=x,
                y=p(x),
                mode="lines",
                name="Trend",
                line=dict(dash="dash", color="#000000")
            ))
            
            title = "Global Emissions Trend (1990-2018)"
            
            # Global insights
            start_emissions = yearly_totals[yearly_totals["Year"] == start_year]["Global Emissions"].values[0]
            end_emissions = yearly_totals[yearly_totals["Year"] == end_year]["Global Emissions"].values[0]
            change = end_emissions - start_emissions
            pct_change = (change / start_emissions) * 100
            
            insights = html.Div([
                dbc.Alert([
                    html.H5("Global Trend Insights"),
                    html.Ul([
                        html.Li([
                            f"From {start_year} to {end_year}, global emissions ",
                            html.Strong(f"{'increased' if change > 0 else 'decreased'} by {abs(change):,.0f} units"),
                            f" ({abs(pct_change):.1f}%)"
                        ]),
                        html.Li([
                            f"Average annual change: ",
                            html.Strong(f"{change / (end_year - start_year):,.1f} units per year")
                        ])
                    ]),
                    html.P([
                        "The overall trend is ",
                        html.Strong(f"{'upward' if z[0] > 0 else 'downward'}"),
                        " with varying rates of change across the time period."
                    ])
                ], color="info")
            ])
            
        else:
            # Show trends for selected countries
            for country in selected_countries:
                country_data = df_filtered[df_filtered["Country"] == country]
                
                if country_data.empty:
                    continue
                    
                years = []
                emissions = []
                
                for year in range(start_year, end_year + 1):
                    years.append(year)
                    emissions.append(country_data[str(year)].values[0])
                
                fig.add_trace(go.Scatter(
                    x=years,
                    y=emissions,
                    mode="lines+markers",
                    name=country
                ))
            
            title = f"Emissions Trends ({start_year}-{end_year})"
            
            # Multi-country insights
            country_changes = []
            
            for country in selected_countries:
                country_data = df_filtered[df_filtered["Country"] == country]
                
                if country_data.empty:
                    continue
                    
                start_val = country_data[str(start_year)].values[0]
                end_val = country_data[str(end_year)].values[0]
                
                if pd.isna(start_val) or pd.isna(end_val):
                    continue
                
                change = end_val - start_val
                pct_change = (change / start_val) * 100 if start_val != 0 else float('inf')
                
                country_changes.append({
                    "country": country,
                    "change": change,
                    "pct_change": pct_change
                })
            
            # Sort by percentage change
            country_changes.sort(key=lambda x: x["pct_change"])
            
            insights_items = []
            for i, data in enumerate(country_changes):
                if i == 0:  # Lowest increase/highest decrease
                    insights_items.append(html.Li([
                        f"Lowest growth: ",
                        html.Strong(f"{data['country']} ({data['pct_change']:+.1f}%)")
                    ]))
                elif i == len(country_changes) - 1:  # Highest increase
                    insights_items.append(html.Li([
                        f"Highest growth: ",
                        html.Strong(f"{data['country']} ({data['pct_change']:+.1f}%)")
                    ]))
            
            insights = html.Div([
                dbc.Alert([
                    html.H5("Trend Comparison Insights"),
                    html.Ul(insights_items)
                ], color="warning")
            ])
            
    else:  # Regional analysis
        # Group countries by continent/region (simplified)
        regions = {
            "North America": ["United States", "Canada", "Mexico"],
            "Europe": ["Germany", "United Kingdom", "France", "Italy", "Spain", "Poland", "Netherlands", "Belgium", "Sweden", "Austria", "Switzerland"],
            "Asia": ["China", "Japan", "India", "South Korea", "Indonesia", "Saudi Arabia", "Iran", "Thailand", "Malaysia"],
            "South America": ["Brazil", "Argentina", "Colombia", "Venezuela", "Chile", "Peru"],
            "Africa": ["South Africa", "Egypt", "Nigeria", "Algeria", "Morocco"],
            "Oceania": ["Australia", "New Zealand"]
        }
        
        # Prepare data
        regional_data = []
        
        for region, countries in regions.items():
            region_countries = df_filtered[df_filtered["Country"].isin(countries)]
            
            if region_countries.empty:
                continue
                
            for year in range(start_year, end_year + 1):
                year_total = region_countries[str(year)].sum()
                regional_data.append({
                    "Region": region,
                    "Year": year,
                    "Emissions": year_total
                })
        
        regional_df = pd.DataFrame(regional_data)
        
        # Create area chart
        fig = px.area(
            regional_df,
            x="Year",
            y="Emissions",
            color="Region",
            title=f"Regional CO₂ Emissions ({start_year}-{end_year})",
            template="plotly_white"
        )
        
        title = f"Regional Emissions Analysis ({start_year}-{end_year})"
        
        # Regional insights
        latest_year_data = regional_df[regional_df["Year"] == end_year]
        region_totals = latest_year_data.groupby("Region")["Emissions"].sum().reset_index()
        region_totals = region_totals.sort_values("Emissions", ascending=False)
        
        top_region = region_totals.iloc[0]["Region"]
        top_emissions = region_totals.iloc[0]["Emissions"]
        
        # Calculate region with highest growth
        region_growth = []
        for region in region_totals["Region"]:
            region_data = regional_df[regional_df["Region"] == region]
            start_val = region_data[region_data["Year"] == start_year]["Emissions"].values[0]
            end_val = region_data[region_data["Year"] == end_year]["Emissions"].values[0]
            growth = (end_val - start_val) / start_val * 100
            region_growth.append({"Region": region, "Growth": growth})
        
        growth_df = pd.DataFrame(region_growth)
        fastest_growth_region = growth_df.loc[growth_df["Growth"].idxmax()]["Region"]
        fastest_growth = growth_df.loc[growth_df["Growth"].idxmax()]["Growth"]
        
        insights = html.Div([
            dbc.Alert([
                html.H5("Regional Analysis Insights"),
                html.Ul([
                    html.Li([
                        f"Highest emitting region in {end_year}: ",
                        html.Strong(f"{top_region} ({top_emissions:,.0f} units)")
                    ]),
                    html.Li([
                        f"Region with fastest emissions growth: ",
                        html.Strong(f"{fastest_growth_region} (+{fastest_growth:.1f}%)")
                    ])
                ])
            ], color="primary")
        ])
    
    # Update common layout settings
    fig.update_layout(
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="white",
        plot_bgcolor="rgba(0,0,0,0.02)",
        height=600,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig, title, insights


